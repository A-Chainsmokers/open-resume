import json
import pathlib
import re

_TEMPLATE_DIR = pathlib.Path(__file__).parent / "templates"
TEMPLATE_DEFS: dict[str, dict] = {}
for _f in sorted(_TEMPLATE_DIR.glob("*.json")):
    with open(_f, encoding="utf-8") as _fh:
        _d = json.load(_fh)
        TEMPLATE_DEFS[_d["id"]] = _d

CSS = """\
@page { size: A4; margin: 22mm 14mm; }
* { box-sizing: border-box; }
body { margin: 0; color: #343a40; font-family: "Microsoft YaHei","Noto Sans SC",SimSun,sans-serif; font-size: 13.4px; line-height: 1.85; }
h1,h2,h3,p { margin-top: 0; }
section { margin-top: 22px; }
h2 { color: #050505; font-size: 21px; border-bottom: 1px solid #c9c9c9; padding-bottom: 5px; margin-bottom: 10px; line-height: 1.25; font-weight: 900; letter-spacing: 0; }
.resume-head { min-height: 36mm; text-align: center; margin-bottom: 12px; overflow: hidden; }
.resume-head h1 { margin: 0 0 12px; color: #050505; font-size: 25px; font-weight: 900; letter-spacing: .08em; }
.contact { margin: 2px 0; color: #3f454b; font-size: 13px; font-weight: 600; }
.avatar { float: right; width: 26mm; height: 32mm; object-fit: cover; border-radius: 3px; margin-left: 28mm; }
.item { margin-bottom: 18px; }
.item-title { display: grid; grid-template-columns: minmax(0,1.25fr) minmax(70px,.55fr) auto; gap: 18px; color: #333b42; align-items: baseline; }
.edu-title { grid-template-columns: minmax(0,1fr) 64px minmax(120px,.7fr) auto; }
.item-title strong { color: #252b31; font-size: 16px; font-weight: 900; }
.item-title span { color: #343a40; font-size: 14px; }
.item-title time { justify-self: end; color: #666d73; font-size: 13px; white-space: nowrap; }
p { margin: 4px 0; }
ul { list-style: none; margin: 4px 0 0; padding: 0; }
li { margin: 2px 0; }
.label-line { margin-top: 8px; color: #222; font-weight: 800; }
.rich-output p { margin: 2px 0; }
.rich-output ol,.rich-output ul { margin: 4px 0 0 20px; padding: 0; list-style-position: outside; }
.rich-output ul { list-style: disc; }
.rich-output ol { list-style: decimal; }
.modern { border-left: 18mm solid #0e3832; }
.modern h2 { color: #0e3832; text-transform: uppercase; }
.minimal h2 { color: #111; border: 0; font-size: 13px; text-transform: uppercase; letter-spacing: .2em; }
"""

DEFAULT_SECTION_ORDER = ["profile", "workExperience", "projects", "education", "skills"]


def escape_html(value) -> str:
    s = str(value) if value is not None else ""
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;").replace("'", "&#39;")


def sanitize_rich_text(value) -> str:
    s = str(value) if value is not None else ""
    s = re.sub(r"<script[\s\S]*?>[\s\S]*?</script>", "", s, flags=re.IGNORECASE)
    s = re.sub(r'\son\w+="[^"]*"', "", s, flags=re.IGNORECASE)
    s = re.sub(r"\son\w+='[^']*'", "", s, flags=re.IGNORECASE)
    s = re.sub(r"javascript:", "", s, flags=re.IGNORECASE)
    return s


def _section_order(resume: dict) -> list[str]:
    user_order = resume.get("settings", {}).get("sectionOrder")
    return list(user_order) if isinstance(user_order, list) else DEFAULT_SECTION_ORDER


# ── Section renderers ──────────────────────────────────────────

def _render_profile(resume: dict, def_: dict) -> str:
    summary = resume.get("profile", {}).get("summary")
    if not summary:
        return ""
    label = def_.get("labels", {}).get("profile", "个人优势")
    output = def_.get("profileOutput", "rich")
    if output == "rich":
        return f'<section><h2>{escape_html(label)}</h2><div class="rich-output">{sanitize_rich_text(summary)}</div></section>'
    return f"<section><h2>{escape_html(label)}</h2><p>{escape_html(summary)}</p></section>"


def _render_work(resume: dict, def_: dict) -> str:
    items = resume.get("workExperience") or []
    if not items:
        return ""
    label = def_.get("labels", {}).get("workExperience", "工作经历")
    current_text = def_.get("currentText", "至今")
    output = def_.get("workOutput", "rich")
    layout = def_.get("layout", "center")

    parts = []
    for w in items:
        company = escape_html(w.get("company", ""))
        position = escape_html(w.get("position", ""))
        start = escape_html(w.get("startDate", ""))
        end = current_text if w.get("isCurrent") else escape_html(w.get("endDate", ""))

        if layout in ("compact", "sidebar"):
            title_strong = f"{escape_html(position)}, {escape_html(company)}" if layout == "compact" else f"{escape_html(company)} &middot; {escape_html(position)}"
            title_html = f"<strong>{title_strong}</strong><span>{start}-{end}</span>"
        else:
            title_html = f"<strong>{company}</strong><span>{position}</span><time>{start}-{end}</time>"

        body = ""
        if output == "rich" and w.get("summary"):
            body = f'<div class="rich-output">{sanitize_rich_text(w["summary"])}</div>'
        elif output == "highlights":
            hl = w.get("highlights") or []
            if hl:
                body = "<ul>" + "".join(f"<li>{escape_html(h)}</li>" for h in hl) + "</ul>"

        parts.append(f'<div class="item"><div class="item-title">{title_html}</div>{body}</div>')

    return f"<section><h2>{escape_html(label)}</h2>{''.join(parts)}</section>"


def _render_projects(resume: dict, def_: dict) -> str:
    items = resume.get("projects") or []
    if not items:
        return ""
    label = def_.get("labels", {}).get("projects", "项目经历")
    output = def_.get("projectsOutput", "rich")
    layout = def_.get("layout", "center")

    parts = []
    for p in items:
        name = escape_html(p.get("name", ""))
        role = escape_html(p.get("role", ""))
        start = escape_html(p.get("startDate", ""))
        end = escape_html(p.get("endDate", ""))
        desc = escape_html(p.get("description", ""))

        if output == "compact":
            tech = ", ".join(escape_html(t) for t in (p.get("techStack") or []))
            title_html = f"<strong>{name}</strong><span>{tech}</span>"
            body = f"<p>{desc}</p>"
            title_grid = ""  # no outer item-title grid for compact
        else:
            if layout == "sidebar":
                title_html = f"<strong>{name} &middot; {role}</strong><span>{start}-{end}</span>"
            else:
                title_html = f"<strong>{name}</strong><span>{role}</span><time>{start}-{end}</time>"
            body = f"<p>{desc}</p>" if desc else ""
            if p.get("techStack"):
                joiner = "、" if layout == "center" else ", "
                body += f'<p>技术栈：{joiner.join(escape_html(t) for t in p["techStack"])}</p>'

            if output == "rich":
                if p.get("responsibilitiesText"):
                    body += f'<p class="label-line">职责：</p><div class="rich-output">{sanitize_rich_text(p["responsibilitiesText"])}</div>'
                if p.get("achievementsText"):
                    body += f'<p class="label-line">成果：</p><div class="rich-output">{sanitize_rich_text(p["achievementsText"])}</div>'
            elif output == "list":
                lines = []
                for l in (p.get("responsibilities") or []):
                    lines.append(escape_html(l))
                for l in (p.get("achievements") or []):
                    lines.append(escape_html(l))
                if lines:
                    body += "<ul>" + "".join(f"<li>{l}</li>" for l in lines) + "</ul>"

        parts.append(f'<div class="item"><div class="item-title">{title_html}</div>{body}</div>')

    return f"<section><h2>{escape_html(label)}</h2>{''.join(parts)}</section>"


def _render_education(resume: dict, def_: dict) -> str:
    items = resume.get("education") or []
    if not items:
        return ""
    label = def_.get("labels", {}).get("education", "教育经历")
    output = def_.get("educationOutput", "detailed")

    parts = []
    for e in items:
        school = escape_html(e.get("school", ""))
        degree = escape_html(e.get("degree", ""))
        major = escape_html(e.get("major", ""))
        start = escape_html(e.get("startDate", ""))
        end = escape_html(e.get("endDate", ""))

        if output == "detailed":
            desc = "".join(f"<li>{escape_html(d)}</li>" for d in (e.get("description") or []) if d)
            title_html = f"<strong>{school}</strong><span>{degree}</span><span>{major}</span><time>{start}-{end}</time>"
            body = f"<ul>{desc}</ul>" if desc else ""
            parts.append(f'<div class="item"><div class="item-title edu-title">{title_html}</div>{body}</div>')
        else:
            parts.append(f"<div class=\"item\"><p>{school} &middot; {major} &middot; {degree} / {start}-{end}</p></div>")

    return f"<section><h2>{escape_html(label)}</h2>{''.join(parts)}</section>"


def _render_skills(resume: dict, def_: dict) -> str:
    items = resume.get("skills") or []
    if not items:
        return ""
    label = def_.get("labels", {}).get("skills", "技能")
    output = def_.get("skillsOutput", "with-level")

    parts = []
    for g in items:
        cat = escape_html(g.get("category", ""))
        skill_items = g.get("items") or []
        if output == "with-level":
            texts = [f"{escape_html(s.get('name', ''))}({escape_html(s.get('level', ''))})" if s.get("level") else escape_html(s.get("name", "")) for s in skill_items]
            joiner = "、"
        else:
            texts = [escape_html(s.get("name", "")) for s in skill_items]
            joiner = ", "
        parts.append(f"<p><strong>{cat}：</strong>{joiner.join(texts)}</p>")

    return f"<section><h2>{escape_html(label)}</h2>{''.join(parts)}</section>"


# ── Layout renderers ───────────────────────────────────────────

def _sections_html(resume: dict, def_: dict) -> str:
    order = _section_order(resume)
    html = ""
    for sid in order:
        if sid == "profile":
            html += _render_profile(resume, def_)
        elif sid == "workExperience":
            html += _render_work(resume, def_)
        elif sid == "projects":
            html += _render_projects(resume, def_)
        elif sid == "education":
            html += _render_education(resume, def_)
        elif sid == "skills":
            html += _render_skills(resume, def_)
    return html


def _render_center(resume: dict, def_: dict) -> str:
    profile = resume.get("profile") or {}
    name = escape_html(profile.get("name", ""))
    gender = escape_html(profile.get("gender", ""))
    age = escape_html(profile.get("age", ""))
    email = escape_html(profile.get("email", ""))
    work_years = escape_html(profile.get("workYears", ""))
    headline = escape_html(profile.get("headline", ""))
    salary = escape_html(profile.get("expectedSalary", ""))
    city = escape_html(profile.get("expectedCity") or profile.get("city", ""))
    avatar = escape_html(profile.get("avatar", "")) if profile.get("avatar") else ""
    avatar_html = f'<img class="avatar" src="{avatar}" alt="头像" />' if avatar else ""

    sections = _sections_html(resume, def_)

    return f"""\
<article class="resume-page {def_["cssClass"]}">
  <header class="resume-head image-format-head">
    <div class="head-copy">
      <h1>{name}</h1>
      <p class="contact compact-contact">{gender} | 年龄：{age} | ✉ {email}</p>
      <p class="contact compact-contact">{work_years} | 求职意向：{headline} | 期望薪资：{salary} | 期望城市：{city}</p>
    </div>
    {avatar_html}
  </header>
  {sections}
</article>"""


def _render_sidebar(resume: dict, def_: dict) -> str:
    profile = resume.get("profile") or {}
    name = escape_html(profile.get("name", ""))
    headline = escape_html(profile.get("headline", ""))
    phone = escape_html(profile.get("phone", ""))
    email = escape_html(profile.get("email", ""))
    city = escape_html(profile.get("city", ""))

    # Sidebar skills
    skills_html = ""
    skills_groups = resume.get("skills") or []
    if skills_groups and "skills" in def_.get("sidebarSections", []):
        items = []
        for g in skills_groups:
            cat = escape_html(g.get("category", ""))
            names = " / ".join(escape_html(s.get("name", "")) for s in (g.get("items") or []))
            items.append(f"<em>{cat}</em><span>{names}</span>")
        if items:
            skills_html = f'<div class="side-block"><b>{escape_html(def_["labels"].get("skills", "Skills"))}</b>{"".join(items)}</div>'

    sections = _sections_html(resume, def_)

    return f"""\
<article class="resume-page {def_["cssClass"]}">
  <aside>
    <h1>{name}</h1>
    <p>{headline}</p>
    <div class="side-block">
      <b>联系方式</b>
      <span>{phone}</span>
      <span>{email}</span>
      <span>{city}</span>
    </div>
    {skills_html}
  </aside>
  <main>
    {sections}
  </main>
</article>"""


def _render_compact(resume: dict, def_: dict) -> str:
    profile = resume.get("profile") or {}
    name = escape_html(profile.get("name", ""))
    headline = escape_html(profile.get("headline", ""))
    phone = escape_html(profile.get("phone", ""))
    email = escape_html(profile.get("email", ""))
    city = escape_html(profile.get("city", ""))

    sections = _sections_html(resume, def_)

    return f"""\
<article class="resume-page {def_["cssClass"]}">
  <header>
    <h1>{name}</h1>
    <p>{headline} / {phone} / {email} / {city}</p>
  </header>
  {sections}
</article>"""


# ── Public entry point ─────────────────────────────────────────

def render_resume_html(resume: dict, template_id: str) -> str:
    def_ = TEMPLATE_DEFS.get(template_id, TEMPLATE_DEFS["classic"])

    layout = def_.get("layout", "center")
    if layout == "sidebar":
        body = _render_sidebar(resume, def_)
    elif layout == "compact":
        body = _render_compact(resume, def_)
    else:
        body = _render_center(resume, def_)

    return f"""<!doctype html><html lang="zh-CN"><head><meta charset="utf-8" /><style>{CSS}</style></head><body>{body}</body></html>"""
