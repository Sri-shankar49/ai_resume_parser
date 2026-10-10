from fastapi import APIRouter, HTTPException

from src.models.resume_model import (
    ResumeListResponse,
    ResumeRecord,
    ResumeDeleteResponse,
)
from src.services.resume_repository import (
    get_resume,
    list_resumes,
    delete_resume,
)
from src.services.resume_vector_service import delete_resume_vector


router = APIRouter(
    prefix="/api/resumes",
    tags=["Resume Management"],
)


@router.get("", response_model=ResumeListResponse)
def get_all_resumes():
    resumes = list_resumes()

    return {
        "count": len(resumes),
        "resumes": resumes,
    }


@router.get("/{resume_id}", response_model=ResumeRecord)
def get_resume_by_id(resume_id: str):
    resume = get_resume(resume_id)

    if not resume:
        raise HTTPException(
            status_code=404,
            detail="Resume not found.",
        )

    return resume


@router.delete(
    "/{resume_id}",
    response_model=ResumeDeleteResponse,
)
def remove_resume(resume_id: str):
    resume = get_resume(resume_id)

    if not resume:
        raise HTTPException(
            status_code=404,
            detail="Resume not found.",
        )

    try:
        # Remove the vector first. If this fails, retain the
        # authoritative SQLite record so deletion can be retried.
        delete_resume_vector(resume_id)
        delete_resume(resume_id)

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unable to delete the resume. Please retry.",
        )

    return {
        "resume_id": resume_id,
        "message": "Resume deleted successfully.",
    }
