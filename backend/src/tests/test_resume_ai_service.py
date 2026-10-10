
import json
from unittest.mock import AsyncMock
from types import SimpleNamespace


import pytest
from pydantic import ValidationError

from src.models.resume_model import ResumeData
from src.services.resume_ai_service import parse_resume_with_ai
from src.services import resume_ai_service

from fastapi.testclient import TestClient

from main import app
from src.controllers import resume_controller

VALID_RESUME = {
    "full_name": "Test Candidate",
    "email": "candidate@example.com",
    "phone": None,
    "location": "Chennai",
    "professional_summary": "Full-stack developer.",
    "technical_skills": ["Python", "React"],
    "soft_skills": ["Communication"],
    "work_experience": [],
    "education": [],
}


def make_fake_groq_client(content=None, error=None):
    if error is not None:
        mock_create = AsyncMock(side_effect=error)
    else:
        fake_response = SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(content=content)
                )
            ]
        )
        mock_create = AsyncMock(return_value=fake_response)

    fake_client = SimpleNamespace(
        chat=SimpleNamespace(
            completions=SimpleNamespace(
                create=mock_create
            )
        ),
        close=AsyncMock(),
        aclose=AsyncMock(),
    )

    return fake_client, mock_create

def test_resume_schema_accepts_valid_data():
    resume = ResumeData.model_validate(VALID_RESUME)

    assert resume.full_name == "Test Candidate"
    assert "Python" in resume.technical_skills


def test_resume_schema_rejects_invalid_field_type():
    invalid_resume = {
        **VALID_RESUME,
        "technical_skills": "Python",
    }

    with pytest.raises(ValidationError):
        ResumeData.model_validate(invalid_resume)


def test_resume_schema_accepts_optional_fields():
    resume = ResumeData.model_validate({
        "technical_skills": [],
        "soft_skills": [],
        "work_experience": [],
        "education": [],
    })

    assert resume.full_name is None
    assert resume.email is None




@pytest.mark.asyncio
async def test_parse_resume_with_ai_valid_response(monkeypatch):
    fake_client, mock_create = make_fake_groq_client(
        content=json.dumps(VALID_RESUME)
    )

    monkeypatch.setattr(
        resume_ai_service,
        "get_groq_client",
        lambda: fake_client,
    )

    result = await resume_ai_service.parse_resume_with_ai(
        "Test Candidate is a full-stack developer."
    )

    assert result.full_name == "Test Candidate"
    assert "Python" in result.technical_skills
    mock_create.assert_awaited_once()


@pytest.mark.asyncio
async def test_parse_resume_with_ai_invalid_json(monkeypatch):
    fake_client, _ = make_fake_groq_client(
        content="{ invalid json"
    )

    monkeypatch.setattr(
        resume_ai_service,
        "get_groq_client",
        lambda: fake_client,
    )

    with pytest.raises(ValueError):
        await resume_ai_service.parse_resume_with_ai(
            "Some extracted resume text"
        )


@pytest.mark.asyncio
async def test_parse_resume_with_ai_api_failure(monkeypatch):
    fake_client, mock_create = make_fake_groq_client(
        error=RuntimeError("Simulated provider failure")
    )

    monkeypatch.setattr(
        resume_ai_service,
        "get_groq_client",
        lambda: fake_client,
    )

    with pytest.raises(Exception):
        await resume_ai_service.parse_resume_with_ai(
            "Some extracted resume text"
        )

    mock_create.assert_awaited_once()


def test_parse_endpoint_returns_controlled_error(monkeypatch):
    def fake_parse_resume(filename, pdf_bytes):
        raise ValueError("Invalid PDF")

    monkeypatch.setattr(
        resume_controller,
        "parse_resume",
        fake_parse_resume,
        raising=False,
    )

    with TestClient(app) as client:
        response = client.post(
            "/api/resumes/parse",
            files={
                "file": (
                    "invalid.pdf",
                    b"not a real PDF",
                    "application/pdf",
                )
            },
        )

    # Verify the actual status code and response contract
    # defined by your controller's exception handling.
    assert response.status_code in (400, 422)