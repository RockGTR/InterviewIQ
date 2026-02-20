/**
 * Interview Guide — Updated guide incorporating interviewee feedback.
 * 
 * Displays the final interview guide that merges the AI-generated
 * brief with the interviewee's corrections and selected questions.
 * This is what the interviewer uses during the actual conversation.
 * 
 * Route: /guide/:sessionId
 * @module InterviewGuide
 */

import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import api from '../services/api';

/**
 * Interview guide component.
 * 
 * @returns {JSX.Element} The rendered guide.
 */
function InterviewGuide() {
    const { sessionId } = useParams();
    const [session, setSession] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadSession();
    }, [sessionId]);

    /** Load session data from the API. */
    const loadSession = async () => {
        try {
            const data = await api.getSession(sessionId);
            setSession(data);
        } catch (err) {
            console.error('Failed to load session:', err);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="container animate-fade-in" style={styles.centered}>
                <div className="animate-pulse" style={{ fontSize: '3rem' }}>📖</div>
                <h2>Loading Interview Guide...</h2>
            </div>
        );
    }

    const hasFeedback = session?.feedback?.submittedAt;

    return (
        <div className="container animate-fade-in" style={styles.page}>
            {/* Header */}
            <div style={styles.header}>
                <div>
                    <div className="badge badge-success" style={{ marginBottom: 'var(--space-2)' }}>
                        {hasFeedback ? '✅ Feedback Incorporated' : '⏳ Awaiting Feedback'}
                    </div>
                    <h1 style={styles.title}>Interview Guide</h1>
                    <p style={styles.companyName}>{session?.companyName}</p>
                </div>
                <Link to={`/dashboard/${sessionId}`} className="btn btn-secondary">
                    ← Back to Dashboard
                </Link>
            </div>

            {/* Feedback Summary */}
            {hasFeedback && (
                <div className="card" style={styles.feedbackCard} id="feedback-summary">
                    <h3 style={styles.sectionTitle}>🔄 Interviewee Feedback</h3>
                    <div style={styles.feedbackGrid}>
                        <div>
                            <span style={styles.feedbackLabel}>Corrections</span>
                            <span style={styles.feedbackValue}>
                                {session.feedback.corrections?.length || 0}
                            </span>
                        </div>
                        <div>
                            <span style={styles.feedbackLabel}>Selected Questions</span>
                            <span style={styles.feedbackValue}>
                                {session.feedback.selectedQuestions?.length || 0}
                            </span>
                        </div>
                        {session.feedback.notes && (
                            <div style={{ gridColumn: '1 / -1' }}>
                                <span style={styles.feedbackLabel}>Notes</span>
                                <p style={{ color: 'var(--text-secondary)', marginTop: 'var(--space-1)' }}>
                                    "{session.feedback.notes}"
                                </p>
                            </div>
                        )}
                    </div>
                </div>
            )}

            {/* Guide Sections */}
            <div style={styles.guideGrid}>
                <div className="card" id="opening-card">
                    <h3 style={styles.sectionTitle}>👋 Opening</h3>
                    <p style={styles.guideText}>
                        "Thank you for taking the time to review our AI research.
                        Before we dive in, I'd love to hear — what did we get wrong?"
                    </p>
                    <p style={styles.guideHint}>
                        This warm-up validates the interviewee's expertise and builds trust.
                    </p>
                </div>

                <div className="card" id="core-questions-card">
                    <h3 style={styles.sectionTitle}>❓ Core Questions</h3>
                    <p style={styles.placeholder}>
                        Selected questions and AI-generated follow-ups will appear here
                        once the pipeline completes and feedback is received.
                    </p>
                </div>

                <div className="card" id="deep-dive-card">
                    <h3 style={styles.sectionTitle}>🔍 Deep Dive Topics</h3>
                    <p style={styles.placeholder}>
                        Deeper probing questions based on initial responses.
                    </p>
                </div>

                <div className="card" id="closing-card">
                    <h3 style={styles.sectionTitle}>🎯 Closing</h3>
                    <p style={styles.guideText}>
                        "Is there anything about your business that we haven't covered
                        that you think is important for us to understand?"
                    </p>
                </div>
            </div>
        </div>
    );
}

/** @type {Object} Component styles */
const styles = {
    page: {
        display: 'flex',
        flexDirection: 'column',
        gap: 'var(--space-8)',
    },
    centered: {
        textAlign: 'center',
        paddingTop: 'var(--space-16)',
    },
    header: {
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'flex-start',
        flexWrap: 'wrap',
        gap: 'var(--space-4)',
    },
    title: {
        fontSize: 'var(--text-3xl)',
    },
    companyName: {
        color: 'var(--text-secondary)',
        fontSize: 'var(--text-lg)',
    },
    feedbackCard: {
        borderColor: 'rgba(16, 185, 129, 0.3)',
    },
    sectionTitle: {
        fontSize: 'var(--text-lg)',
        marginBottom: 'var(--space-4)',
    },
    feedbackGrid: {
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
        gap: 'var(--space-4)',
    },
    feedbackLabel: {
        display: 'block',
        fontSize: 'var(--text-xs)',
        color: 'var(--text-muted)',
        textTransform: 'uppercase',
        letterSpacing: '0.05em',
    },
    feedbackValue: {
        display: 'block',
        fontSize: 'var(--text-2xl)',
        fontWeight: 700,
        color: 'var(--color-success)',
        marginTop: 'var(--space-1)',
    },
    guideGrid: {
        display: 'flex',
        flexDirection: 'column',
        gap: 'var(--space-6)',
    },
    guideText: {
        color: 'var(--text-secondary)',
        lineHeight: 1.7,
        fontStyle: 'italic',
        padding: 'var(--space-4)',
        background: 'var(--bg-tertiary)',
        borderRadius: 'var(--radius-md)',
        borderLeft: '3px solid var(--color-primary)',
    },
    guideHint: {
        color: 'var(--text-muted)',
        fontSize: 'var(--text-sm)',
        marginTop: 'var(--space-3)',
    },
    placeholder: {
        color: 'var(--text-muted)',
        fontStyle: 'italic',
    },
};

export default InterviewGuide;
