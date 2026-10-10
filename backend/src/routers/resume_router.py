
from fastapi import APIRouter

from src.controllers.resume_controller import extract_resume, parse_resume_endpoint
from src.controllers.search_controller import search_resume_endpoint
from src.controllers.resume_management_controller import (
    get_all_resumes,
    get_resume_by_id,
    remove_resume,
)
from src.models.resume_model import ResumeExtractionResponse, ResumeParseResponse, ResumeListResponse, ResumeRecord, ResumeDeleteResponse


router = APIRouter(
    prefix="/api/resumes",
    tags=["Resumes"]
)

router.add_api_route(
    "/extract",
    extract_resume,
    methods=["POST"],
    response_model=ResumeExtractionResponse,
)

router.add_api_route(
    "/parse",
    parse_resume_endpoint,
    methods=["POST"],
    response_model=ResumeParseResponse,
)

router.add_api_route(
    "/search",
    search_resume_endpoint,
    methods=["POST"],
)

router.add_api_route(
    "",
    get_all_resumes,
    methods=["GET"],
    response_model=ResumeListResponse,
)

router.add_api_route(
    "/{resume_id}",
    get_resume_by_id,
    methods=["GET"],
    response_model=ResumeRecord,
)

router.add_api_route(
    "/{resume_id}",
    remove_resume,
    methods=["DELETE"],
    response_model=ResumeDeleteResponse,
)