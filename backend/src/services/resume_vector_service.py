
import os
import uuid

from pathlib import Path
from functools import lru_cache

import chromadb
from sentence_transformers import SentenceTransformer


# Resolve the database path relative to the backend folder.
BACKEND_DIR = Path(__file__).resolve().parents[2]

db_path = Path(
    os.getenv("CHROMA_DB_PATH", "./chroma_db")
)

db_path.mkdir(parents=True, exist_ok=True)

if not db_path.is_absolute():
    db_path = BACKEND_DIR / db_path

MODEL_NAME = os.getenv(
    "EMBEDDING_MODEL",
    "sentence-transformers/all-MiniLM-L6-v2",
)

COLLECTION_NAME = os.getenv(
    "CHROMA_COLLECTION_NAME",
    "resumes",
)


@lru_cache(maxsize=1)
def get_embedding_model():
    """Load the embedding model once per process."""
    return SentenceTransformer(MODEL_NAME)


@lru_cache(maxsize=1)
def get_collection():
    """Create or reopen our persistent ChromaDB collection."""
    client = chromadb.PersistentClient(
        path=str(db_path)
    )

    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


def build_resume_text(resume: dict) -> str:
    """Build searchable text from structured resume data."""
    parts = [
        f"Name: {resume.get('full_name') or ''}",
        f"Summary: {resume.get('professional_summary') or ''}",
        f"Technical skills: {', '.join(resume.get('technical_skills') or [])}",
        f"Soft skills: {', '.join(resume.get('soft_skills') or [])}",
    ]

    for job in resume.get("work_experience", []):
        parts.append(
            "Experience: "
            f"{job.get('job_title') or ''} "
            f"at {job.get('company') or ''}. "
            f"{' '.join(job.get('responsibilities') or [])}"
        )

    for education in resume.get("education", []):
        parts.append(
            "Education: "
            f"{education.get('degree') or ''} "
            f"at {education.get('institution') or ''}"
        )

    return "\n".join(parts)


def store_resume(
    filename: str,
    resume: dict,
    resume_id: str,
) -> str:
    """Embed a parsed resume and save it to ChromaDB."""
    searchable_text = build_resume_text(resume)

    if not searchable_text.strip():
        raise ValueError("No resume information to store.")

    model = get_embedding_model()

    embedding = model.encode(
        searchable_text,
        normalize_embeddings=True,
    ).tolist()

    # resume_id = str(uuid.uuid4())

    collection = get_collection()

    # collection.add(
    #     ids=[resume_id],
    #     documents=[searchable_text],
    #     embeddings=[embedding],
    #     metadatas=[{
    #         "filename": filename,
    #         "full_name": resume.get("full_name") or "Unknown",
    #     }],
    # )
    
    collection.upsert(
            ids=[resume_id],
            documents=[searchable_text],
            embeddings=[embedding],
            metadatas=[{
                "filename": filename,
                "full_name": resume.get("full_name") or "Unknown",
            }],
        )

    return resume_id


def delete_resume_vector(resume_id: str) -> None:
    """Delete a resume's vector from ChromaDB."""
    collection = get_collection()
    collection.delete(ids=[resume_id])


def search_resumes(
    query: str,
    top_k: int = 5,
) -> list[dict]:
    """Find resumes semantically similar to a query."""
    if not query.strip():
        raise ValueError("Search query cannot be empty.")

    if not 1 <= top_k <= 20:
        raise ValueError("top_k must be between 1 and 20.")

    collection = get_collection()

    if collection.count() == 0:
        return []

    model = get_embedding_model()

    query_embedding = model.encode(
        query,
        normalize_embeddings=True,
    ).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(top_k, collection.count()),
        include=["documents", "metadatas", "distances"],
    )

    matches = []

    for index, resume_id in enumerate(results["ids"][0]):
        matches.append({
            "resume_id": resume_id,
            "filename": results["metadatas"][0][index]["filename"],
            "full_name": results["metadatas"][0][index]["full_name"],
            "resume_text": results["documents"][0][index],
            "distance": results["distances"][0][index],
        })

    return matches
