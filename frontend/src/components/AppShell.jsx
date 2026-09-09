import { NavLink } from 'react-router-dom'

const navigation = [
  { to: '/', label: 'Dashboard', icon: '⌂' },
  { to: '/analyze', label: 'Analyze migration', icon: '⌁' },
  { to: '/history', label: 'Migration history', icon: '◷' },
  { to: '/graph', label: 'Knowledge graph', icon: '✣' },
]

export default function AppShell({ children }) {
  return <div className="app-shell">
    <aside className="sidebar">
      <div className="brand"><span className="brand-mark">MS</span><span><strong>Migration</strong><small>Safety Platform</small></span></div>
      <nav aria-label="Main navigation">
        <p className="nav-label">Workspace</p>
        {navigation.map((item) => <NavLink key={item.to} to={item.to} end={item.to === '/'} className={({ isActive }) => isActive ? 'nav-item active' : 'nav-item'}><span className="nav-icon">{item.icon}</span>{item.label}</NavLink>)}
      </nav>
      <div className="sidebar-footer"><span className="status-dot" />Local analysis mode</div>
    </aside>
    <main className="main-content">
      <header className="topbar"><div><span className="eyebrow">DATABASE SAFETY</span><h1>Migration review workspace</h1></div><div className="topbar-meta"><span className="pill pill-soft">Phase 1 preview</span><span className="avatar">P2</span></div></header>
      <div className="page-content">{children}</div>
    </main>
  </div>
}
