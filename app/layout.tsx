import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Calendar Monitor | Flock-Off',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body style={{
        margin: 0,
        fontFamily: "'Segoe UI', system-ui, sans-serif",
        background: '#0a0a0f',
        color: '#e8e8f0',
        lineHeight: 1.6,
      }}>
        <style>{`
          *, *::before, *::after { box-sizing: border-box; }
          nav a { color: #7a7a9a; text-decoration: none; font-size: 0.9rem; transition: color 0.2s; }
          nav a:hover { color: #e8e8f0; }
          .nav-monitor { color: #e63946 !important; font-weight: 600; }
          .nav-donate {
            color: #e63946 !important;
            border: 1px solid #e63946;
            padding: 0.5rem 1.2rem;
            border-radius: 6px;
            font-weight: 600;
          }
          .nav-donate:hover { background: #e63946 !important; color: #fff !important; }
          .nav-cta {
            background: #e63946;
            color: #fff !important;
            padding: 0.5rem 1.2rem;
            border-radius: 6px;
            font-weight: 600;
          }
          .nav-cta:hover { background: #c1121f !important; }
          .nav-links { list-style: none; display: flex; gap: 2rem; margin: 0; padding: 0; align-items: center; }
          .nav-links li { display: flex; align-items: center; }
          @media (max-width: 768px) {
            .nav-links { display: none; }
          }
        `}</style>

        <nav style={{
          position: 'fixed',
          top: 0, left: 0, right: 0,
          zIndex: 100,
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          padding: '1rem 1.5rem',
          background: 'rgba(10, 10, 15, 0.95)',
          backdropFilter: 'blur(12px)',
          borderBottom: '1px solid #1e1e2e',
        }}>
          <a href="/index.html" style={{ display: 'flex', alignItems: 'center' }}>
            <img src="/logo.png" alt="Flock-Off" style={{ height: 28 }} />
          </a>

          <ul className="nav-links">
            <li><a href="/index.html#problem">The Problem</a></li>
            <li><a href="/index.html#action">Take Action</a></li>
            <li><a href="/chapters.html">Chapters</a></li>
            <li><a href="/about.html">About</a></li>
            <li><a href="/monitor" className="nav-monitor">Calendar Monitor</a></li>
            <li><a href="/donate.html" className="nav-donate">Donate</a></li>
            <li><a href="/index.html#join" className="nav-cta">Join the Fight</a></li>
          </ul>
        </nav>

        <main style={{
          maxWidth: 1100,
          margin: '0 auto',
          padding: '80px 16px 48px',
        }}>
          {children}
        </main>
      </body>
    </html>
  )
}
