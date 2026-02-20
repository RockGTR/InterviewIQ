/**
 * Layout Component — Page wrapper with header and content area.
 * 
 * Provides consistent page structure with the navigation header
 * and a padded content area below.
 * 
 * @module Layout
 */

import Header from './Header';

/**
 * Layout wrapper component.
 * 
 * @param {Object} props
 * @param {React.ReactNode} props.children - Page content to render.
 * @returns {JSX.Element} The rendered layout.
 */
function Layout({ children }) {
    return (
        <div style={styles.layout}>
            <Header />
            <main style={styles.main}>
                {children}
            </main>
        </div>
    );
}

/** @type {Object} Component styles */
const styles = {
    layout: {
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
    },
    main: {
        flex: 1,
        paddingTop: 'calc(var(--header-height) + var(--space-8))',
        paddingBottom: 'var(--space-16)',
    },
};

export default Layout;
