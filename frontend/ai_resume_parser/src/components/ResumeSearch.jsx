
import { useState } from "react";
import { searchResumes } from "../services/resumeApi";

export default function ResumeSearch() {
    const [query, setQuery] = useState("");
    const [results, setResults] = useState([]);
    const [searched, setSearched] = useState(false);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    async function handleSearch(event) {
        event.preventDefault();

        if (!query.trim()) {
            setError("Enter a search query.");
            return;
        }

        setLoading(true);
        setError("");
        setSearched(false);

        try {
            const data = await searchResumes(query.trim(), 5);
            setResults(data.results || []);
            setSearched(true);
        } catch (err) {
            setError(err.message || "Search failed.");
        } finally {
            setLoading(false);
        }
    }

    return (
        <section className="panel">
            <h2>Semantic Resume Search</h2>
            <p className="muted">
                Search by skills, experience, or a natural-language description.
            </p>

            <form className="search-form" onSubmit={handleSearch}>
                <input
                    type="text"
                    value={query}
                    onChange={(event) => setQuery(event.target.value)}
                    placeholder="e.g. React developer with Python API experience"
                    maxLength={1000}
                />

                <button
                    className="primary-button"
                    type="submit"
                    disabled={loading || !query.trim()}
                >
                    {loading ? "Searching..." : "Search"}
                </button>
            </form>

            {error && <p className="error">{error}</p>}

            {searched && (
                <div className="search-results">
                    <h3>Results ({results.length})</h3>

                    {results.length === 0 && (
                        <p className="muted">
                            No resumes found. Upload and parse resumes first.
                        </p>
                    )}

                    {results.map((resume) => (
                        <article className="result-card" key={resume.resume_id}>
                            <h3>{resume.full_name || "Unknown Candidate"}</h3>

                            <p className="muted">{resume.filename}</p>

                            <p className="distance">
                                Cosine distance: {Number(resume.distance).toFixed(4)}
                            </p>

                            <details>
                                <summary>View indexed resume text</summary>
                                <p className="resume-text">{resume.resume_text}</p>
                            </details>
                        </article>
                    ))}
                </div>
            )}
        </section>
    );
}
