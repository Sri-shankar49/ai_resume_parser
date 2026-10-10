
const API_BASE_URL =
    import.meta.env.VITE_API_BASE_URL ||
    "http://127.0.0.1:8000";

async function handleResponse(response) {
    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
        throw new Error(
            data.detail || "Something went wrong. Please try again."
        );
    }

    return data;
}

export async function parseResume(file) {
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch(
        `${API_BASE_URL}/api/resumes/parse`,
        {
            method: "POST",
            body: formData,
        }
    );

    return handleResponse(response);
}

export async function searchResumes(query, topK = 5) {
    const response = await fetch(
        `${API_BASE_URL}/api/resumes/search`,
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                query,
                top_k: topK,
            }),
        }
    );

    return handleResponse(response);
}


export async function getResumes() {
    const response = await fetch(
        `${API_BASE_URL}/api/resumes`
    );

    return handleResponse(response);
}

export async function getResumeById(resumeId) {
    const response = await fetch(
        `${API_BASE_URL}/api/resumes/${encodeURIComponent(resumeId)}`
    );

    return handleResponse(response);
}

export async function deleteResume(resumeId) {
    const response = await fetch(
        `${API_BASE_URL}/api/resumes/${encodeURIComponent(resumeId)}`,
        {
            method: "DELETE",
        }
    );

    return handleResponse(response);
}
