from playwright.async_api import async_playwright

from .template_service import render_resume_html


async def create_resume_pdf(resume: dict, template_id: str) -> bytes:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        try:
            page = await browser.new_page()
            html = render_resume_html(resume, template_id)
            await page.set_content(html, wait_until="load")
            await page.evaluate("document.fonts.ready")

            pdf_bytes = await page.pdf(
                format="A4",
                print_background=True,
                margin={"top": "0mm", "right": "0mm", "bottom": "0mm", "left": "0mm"},
            )
            return pdf_bytes
        finally:
            await browser.close()
