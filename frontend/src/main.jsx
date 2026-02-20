/**
 * Application entry point.
 * 
 * Renders the root React component into the DOM.
 * Imports global styles and design system tokens.
 * 
 * @module main
 */

import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import './index.css';
import App from './App.jsx';

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
