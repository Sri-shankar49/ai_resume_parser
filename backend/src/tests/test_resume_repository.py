
import pytest

from src.services import resume_repository as repository


@pytest.fixture
def test_database(tmp_path, monkeypatch):
    """Give each test its own temporary SQLite database."""
    database_path = tmp_path / "test_resumes.db"

    monkeypatch.setattr(
        repository,
        "DATABASE_PATH",
        database_path,
    )

    repository.initialize_database()

    return database_path


def test_create_and_retrieve_resume(test_database):
    resume = {
        "full_name": "Test Candidate",
        "email": "candidate@example.com",
        "technical_skills": ["Python", "React"],
        "soft_skills": [],
        "work_experience": [],
        "education": [],
    }

    created = repository.create_resume(
        resume_id="test-resume-1",
        filename="candidate.pdf",
        file_hash="hash-test-1",
        parsed_resume=resume,
    )

    assert created is not None
    assert created["resume_id"] == "test-resume-1"
    assert created["filename"] == "candidate.pdf"
    assert created["parsed_resume"]["full_name"] == "Test Candidate"

    retrieved = repository.get_resume("test-resume-1")

    assert retrieved is not None
    assert retrieved["parsed_resume"]["technical_skills"] == [
        "Python",
        "React",
    ]


def test_list_resumes(test_database):
    repository.create_resume(
        resume_id="test-resume-2",
        filename="second.pdf",
        file_hash="hash-test-2",
        parsed_resume={"full_name": "Second Candidate"},
    )

    records = repository.list_resumes()

    assert len(records) == 1
    assert records[0]["resume_id"] == "test-resume-2"


def test_find_resume_by_hash(test_database):
    repository.create_resume(
        resume_id="test-resume-3",
        filename="candidate.pdf",
        file_hash="hash-test-3",
        parsed_resume={"full_name": "Hash Candidate"},
    )

    record = repository.get_resume_by_hash("hash-test-3")

    assert record is not None
    assert record["resume_id"] == "test-resume-3"


def test_delete_resume(test_database):
    repository.create_resume(
        resume_id="test-resume-4",
        filename="delete-me.pdf",
        file_hash="hash-test-4",
        parsed_resume={"full_name": "Delete Candidate"},
    )

    deleted = repository.delete_resume("test-resume-4")

    assert deleted is True
    assert repository.get_resume("test-resume-4") is None


def test_missing_resume_returns_none(test_database):
    assert repository.get_resume("does-not-exist") is None
