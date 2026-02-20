# InterviewIQ Frontend

React + Vite application for the InterviewIQ interview intelligence system.

## Setup

```bash
npm install
npm run dev        # → http://localhost:5173
npm run build      # → dist/
```

## Pages

| Route | Component | Purpose |
|-------|-----------|---------|
| `/` | `HomePage` | Company input form, feature grid, hero section |
| `/dashboard/:id` | `InterviewerDashboard` | View AI-generated brief, questions, company profile |
| `/interview/:id` | `IntervieweePortal` | Review AI findings, correct inaccuracies, select questions |
| `/guide/:id` | `InterviewGuide` | Updated guide with interviewee feedback incorporated |

## Components

- **Header** — Navigation bar with glassmorphism, gradient logo, active route highlighting
- **Layout** — Page wrapper with header and padded content area

## API Service

`src/services/api.js` — Fetch-based client for all backend endpoints.

```javascript
import api from '../services/api';

// Set API base URL (update after deployment)
// Edit the API_BASE constant in api.js

const session = await api.createSession({ companyName: 'GridFlex Energy' });
const data = await api.getSession(sessionId);
```

## Design System

CSS variables defined in `src/index.css`:

- **Theme**: Dark (`--bg-primary: #0a0a0f`)
- **Accent**: Gradient purple-cyan (`--accent-primary: #6366f1`)
- **Font**: System sans-serif stack
- **Effects**: Glassmorphism, gradient borders, hover animations

## Deploy

Build spec in `amplify.yml` for AWS Amplify:
```yaml
preBuild: npm ci
build: npm run build
output: dist
```
