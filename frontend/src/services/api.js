/**
 * API Service — Frontend client for InterviewIQ backend.
 * 
 * Provides typed functions for all API endpoints. Handles JSON
 * serialization, error handling, and base URL configuration.
 * 
 * Usage:
 *   import api from '../services/api';
 *   const session = await api.createSession('GridFlex Energy', 'https://...');
 * 
 * @module api
 */

/** Base URL for the API — configured per environment */
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:3000';

/**
 * Make an HTTP request to the API.
 * 
 * @param {string} endpoint - API path (e.g., '/sessions').
 * @param {Object} options - Fetch options.
 * @param {string} [options.method='GET'] - HTTP method.
 * @param {Object} [options.body] - Request body (auto-serialized to JSON).
 * @returns {Promise<Object>} Parsed JSON response.
 * @throws {Error} If the request fails or returns an error status.
 */
async function request(endpoint, { method = 'GET', body } = {}) {
    const config = {
        method,
        headers: { 'Content-Type': 'application/json' },
    };

    if (body) {
        config.body = JSON.stringify(body);
    }

    const response = await fetch(`${API_BASE_URL}${endpoint}`, config);
    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.error || `API error: ${response.status}`);
    }

    return data;
}

/**
 * InterviewIQ API client.
 * @namespace api
 */
const api = {
    /**
     * Create a new interview preparation session.
     * 
     * @param {string} companyName - Name of the target company.
     * @param {string} [companyUrl] - Optional company website URL.
     * @returns {Promise<Object>} Created session with sessionId.
     */
    createSession: (companyName, companyUrl) =>
        request('/sessions', {
            method: 'POST',
            body: { companyName, companyUrl },
        }),

    /**
     * Retrieve session data by ID.
     * 
     * @param {string} sessionId - The session identifier.
     * @returns {Promise<Object>} Full session data.
     */
    getSession: (sessionId) =>
        request(`/sessions/${sessionId}`),

    /**
     * Start the full interview intelligence pipeline.
     * 
     * @param {string} companyName - Company name.
     * @param {string} [companyUrl] - Optional company URL.
     * @param {string[]} [documents] - Optional S3 keys of uploaded documents.
     * @returns {Promise<Object>} Pipeline execution details.
     */
    startPipeline: (companyName, companyUrl, documents = []) =>
        request('/pipeline', {
            method: 'POST',
            body: { companyName, companyUrl, documents },
        }),

    /**
     * Check pipeline execution status.
     * 
     * @param {string} executionId - Pipeline execution ID.
     * @returns {Promise<Object>} Execution status and output.
     */
    getPipelineStatus: (executionId) =>
        request(`/pipeline/${executionId}`),

    /**
     * Submit interviewee feedback (corrections and question selection).
     * 
     * @param {string} sessionId - The session identifier.
     * @param {Object[]} corrections - List of AI finding corrections.
     * @param {string[]} selectedQuestions - IDs of selected questions.
     * @param {string} [notes] - Optional free-form notes.
     * @returns {Promise<Object>} Confirmation of stored feedback.
     */
    submitFeedback: (sessionId, corrections, selectedQuestions, notes) =>
        request(`/sessions/${sessionId}/feedback`, {
            method: 'POST',
            body: { corrections, selectedQuestions, notes },
        }),

    /**
     * Check API health status.
     * 
     * @returns {Promise<Object>} Health check response.
     */
    healthCheck: () => request('/health'),
};

export default api;
