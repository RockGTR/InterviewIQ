/**
 * Interviewee Portal — Pre-interview review and feedback form.
 * 
 * Allows the interviewee to review AI-generated findings about
 * their company, correct inaccuracies, and select preferred
 * discussion questions before the interview.
 * 
 * Route: /interview/:sessionId
 * @module IntervieweePortal
 */

import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../services/api';

/**
 * Interviewee portal component.
 * 
 * @returns {JSX.Element} The rendered portal.
 */
function IntervieweePortal() {
    const { sessionId } = useParams();
    const navigate = useNavigate();
    const [session, setSession] = useState(null);
    const [loading, setLoading] = useState(true);
    const [submitting, setSubmitting] = useState(false);
    const [selectedQuestions, setSelectedQuestions] = useState([]);
    const [corrections, setCorrections] = useState([]);
    const [notes, setNotes] = useState('');
    const [submitted, setSubmitted] = useState(false);

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

    /**
     * Toggle question selection.
     * @param {string} questionId - The question to toggle.
     */
    const toggleQuestion = (questionId) => {
        setSelectedQuestions((prev) =>
            prev.includes(questionId)
                ? prev.filter((id) => id !== questionId)
                : [...prev, questionId]
        );
    };

    /** Submit feedback to the API. */
    const handleSubmit = async () => {
        setSubmitting(true);
        try {
            await api.submitFeedback(sessionId, corrections, selectedQuestions, notes);
            setSubmitted(true);
        } catch (err) {
            console.error('Failed to submit feedback:', err);
        } finally {
            setSubmitting(false);
        }
    };

    if (loading) {
        return (
            <div className="container animate-fade-in" style={styles.centered}>
                <div className="animate-pulse" style={{ fontSize: '3rem' }}>📋</div>
                <h2>Loading your pre-interview packet...</h2>
            </div>
        );
    }

    if (submitted) {
        return (
            <div className="container animate-fade-in" style={styles.centered}>
                <div style={{ fontSize: '4rem', marginBottom: 'var(--space-4)' }}>✅</div>
                <h2>Thank You!</h2>
                <p style={{ color: 'var(--text-secondary)', marginTop: 'var(--space-2)' }}>
                    Your feedback has been received. Your interviewer will use this
                    to create a more focused conversation.
                </p>
            </div>
        );
    }

    return (
        <div className="container animate-fade-in" style={styles.page}>
            {/* Header */}
            <div style={styles.header}>
                <h1 style={styles.title}>Pre-Interview Review</h1>
                <p style={styles.subtitle}>
                    Our AI researched <strong>{session?.companyName}</strong>. Please review
                    what we found and help us prepare better questions for your interview.
                </p>
            </div>

            {/* AI Findings */}
            <div className="card" id="ai-findings-card">
                <h3 style={styles.sectionTitle}>
                    🤖 What Our AI Found
                    <span style={styles.sectionHint}> — Please correct any inaccuracies</span>
                </h3>
                <div style={styles.findingsContent}>
                    <p style={{ color: 'var(--text-secondary)', lineHeight: 1.7 }}>
                        {session?.intervieweePacket?.invitation_text ||
                            'AI findings about your company will appear here.'}
                    </p>
                </div>
            </div>

            {/* Notes */}
            <div className="card" id="notes-card">
                <h3 style={styles.sectionTitle}>📝 Your Notes</h3>
                <p style={{ color: 'var(--text-muted)', fontSize: 'var(--text-sm)', marginBottom: 'var(--space-3)' }}>
                    Anything you'd like us to know before the interview?
                </p>
                <textarea
                    className="input"
                    id="interviewee-notes"
                    value={notes}
                    onChange={(e) => setNotes(e.target.value)}
                    placeholder="Share any context, corrections, or topics you'd like to discuss..."
                    rows={4}
                    style={{ resize: 'vertical' }}
                />
            </div>

            {/* Submit */}
            <div style={styles.submitSection}>
                <button
                    className="btn btn-primary btn-lg"
                    id="submit-feedback-btn"
                    onClick={handleSubmit}
                    disabled={submitting}
                >
                    {submitting ? '⏳ Submitting...' : '✅ Submit Review'}
                </button>
                <p style={{ color: 'var(--text-muted)', fontSize: 'var(--text-xs)' }}>
                    Your responses help create a more productive interview experience.
                </p>
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
        maxWidth: '800px',
        margin: '0 auto',
    },
    centered: {
        textAlign: 'center',
        paddingTop: 'var(--space-16)',
        maxWidth: '500px',
        margin: '0 auto',
    },
    header: {
        textAlign: 'center',
    },
    title: {
        fontSize: 'var(--text-3xl)',
        marginBottom: 'var(--space-3)',
    },
    subtitle: {
        color: 'var(--text-secondary)',
        fontSize: 'var(--text-lg)',
    },
    sectionTitle: {
        fontSize: 'var(--text-lg)',
        marginBottom: 'var(--space-4)',
    },
    sectionHint: {
        fontSize: 'var(--text-sm)',
        fontWeight: 400,
        color: 'var(--text-muted)',
    },
    findingsContent: {
        padding: 'var(--space-4)',
        background: 'var(--bg-tertiary)',
        borderRadius: 'var(--radius-md)',
    },
    submitSection: {
        textAlign: 'center',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        gap: 'var(--space-3)',
    },
};

export default IntervieweePortal;
