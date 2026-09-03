import Header from './Header'
import Sidebar from './Sidebar'

/**
 * Layout — wraps the entire application with header + sidebar + main content area.
 * @param {string}   activePage  - currently active page key
 * @param {Function} onNavigate  - navigation callback
 * @param {ReactNode} children   - page content rendered in the main area
 */
export default function Layout({ activePage, onNavigate, children }) {
  return (
    <div className="flex flex-col h-screen overflow-hidden"
      style={{ background: 'var(--bg-primary)' }}
    >
      {/* Top header — full width */}
      <Header />

      {/* Body: sidebar + main content */}
      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar — fixed width, scrolls independently */}
        <Sidebar activePage={activePage} onNavigate={onNavigate} />

        {/* Main content area — scrollable */}
        <main
          className="flex-1 overflow-y-auto"
          style={{ background: 'var(--bg-primary)' }}
          id="main-content"
        >
          {/* Mesh gradient background overlay */}
          <div
            className="fixed inset-0 pointer-events-none"
            style={{
              background:
                'radial-gradient(at 20% 10%, rgba(99,102,241,0.07) 0, transparent 50%),' +
                'radial-gradient(at 80% 80%, rgba(34,211,238,0.05) 0, transparent 50%)',
              zIndex: 0,
            }}
          />
          <div className="relative z-10">
            {children}
          </div>
        </main>
      </div>
    </div>
  )
}
