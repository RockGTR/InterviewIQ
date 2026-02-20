/**
 * InterviewIQ — AI-Powered Interview Intelligence System
 * 
 * Main application component with React Router configuration.
 * Routes users between the home page, interviewer dashboard,
 * interviewee portal, and interview guide views.
 * 
 * @module App
 */

import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import HomePage from './pages/HomePage';
import InterviewerDashboard from './pages/InterviewerDashboard';
import IntervieweePortal from './pages/IntervieweePortal';
import InterviewGuide from './pages/InterviewGuide';

/**
 * Root application component.
 * 
 * Configures client-side routing for the four main views:
 * - `/` — Home page with company input form
 * - `/dashboard/:sessionId` — Interviewer brief view
 * - `/interview/:sessionId` — Interviewee review portal
 * - `/guide/:sessionId` — Updated interview guide with feedback
 * 
 * @returns {JSX.Element} The rendered application.
 */
function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/dashboard/:sessionId" element={<InterviewerDashboard />} />
          <Route path="/interview/:sessionId" element={<IntervieweePortal />} />
          <Route path="/guide/:sessionId" element={<InterviewGuide />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;
