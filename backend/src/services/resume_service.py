import uuid

from src.services.resume_repository import (
    calculate_file_hash,
    create_resume,
    get_resume_by_hash,
)

from src.utils.pdf_utils import extract_text_from_pdf
from src.services.resume_ai_service import parse_resume_with_ai
from src.services.resume_vector_service import store_resume
from fastapi import HTTPException, UploadFile



MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


def process_resume(filename: str, pdf_bytes: bytes) -> dict:
    """
    Validate the uploaded PDF and extract its text.
    """

    if not filename.lower().endswith(".pdf"):
        raise ValueError("Please upload a PDF file.")

    if not pdf_bytes:
        raise ValueError("The uploaded file is empty.")

    if len(pdf_bytes) > MAX_FILE_SIZE:
        raise ValueError("The PDF must be 10 MB or smaller.")

    if not pdf_bytes.startswith(b"%PDF-"):
        raise ValueError("The uploaded file is not a valid PDF.")

    try:
        pages, extracted_text = extract_text_from_pdf(pdf_bytes)
    except ValueError:
        raise
    except Exception as exc:
        raise ValueError(
            "Unable to read this PDF. Please try another file."
        ) from exc

    if not extracted_text:
        message = (
            "No selectable text found. "
            "This PDF may require OCR."
        )
    else:
        message = "Resume text extracted successfully."

    return {
        "filename": filename,
        "pages": pages,
        "extracted_text": extracted_text,
        "message": message,
    }
    
    
# async def parse_resume(
#     filename: str,
#     pdf_bytes: bytes
# ) -> dict:
#     # Reuse the PDF extraction logic we already built.
#     extracted = process_resume(
#         filename=filename,
#         pdf_bytes=pdf_bytes
#     )

#     if not extracted["extracted_text"]:
#         raise ValueError(
#             "No selectable text found. This PDF may require OCR."
#         )

#     # Ask Groq to structure the extracted information.
#     parsed_resume = await parse_resume_with_ai(
#         extracted["extracted_text"]
#     )
    
#     resume_data = parsed_resume.model_dump()

#     # Store the parsed resume in ChromaDB for future semantic search.
#     resume_id = store_resume(
#         filename=filename,
#         resume=resume_data,
#     )

#     return {
#         "resume_id": resume_id,
#         "filename": filename,
#         "parsed_resume": parsed_resume.model_dump(),
#         "message": "Resume parsed successfully."
#     }


async def parse_resume(
    filename: str,
    pdf_bytes: bytes,
) -> dict:
    # Validate the PDF and extract its text.
    extracted = process_resume(
        filename=filename,
        pdf_bytes=pdf_bytes,
    )

    file_hash = calculate_file_hash(pdf_bytes)

    # Return the existing record instead of parsing the same
    # exact PDF again.
    existing = get_resume_by_hash(file_hash)

    if existing:
        return {
            "resume_id": existing["resume_id"],
            "filename": existing["filename"],
            "parsed_resume": existing["parsed_resume"],
            "message": "This resume has already been uploaded.",
            "duplicate": True,
        }

    if not extracted["extracted_text"]:
        raise ValueError(
            "No selectable text found. This PDF may require OCR."
        )

    # Ask Groq to parse the resume.
    parsed = await parse_resume_with_ai(
        extracted["extracted_text"]
    )

    resume_data = parsed.model_dump()
    resume_id = str(uuid.uuid4())

    # Persist the structured profile first.
    record = create_resume(
        resume_id=resume_id,
        filename=filename,
        file_hash=file_hash,
        parsed_resume=resume_data,
    )

    # Then create its semantic-search vector.
    try:
        store_resume(
            filename=filename,
            resume=resume_data,
            resume_id=resume_id,
        )
    except Exception:
        # Avoid leaving an incomplete record if vector storage fails.
        from src.services.resume_repository import delete_resume

        delete_resume(resume_id)
        raise

    return {
        "resume_id": record["resume_id"],
        "filename": record["filename"],
        "parsed_resume": record["parsed_resume"],
        "message": "Resume parsed and stored successfully.",
        "duplicate": False,
    }


async def read_pdf_upload(file: UploadFile) -> bytes:
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Please upload a PDF file.",
        )

    content = await file.read(MAX_FILE_SIZE + 1)

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="The PDF exceeds the 10 MB upload limit.",
        )

    if not content:
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is empty.",
        )

    if not content.startswith(b"%PDF-"):
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is not a valid PDF.",
        )

    return content
