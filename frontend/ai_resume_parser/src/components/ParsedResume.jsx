
function DetailList({ title, items, renderItem }) {
    if (!items?.length) return null;

    return (
        <div className="detail-section">
            <h3>{title}</h3>
            <ul>
                {items.map((item, index) => (
                    <li key={index}>{renderItem(item)}</li>
                ))}
            </ul>
        </div>
    );
}

export default function ParsedResume({ result }) {
    if (!result) {
        return (
            <section className="panel empty-state">
                <h2>Parsed Profile</h2>
                <p className="muted">
                    Upload a resume to view candidate information here.
                </p>
            </section>
        );
    }

    const resume = result.parsed_resume;

    return (
        <section className="panel">
            <div className="section-heading">
                <div>
                    <h2>{resume.full_name || "Unknown Candidate"}</h2>
                    <p className="muted">{result.filename}</p>
                </div>

                <span className="status-badge">Parsed</span>
            </div>

            <p>
                <strong>Resume ID:</strong>{" "}
                <code>{result.resume_id}</code>
            </p>

            {resume.professional_summary && (
                <div className="detail-section">
                    <h3>Professional Summary</h3>
                    <p>{resume.professional_summary}</p>
                </div>
            )}

            <div className="contact-grid">
                <div>
                    <span className="muted">Email</span>
                    <p>{resume.email || "Not provided"}</p>
                </div>

                <div>
                    <span className="muted">Phone</span>
                    <p>{resume.phone || "Not provided"}</p>
                </div>

                <div>
                    <span className="muted">Location</span>
                    <p>{resume.location || "Not provided"}</p>
                </div>
            </div>

            <div className="detail-section">
                <h3>Technical Skills</h3>

                {resume.technical_skills?.length ? (
                    <div className="skill-list">
                        {resume.technical_skills.map((skill, index) => (
                            <span className="skill-tag" key={`${skill}-${index}`}>
                                {skill}
                            </span>
                        ))}
                    </div>
                ) : (
                    <p className="muted">No technical skills identified.</p>
                )}
            </div>

            <DetailList
                title="Soft Skills"
                items={resume.soft_skills}
                renderItem={(item) => item}
            />

            <DetailList
                title="Work Experience"
                items={resume.work_experience}
                renderItem={(job) => (
                    <div>
                        <strong>{job.job_title || "Role not specified"}</strong>
                        <p className="muted">
                            {job.company || "Company not specified"}
                            {job.duration ? ` · ${job.duration}` : ""}
                        </p>

                        {job.responsibilities?.length > 0 && (
                            <ul>
                                {job.responsibilities.map((item, index) => (
                                    <li key={index}>{item}</li>
                                ))}
                            </ul>
                        )}
                    </div>
                )}
            />

            <DetailList
                title="Education"
                items={resume.education}
                renderItem={(education) => (
                    <div>
                        <strong>{education.degree || "Degree not specified"}</strong>
                        <p className="muted">
                            {education.institution || "Institution not specified"}
                            {education.graduation_year
                                ? ` · ${education.graduation_year}`
                                : ""}
                        </p>
                    </div>
                )}
            />
        </section>
    );
}
