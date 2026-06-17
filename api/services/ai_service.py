import json
import re
from urllib.parse import urlparse

import httpx


RESUME_EXTRACTION_SYSTEM_PROMPT = """你是简历 OCR 和结构化信息抽取助手。
你的任务是从纯文本简历内容中提取结构化信息，只返回严格 JSON，不要 Markdown 包装，不要解释。
字段缺失用空字符串或空数组。
富文本字段请返回安全 HTML，可用 p、ol、ul、li、strong 标签。"""

RESUME_EXTRACTION_USER_TEMPLATE = """请从以下简历文本中提取信息，并按要求的 JSON 结构返回：

简历文本：
{text}

请严格按以下 JSON 结构返回，不要添加额外字段：
{{
  "profile": {{ "name":"", "headline":"", "phone":"", "email":"", "city":"", "gender":"", "age":"", "workYears":"", "expectedSalary":"", "expectedCity":"", "summary":"" }},
  "workExperience": [{{ "company":"", "position":"", "city":"", "startDate":"YYYY-MM", "endDate":"YYYY-MM", "isCurrent": false, "summary":"<ol><li>...</li></ol>" }}],
  "projects": [{{ "name":"", "role":"", "startDate":"YYYY-MM", "endDate":"YYYY-MM", "description":"", "techStack": [], "responsibilitiesText":"<ol><li>...</li></ol>", "achievementsText":"<ol><li>...</li></ol>" }}],
  "education": [{{ "school":"", "degree":"", "major":"", "startDate":"YYYY-MM", "endDate":"YYYY-MM", "description": [] }}],
  "skills": [{{ "category":"", "items": [{{ "name":"", "level":"" }}] }}]
}}"""

POLISH_SYSTEM_PROMPT = """你是资深招聘顾问。请润色简历内容，要求表达专业、具体、结果导向。
只返回安全的 HTML 片段，可使用 p、ol、ul、li、strong 标签，不要返回 Markdown，不要编造离谱数据。"""

CHAT_EDIT_SYSTEM_PROMPT = """你是在线简历编辑助手。用户会用自然语言要求修改简历。
请基于当前简历只返回严格 JSON，不要 Markdown，不要解释。
返回结构：{{ "reply": "修改说明（说明具体修改了什么，如：将工作经历1的公司名改为字节跳动，将项目1的技术栈改为React、Vue）", "resume": PartialResume }}。
PartialResume 只包含需要修改的字段。
富文本字段返回安全 HTML，可用 p、ol、ul、li、strong 标签。
不要删除用户没有要求删除的内容。"""

IMAGE_EXTRACTION_SYSTEM_PROMPT = """你是简历 OCR 和结构化信息抽取助手。
请从图片中识别简历内容，并只返回严格 JSON，不要 Markdown，不要解释。
字段缺失用空字符串或空数组。
富文本字段请返回安全 HTML，可用 p、ol、ul、li、strong 标签。"""

IMAGE_EXTRACTION_USER_TEMPLATE = """请按以下 JSON 结构返回识别结果：
{{
  "profile": {{ "name":"", "headline":"", "phone":"", "email":"", "city":"", "gender":"", "age":"", "workYears":"", "expectedSalary":"", "expectedCity":"", "summary":"" }},
  "workExperience": [{{ "company":"", "position":"", "city":"", "startDate":"YYYY-MM", "endDate":"YYYY-MM", "isCurrent": false, "summary":"<ol><li>...</li></ol>" }}],
  "projects": [{{ "name":"", "role":"", "startDate":"YYYY-MM", "endDate":"YYYY-MM", "description":"", "techStack": [], "responsibilitiesText":"<ol><li>...</li></ol>", "achievementsText":"<ol><li>...</li></ol>" }}],
  "education": [{{ "school":"", "degree":"", "major":"", "startDate":"YYYY-MM", "endDate":"YYYY-MM", "description": [] }}],
  "skills": [{{ "category":"", "items": [{{ "name":"", "level":"" }}] }}]
}}"""


def _to_chat_completions_url(url: str) -> str:
    """兼容前端传完整接口地址或只传 base URL。"""
    if not url:
        return "https://api.openai.com/v1/chat/completions"

    parsed = urlparse(url)
    path = parsed.path.rstrip("/")
    if path.endswith("/chat/completions"):
        return f"{parsed.scheme}://{parsed.netloc}{path}"
    return f"{parsed.scheme}://{parsed.netloc}{path}/chat/completions"


def _parse_json_content(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
        return {}


async def extract_resume_from_text(
    text: str,
    api_key: str,
    base_url: str | None = None,
    model: str | None = None,
) -> dict:
    url = _to_chat_completions_url(base_url or "")
    async with httpx.AsyncClient(timeout=120) as client:
        response = await client.post(
            url,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
            json={
                "model": model or "gpt-4o-mini",
                "temperature": 0.1,
                "messages": [
                    {"role": "system", "content": RESUME_EXTRACTION_SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": RESUME_EXTRACTION_USER_TEMPLATE.format(text=text),
                    },
                ],
            },
        )

    if response.status_code >= 400:
        raise RuntimeError(f"OpenAI 接口请求失败：{response.status_code} {response.text}")

    data = response.json()
    content = data.get("choices", [{}])[0].get("message", {}).get("content") or "{}"
    return _parse_json_content(content)


async def _call_chat_completion(
    messages: list[dict],
    api_key: str,
    base_url: str | None = None,
    model: str | None = None,
    temperature: float = 0.1,
) -> str:
    url = _to_chat_completions_url(base_url or "")
    async with httpx.AsyncClient(timeout=120) as client:
        response = await client.post(
            url,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
            json={"model": model or "gpt-4o-mini", "temperature": temperature, "messages": messages},
        )
    if response.status_code >= 400:
        raise RuntimeError(f"AI 接口请求失败：{response.status_code} {response.text}")
    data = response.json()
    return data.get("choices", [{}])[0].get("message", {}).get("content") or ""


async def polish_resume_text(
    field: str,
    html: str,
    api_key: str,
    base_url: str | None = None,
    model: str | None = None,
    context: dict | None = None,
) -> str:
    user_content = f"字段：{field}\n"
    if context:
        user_content += f"上下文：{json.dumps(context, ensure_ascii=False)}\n"
    user_content += f"原文 HTML：{html}"

    content = await _call_chat_completion(
        messages=[
            {"role": "system", "content": POLISH_SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
        api_key=api_key,
        base_url=base_url,
        model=model,
        temperature=0.4,
    )
    return content.rstrip("`").strip() if content else html


async def chat_edit_resume(
    message: str,
    resume: dict,
    api_key: str,
    base_url: str | None = None,
    model: str | None = None,
) -> dict:
    user_content = f"用户要求：{message}\n当前简历 JSON：{json.dumps(resume, ensure_ascii=False)}"

    content = await _call_chat_completion(
        messages=[
            {"role": "system", "content": CHAT_EDIT_SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
        api_key=api_key,
        base_url=base_url,
        model=model,
        temperature=0.2,
    )
    parsed = _parse_json_content(content)
    return {
        "reply": parsed.get("reply", "已根据你的要求修改简历。"),
        "resume": parsed.get("resume", {}),
    }


async def extract_resume_from_image(
    image: str,
    mime_type: str,
    api_key: str,
    base_url: str | None = None,
    model: str | None = None,
) -> dict:
    content = await _call_chat_completion(
        messages=[
            {"role": "system", "content": IMAGE_EXTRACTION_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": IMAGE_EXTRACTION_USER_TEMPLATE},
                    {"type": "image_url", "image_url": {"url": image}},
                ],
            },
        ],
        api_key=api_key,
        base_url=base_url,
        model=model or "gpt-4o-mini",
        temperature=0.1,
    )
    return _parse_json_content(content)
