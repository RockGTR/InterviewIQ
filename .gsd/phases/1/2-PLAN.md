---
phase: 1
plan: 2
wave: 1
---

# Plan 1.2: React Frontend Scaffold & Amplify Deployment

## Objective
Create the React frontend application with routing structure and deploy to AWS Amplify. This runs in parallel with Plan 1.1 (no dependency). The frontend will serve as the shell for the interviewer dashboard and interviewee portal.

## Context
- .gsd/SPEC.md (UI flows, two-stage workflow)
- .gsd/phases/1/RESEARCH.md (section 1 — Amplify Gen 2)
- .gsd/DECISIONS.md (ADR-001)

## Tasks

<task type="auto">
  <name>Scaffold React app with Vite and project structure</name>
  <files>
    frontend/package.json
    frontend/vite.config.js
    frontend/src/App.jsx
    frontend/src/main.jsx
    frontend/src/index.css
    frontend/src/pages/HomePage.jsx
    frontend/src/pages/InterviewerDashboard.jsx
    frontend/src/pages/IntervieweePortal.jsx
    frontend/src/pages/InterviewGuide.jsx
    frontend/src/components/Layout.jsx
    frontend/src/components/Header.jsx
    frontend/src/services/api.js
    frontend/README.md
  </files>
  <action>
    1. Initialize React app with Vite:
       ```bash
       npm create vite@latest frontend -- --template react
       ```

    2. Install dependencies:
       ```bash
       cd frontend
       npm install react-router-dom aws-amplify @aws-amplify/ui-react
       ```

    3. Create project structure:
       ```
       frontend/
       ├── src/
       │   ├── pages/           # Route pages
       │   │   ├── HomePage.jsx
       │   │   ├── InterviewerDashboard.jsx
       │   │   ├── IntervieweePortal.jsx
       │   │   └── InterviewGuide.jsx
       │   ├── components/      # Shared components
       │   │   ├── Layout.jsx
       │   │   └── Header.jsx
       │   ├── services/        # API client
       │   │   └── api.js
       │   ├── App.jsx          # Router setup
       │   ├── main.jsx         # Entry point
       │   └── index.css        # Global styles + design system
       └── README.md
       ```

    4. Set up React Router with routes:
       - `/` → HomePage (landing, enter company name/URL)
       - `/dashboard/:sessionId` → InterviewerDashboard (view brief)
       - `/interview/:sessionId` → IntervieweePortal (interviewee reviews)
       - `/guide/:sessionId` → InterviewGuide (updated guide with feedback)

    5. Create placeholder pages with proper component structure
       - Each page should have a clear JSDoc comment explaining its purpose
       - Use semantic HTML structure
       - Include loading/error state placeholders

    6. Create `api.js` service module:
       - Stub functions for all backend API calls
       - `createSession(companyName, companyUrl)` → POST
       - `getSession(sessionId)` → GET
       - `submitFeedback(sessionId, corrections, selectedQuestions)` → POST
       - Each function documented with JSDoc

    7. Create `frontend/README.md`:
       - Project overview
       - Setup instructions
       - Available routes
       - Component documentation
       - Development commands

    IMPORTANT:
    - Every component and function must have comprehensive JSDoc documentation
    - Use modern React patterns (functional components, hooks)
    - All interactive elements must have unique IDs for testing
    - Design system tokens in index.css (colors, fonts, spacing)
    - Professional dark theme with vibrant accent colors
  </action>
  <verify>
    cd frontend && npm run build
  </verify>
  <done>
    - Vite build succeeds without errors
    - All 4 routes render placeholder content
    - API service module has all stub functions with JSDoc
    - README.md documents setup and routes
    - Design system tokens defined in index.css
  </done>
</task>

<task type="auto">
  <name>Deploy frontend to AWS Amplify</name>
  <files>
    frontend/amplify.yml
  </files>
  <action>
    1. Create `frontend/amplify.yml` build spec:
       ```yaml
       version: 1
       frontend:
         phases:
           preBuild:
             commands:
               - npm ci
           build:
             commands:
               - npm run build
         artifacts:
           baseDirectory: dist
           files:
             - '**/*'
         cache:
           paths:
             - node_modules/**/*
       ```

    2. Initialize git repo for frontend (if using separate repo)
       OR connect directory to Amplify via CLI:
       ```bash
       # Using Amplify CLI
       amplify init
       amplify add hosting
       amplify publish
       ```

    3. Document deployment process in README.md

    IMPORTANT:
    - Amplify is for frontend hosting ONLY
    - No Amplify backend resources (we use SAM for that)
    - Ensure CORS is configured for API Gateway URL
  </action>
  <verify>
    # Verify Amplify app exists
    aws amplify list-apps --query "apps[?name=='InterviewIQ']"
  </verify>
  <done>
    - Amplify app created and accessible via URL
    - Build spec (amplify.yml) configured
    - Frontend renders at the Amplify URL
    - Deployment documented in README.md
  </done>
</task>

## Success Criteria
- [ ] React app scaffolded with all routes
- [ ] Vite build succeeds
- [ ] Frontend deployed to Amplify
- [ ] All components have JSDoc documentation
- [ ] README.md is comprehensive
