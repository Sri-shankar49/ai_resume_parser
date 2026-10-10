
import pymupdf


def extract_text_from_pdf(pdf_bytes: bytes) -> tuple[int, str]:
    """
    Extract selectable text from a PDF.

    Returns:
        A tuple containing the page count and extracted text.
    """
    with pymupdf.open(
        stream=pdf_bytes,
        filetype="pdf"
    ) as document:
        if document.needs_pass:
            raise ValueError(
                "Password-protected PDFs are not supported."
            )

        pages = len(document)

        extracted_text = "\n".join(
            page.get_text() for page in document
        ).strip()

        return pages, extracted_text
