from urllib.parse import urlparse

import httpx
from fastapi import APIRouter, File, Form, HTTPException, UploadFile, Body
from pydantic import BaseModel

from services.ai_service import (
    extract_resume_from_text,
    polish_resume_text,
    chat_edit_resume,
    extract_resume_from_image,
)
from services.ocr_service import extract_text_from_pdf

router = APIRouter(prefix="/api/ai", tags=["ai"])


def _to_models_url(url: str) -> str:
    parsed = urlparse(url)
    path = parsed.path.rstrip("/")
    path = path.removesuffix("/chat/completions")
    if not path:
        path = "/v1"
    return f"{parsed.scheme}://{parsed.netloc}{path}/models"


class AiSettingsBody(BaseModel):
    baseUrl: str | None = None
    apiKey: str | None = None
    model: str | None = None


class PolishBody(BaseModel):
    field: str
    html: str
    context: dict | None = None
    aiSettings: AiSettingsBody | None = None


class ChatEditBody(BaseModel):
    message: str
    resume: dict
    aiSettings: AiSettingsBody | None = None


class RecognizeImageBody(BaseModel):
    image: str
    mimeType: str
    aiSettings: AiSettingsBody | None = None


@router.post("/models")
async def list_models(settings: AiSettingsBody = Body(...)):
    api_key = (settings.apiKey or "").strip()
    base_url = (settings.baseUrl or "").strip()
    if not api_key:
        raise HTTPException(status_code=400, detail="请先配置 API Key")

    url = _to_models_url(base_url or "https://api.openai.com/v1/chat/completions")
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(url, headers={"x-api-key": f"{api_key}"})
        if resp.status_code >= 400:
            raise HTTPException(status_code=502, detail=f"获取模型失败：{resp.status_code} {resp.text}")
        data = resp.json()
        models = [m["id"] for m in data.get("data", []) if m.get("id")]
        return {"models": sorted(models)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/recognize-pdf")
async def recognize_pdf(
    file: UploadFile = File(...),
    api_key: str = Form(...),
    base_url: str | None = Form(None),
    model: str | None = Form(None),
):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="仅支持 PDF 文件")

    try:
        pdf_bytes = await file.read()
        text = extract_text_from_pdf(pdf_bytes)
        if not text.strip():
            raise HTTPException(status_code=400, detail="未能从 PDF 中提取到文字内容")

        resume = await extract_resume_from_text(
            text=text,
            api_key=api_key.strip(),
            base_url=base_url.strip() if base_url else None,
            model=model.strip() if model else None,
        )
        return {"resume": resume}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/polish")
async def polish(body: PolishBody = Body(...)):
    settings = body.aiSettings or AiSettingsBody()
    api_key = (settings.apiKey or "").strip()
    base_url = (settings.baseUrl or "").strip()
    model = (settings.model or "").strip()
    if not api_key:
        raise HTTPException(status_code=400, detail="请先配置 API Key")

    try:
        html = await polish_resume_text(
            field=body.field,
            html=body.html,
            api_key=api_key,
            base_url=base_url or None,
            model=model or None,
            context=body.context,
        )
        return {"html": html}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat-edit")
async def chat_edit(body: ChatEditBody = Body(...)):
    settings = body.aiSettings or AiSettingsBody()
    api_key = (settings.apiKey or "").strip()
    base_url = (settings.baseUrl or "").strip()
    model = (settings.model or "").strip()
    if not api_key:
        raise HTTPException(status_code=400, detail="请先配置 API Key")

    try:
        result = await chat_edit_resume(
            message=body.message,
            resume=body.resume,
            api_key=api_key,
            base_url=base_url or None,
            model=model or None,
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/recognize-image")
async def recognize_image(body: RecognizeImageBody = Body(...)):
    settings = body.aiSettings or AiSettingsBody()
    api_key = (settings.apiKey or "").strip()
    base_url = (settings.baseUrl or "").strip()
    model = (settings.model or "").strip()
    if not api_key:
        raise HTTPException(status_code=400, detail="请先配置 API Key")

    try:
        resume = await extract_resume_from_image(
            image=body.image,
            mime_type=body.mimeType,
            api_key=api_key,
            base_url=base_url or None,
            model=model or None,
        )
        return {"resume": resume}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
