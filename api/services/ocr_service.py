import fitz


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    pages = []
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        pages.append(page.get_text())
    doc.close()
    return "\n".join(pages)
