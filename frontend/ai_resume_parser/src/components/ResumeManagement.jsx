
import { useCallback, useEffect, useState } from "react";
import {
    getResumes,
    getResumeById,
    deleteResume,
} from "../services/resumeApi";

export default function ResumeManagement() {
    const [resumes, setResumes] = useState([]);
    const [selectedResume, setSelectedResume] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [actionLoading, setActionLoading] = useState(false);

    const loadResumes = useCallback(async () => {
        setLoading(true);
        setError("");

        try {
            const data = await getResumes();
            setResumes(data.resumes || []);
        } catch (err) {
            setError(err.message || "Unable to load resumes.");
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        let isActive = true;

        getResumes()
            .then((data) => {
                if (isActive) {
                    setResumes(data.resumes || []);
                }
            })
            .catch((err) => {
                if (isActive) {
                    setError(err.message || "Unable to load resumes.");
                }
            })
            .finally(() => {
                if (isActive) {
                    setLoading(false);
                }
            });

        return () => {
            isActive = false;
        };
    }, []);

    async function handleView(resumeId) {
        setActionLoading(true);
        setError("");

        try {
            const profile = await getResumeById(resumeId);
            setSelectedResume(profile);
        } catch (err) {
            setError(err.message || "Unable to load candidate.");
        } finally {
            setActionLoading(false);
        }
    }

    async function handleDelete(resume) {
        const confirmed = window.confirm(
            `Delete the resume "${resume.filename}"?`
        );

        if (!confirmed) return;

        setActionLoading(true);
        setError("");

        try {
            await deleteResume(resume.resume_id);

            if (selectedResume?.resume_id === resume.resume_id) {
                setSelectedResume(null);
            }

            await loadResumes();
        } catch (err) {
            setError(err.message || "Unable to delete resume.");
        } finally {
            setActionLoading(false);
        }
    }

    return (
        <section className="panel">
            <div className="section-heading">
                <h2>Resume Management</h2>

                <button
                    className="primary-button"
                    onClick={loadResumes}
                    disabled={loading || actionLoading}
                >
                    Refresh
                </button>
            </div>

            {error && <p className="error">{error}</p>}

            {loading ? (
                <p className="muted">Loading resumes...</p>
            ) : resumes.length === 0 ? (
                <p className="muted">No stored resumes yet.</p>
            ) : (
                <div className="management-list">
                    {resumes.map((resume) => (
                        <article
                            className="result-card"
                            key={resume.resume_id}
                        >
                            <h3>
                                {resume.parsed_resume.full_name ||
                                    "Unknown Candidate"}
                            </h3>

                            <p className="muted">{resume.filename}</p>

                            <p className="muted">
                                Added: {new Date(resume.created_at).toLocaleString()}
                            </p>

                            <div className="management-actions">
                                <button
                                    className="secondary-button"
                                    disabled={actionLoading}
                                    onClick={() => handleView(resume.resume_id)}
                                >
                                    View Profile
                                </button>

                                <button
                                    className="danger-button"
                                    disabled={actionLoading}
                                    onClick={() => handleDelete(resume)}
                                >
                                    Delete
                                </button>
                            </div>
                        </article>
                    ))}
                </div>
            )}

            {selectedResume && (
                <div className="detail-section">
                    <h3>Candidate Profile</h3>

                    <p>
                        <strong>Name:</strong>{" "}
                        {selectedResume.parsed_resume.full_name ||
                            "Unknown Candidate"}
                    </p>

                    <p>
                        <strong>Email:</strong>{" "}
                        {selectedResume.parsed_resume.email ||
                            "Not provided"}
                    </p>

                    <p>
                        <strong>Resume ID:</strong>{" "}
                        <code>{selectedResume.resume_id}</code>
                    </p>

                    <button
                        className="secondary-button"
                        onClick={() => setSelectedResume(null)}
                    >
                        Close Profile
                    </button>
                </div>
            )}
        </section>
    );
}
