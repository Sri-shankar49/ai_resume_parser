
import { useRef, useState } from "react";
import { parseResume } from "../services/resumeApi";

export default function ResumeUpload({ onParsed }) {
    const [file, setFile] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const inputRef = useRef(null);

    function handleFileChange(event) {
        const selectedFile = event.target.files?.[0];

        setError("");
        setFile(null);

        if (!selectedFile) return;

        if (!selectedFile.name.toLowerCase().endsWith(".pdf")) {
            setError("Please select a PDF resume.");
            event.target.value = "";
            return;
        }

        if (selectedFile.size > 10 * 1024 * 1024) {
            setError("The PDF must be 10 MB or smaller.");
            event.target.value = "";
            return;
        }

        setFile(selectedFile);
    }

    async function handleUpload(event) {
        event.preventDefault();

        if (!file) {
            setError("Please select a resume first.");
            return;
        }

        setLoading(true);
        setError("");

        try {
            const result = await parseResume(file);
            onParsed(result);
            setFile(null);

            if (inputRef.current) {
                inputRef.current.value = "";
            }
        } catch (err) {
            setError(err.message || "Unable to parse resume.");
        } finally {
            setLoading(false);
        }
    }

    return (
        <section className="panel">
            <h2>Upload Resume</h2>
            <p className="muted">
                Upload a PDF to extract and analyze candidate details.
            </p>

            <form onSubmit={handleUpload}>
                <label className="file-picker">
                    <span className="file-icon">📄</span>
                    <span>
                        {file ? file.name : "Choose a PDF resume"}
                    </span>

                    <input
                        ref={inputRef}
                        type="file"
                        accept=".pdf,application/pdf"
                        onChange={handleFileChange}
                    />
                </label>

                <button
                    className="primary-button"
                    type="submit"
                    disabled={!file || loading}
                >
                    {loading ? "Analyzing resume..." : "Upload & Analyze"}
                </button>
            </form>

            {loading && (
                <p className="muted">
                    Extracting text, analyzing with AI, and storing vectors...
                </p>
            )}

            {error && <p className="error">{error}</p>}
        </section>
    );
}
