
from fastapi import APIRouter, UploadFile, File, HTTPException

from src.models.resume_model import ResumeExtractionResponse, ResumeParseResponse
from src.services.resume_service import process_resume, parse_resume


router = APIRouter(
    prefix="/api/resumes",
    tags=["Resumes"]
)


@router.post("/extract",response_model=ResumeExtractionResponse)
async def extract_resume(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="A filename is required."
        )

    try:
        pdf_bytes = await file.read()

        result = process_resume(
            filename=file.filename,
            pdf_bytes=pdf_bytes
        )

        return result

    except ValueError as exc:
        message = str(exc)

        status_code = (
            413 if "10 MB" in message else 400
        )

        raise HTTPException(
            status_code=status_code,
            detail=message
        ) from exc

    finally:
        await file.close()
        
        


@router.post("/parse", response_model=ResumeParseResponse)
async def parse_resume_endpoint(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="A filename is required."
        )

    try:
        pdf_bytes = await file.read()

        result = await parse_resume(
            filename=file.filename,
            pdf_bytes=pdf_bytes
        )

        return result

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc)
        ) from exc

    except RuntimeError as exc:
        # Configuration problems, such as a missing API key.
        raise HTTPException(
            status_code=500,
            detail=str(exc)
        ) from exc

    except Exception as exc:
        # Log the detailed exception server-side in production.
        # Avoid exposing raw provider errors to public clients.
        raise HTTPException(
            status_code=502,
            detail="AI resume parsing failed. Please try again."
        ) from exc

    finally:
        await file.close()
        
