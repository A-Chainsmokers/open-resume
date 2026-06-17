from urllib.parse import quote

from fastapi import APIRouter, HTTPException
from starlette.responses import Response
from schemas.pdf import ExportRequest

from services.pdf_service import create_resume_pdf

router = APIRouter(prefix="/api/pdf", tags=["pdf"])


@router.post("/export")
async def export_pdf(req: ExportRequest):
    try:
        pdf_bytes = await create_resume_pdf(req.resume, req.template_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    profile = req.resume.get("profile") or {}
    name = profile.get("name", "resume")
    headline = profile.get("headline", "简历")
    filename = f"{name}_{headline}.pdf"
    encoded = quote(filename)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{encoded}"},
    )
