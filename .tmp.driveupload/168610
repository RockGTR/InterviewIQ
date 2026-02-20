/**
 * Header Component — Application navigation bar.
 * 
 * Displays the InterviewIQ logo and navigation links.
 * Uses glassmorphism styling with backdrop blur.
 * 
 * @module Header
 */

import { Link, useLocation } from 'react-router-dom';

/**
 * Header navigation component.
 * 
 * @returns {JSX.Element} The rendered header.
 */
function Header() {
    const location = useLocation();
    const isHome = location.pathname === '/';

    return (
        <header style={styles.header}>
            <div className="container" style={styles.container}>
                <Link to="/" style={styles.logo} id="header-logo">
                    <span style={styles.logoIcon}>⚡</span>
                    <span style={styles.logoText}>InterviewIQ</span>
                </Link>

                <nav style={styles.nav}>
                    {!isHome && (
                        <Link to="/" style={styles.navLink} id="nav-home">
                            ← New Session
                        </Link>
                    )}
                    <span style={styles.badge}>
                        AI-Powered
                    </span>
                </nav>
            </div>
        </header>
    );
}

/** @type {Object} Component styles */
const styles = {
    header: {
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        height: 'var(--header-height)',
        background: 'var(--bg-glass)',
        backdropFilter: 'blur(16px)',
        borderBottom: '1px solid var(--border-primary)',
        zIndex: 100,
        display: 'flex',
        alignItems: 'center',
    },
    container: {
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        width: '100%',
    },
    logo: {
        display: 'flex',
        alignItems: 'center',
        gap: 'var(--space-2)',
        textDecoration: 'none',
        color: 'var(--text-primary)',
    },
    logoIcon: {
        fontSize: 'var(--text-xl)',
    },
    logoText: {
        fontSize: 'var(--text-lg)',
        fontWeight: 700,
        background: 'linear-gradient(135deg, var(--color-primary-light), var(--color-accent-light))',
        WebkitBackgroundClip: 'text',
        WebkitTextFillColor: 'transparent',
    },
    nav: {
        display: 'flex',
        alignItems: 'center',
        gap: 'var(--space-4)',
    },
    navLink: {
        fontSize: 'var(--text-sm)',
        color: 'var(--text-secondary)',
        textDecoration: 'none',
        transition: 'color var(--transition-fast)',
    },
    badge: {
        padding: 'var(--space-1) var(--space-3)',
        fontSize: 'var(--text-xs)',
        fontWeight: 600,
        borderRadius: 'var(--radius-full)',
        background: 'var(--color-primary-glow)',
        color: 'var(--color-primary-light)',
        textTransform: 'uppercase',
        letterSpacing: '0.05em',
    },
};

export default Header;
