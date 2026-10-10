from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.services.resume_vector_service import search_resumes


router = APIRouter(
    prefix="/api/resumes",
    tags=["Resume Search"],
)


class ResumeSearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=1000)
    top_k: int = Field(default=5, ge=1, le=20)


@router.post("/search")
def search_resume_endpoint(request: ResumeSearchRequest):
    try:
        matches = search_resumes(
            query=request.query,
            top_k=request.top_k,
        )

        return {
            "query": request.query,
            "count": len(matches),
            "results": matches,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Resume search failed.",
        )
