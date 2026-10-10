from datetime import datetime

from pydantic import BaseModel, Field




class WorkExperience(BaseModel):
    job_title: str | None = None
    company: str | None = None
    duration: str | None = None
    responsibilities: list[str] = Field(default_factory=list)


class Education(BaseModel):
    degree: str | None = None
    institution: str | None = None
    graduation_year: str | None = None


class ResumeData(BaseModel):
    full_name: str | None = None
    email: str | None = None
    phone: str | None = None
    location: str | None = None

    professional_summary: str | None = None

    technical_skills: list[str] = Field(default_factory=list)
    soft_skills: list[str] = Field(default_factory=list)

    work_experience: list[WorkExperience] = Field(
        default_factory=list
    )

    education: list[Education] = Field(
        default_factory=list
    )


class ResumeExtractionResponse(BaseModel):
    filename: str
    pages: int
    extracted_text: str
    message: str


class ResumeParseResponse(BaseModel):
    resume_id: str
    filename: str
    parsed_resume: ResumeData
    message: str
    duplicate: bool = False


class ResumeRecord(BaseModel):
    resume_id: str
    filename: str
    parsed_resume: ResumeData
    created_at: datetime
    updated_at: datetime


class ResumeListResponse(BaseModel):
    count: int
    resumes: list[ResumeRecord]


class ResumeDeleteResponse(BaseModel):
    resume_id: str
    message: str
