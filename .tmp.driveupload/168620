/**
 * HomePage — Landing page with company input form.
 * 
 * This is the entry point for the interview intelligence workflow.
 * Users enter a company name and optional URL, then the system
 * generates an AI-powered interview brief.
 * 
 * @module HomePage
 */

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';

/**
 * Home page component with company input form.
 * 
 * @returns {JSX.Element} The rendered home page.
 */
function HomePage() {
    const navigate = useNavigate();
    const [companyName, setCompanyName] = useState('');
    const [companyUrl, setCompanyUrl] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    /**
     * Handle form submission — create session and start pipeline.
     * @param {Event} e - Form submit event.
     */
    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!companyName.trim()) return;

        setLoading(true);
        setError('');

        try {
            const session = await api.createSession(companyName, companyUrl);
            navigate(`/dashboard/${session.sessionId}`);
        } catch (err) {
            setError(err.message || 'Failed to create session. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="container animate-fade-in" style={styles.page}>
            {/* Hero Section */}
            <div style={styles.hero}>
                <span style={styles.heroEmoji}>🎯</span>
                <h1 style={styles.title}>
                    Interview
                    <span style={styles.titleAccent}> Intelligence</span>
                </h1>
                <p style={styles.subtitle}>
                    AI-powered interview preparation that transforms public data into
                    strategic conversation guides in minutes.
                </p>
            </div>

            {/* Input Form */}
            <div className="card" style={styles.formCard}>
                <form onSubmit={handleSubmit} style={styles.form}>
                    <div style={styles.inputGroup}>
                        <label htmlFor="company-name" style={styles.label}>
                            Company Name *
                        </label>
                        <input
                            id="company-name"
                            className="input"
                            type="text"
                            value={companyName}
                            onChange={(e) => setCompanyName(e.target.value)}
                            placeholder="e.g., GridFlex Energy"
                            required
                            disabled={loading}
                        />
                    </div>

                    <div style={styles.inputGroup}>
                        <label htmlFor="company-url" style={styles.label}>
                            Company Website
                            <span style={styles.labelOptional}> (optional)</span>
                        </label>
                        <input
                            id="company-url"
                            className="input"
                            type="url"
                            value={companyUrl}
                            onChange={(e) => setCompanyUrl(e.target.value)}
                            placeholder="https://example.com"
                            disabled={loading}
                        />
                    </div>

                    {error && (
                        <div style={styles.error} id="form-error">
                            ⚠️ {error}
                        </div>
                    )}

                    <button
                        type="submit"
                        className="btn btn-primary btn-lg"
                        id="start-session-btn"
                        disabled={loading || !companyName.trim()}
                        style={styles.submitBtn}
                    >
                        {loading ? (
                            <>
                                <span className="animate-pulse">⏳</span> Generating Intelligence...
                            </>
                        ) : (
                            <>🚀 Generate Interview Brief</>
                        )}
                    </button>
                </form>
            </div>

            {/* Features Grid */}
            <div style={styles.features}>
                {[
                    { icon: '🌐', title: 'Web Intelligence', desc: 'Scrapes public data for company insights' },
                    { icon: '🧠', title: 'AI Analysis', desc: 'Claude generates strategic questions' },
                    { icon: '📋', title: 'Smart Briefs', desc: 'Ready-to-use interviewer guides' },
                    { icon: '🔄', title: 'Interviewee Loop', desc: 'Feedback refines the conversation' },
                ].map((feature, i) => (
                    <div className="card" key={i} style={styles.featureCard}>
                        <span style={styles.featureIcon}>{feature.icon}</span>
                        <h3 style={styles.featureTitle}>{feature.title}</h3>
                        <p style={styles.featureDesc}>{feature.desc}</p>
                    </div>
                ))}
            </div>
        </div>
    );
}

/** @type {Object} Component styles */
const styles = {
    page: {
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        gap: 'var(--space-12)',
        paddingTop: 'var(--space-8)',
    },
    hero: {
        textAlign: 'center',
        maxWidth: '700px',
    },
    heroEmoji: {
        fontSize: '3rem',
        display: 'block',
        marginBottom: 'var(--space-4)',
    },
    title: {
        fontSize: 'var(--text-5xl)',
        fontWeight: 800,
        lineHeight: 1.1,
        marginBottom: 'var(--space-4)',
    },
    titleAccent: {
        background: 'linear-gradient(135deg, var(--color-primary), var(--color-accent))',
        WebkitBackgroundClip: 'text',
        WebkitTextFillColor: 'transparent',
    },
    subtitle: {
        fontSize: 'var(--text-lg)',
        color: 'var(--text-secondary)',
        lineHeight: 1.6,
    },
    formCard: {
        maxWidth: '560px',
        width: '100%',
        padding: 'var(--space-8)',
    },
    form: {
        display: 'flex',
        flexDirection: 'column',
        gap: 'var(--space-6)',
    },
    inputGroup: {
        display: 'flex',
        flexDirection: 'column',
        gap: 'var(--space-2)',
    },
    label: {
        fontSize: 'var(--text-sm)',
        fontWeight: 600,
        color: 'var(--text-primary)',
    },
    labelOptional: {
        fontWeight: 400,
        color: 'var(--text-muted)',
    },
    error: {
        padding: 'var(--space-3) var(--space-4)',
        background: 'rgba(239, 68, 68, 0.1)',
        border: '1px solid rgba(239, 68, 68, 0.3)',
        borderRadius: 'var(--radius-lg)',
        color: 'var(--color-error)',
        fontSize: 'var(--text-sm)',
    },
    submitBtn: {
        marginTop: 'var(--space-2)',
    },
    features: {
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
        gap: 'var(--space-6)',
        maxWidth: '960px',
        width: '100%',
    },
    featureCard: {
        textAlign: 'center',
        padding: 'var(--space-6)',
    },
    featureIcon: {
        fontSize: '2rem',
        display: 'block',
        marginBottom: 'var(--space-3)',
    },
    featureTitle: {
        fontSize: 'var(--text-base)',
        fontWeight: 600,
        marginBottom: 'var(--space-2)',
    },
    featureDesc: {
        fontSize: 'var(--text-sm)',
        color: 'var(--text-muted)',
    },
};

export default HomePage;
