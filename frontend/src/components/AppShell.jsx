import { NavLink } from 'react-router-dom'

const navigation = [
  { to: '/', label: 'Dashboard', icon: '⌂' },
  { to: '/analyze', label: 'Analyze migration', icon: '⌁' },
  { to: '/history', label: 'Migration history', icon: '◷' },
  { to: '/graph', label: 'Knowledge graph', icon: '✣' },
]

export default function AppShell({ children }) {
  return <div className="app-shell">
    <header className="topbar">
      <div className="brand"><span className="brand-mark">MS</span><span><strong>Migration Safety</strong><small>Database review workspace</small></span></div>
      <nav className="top-navigation" aria-label="Main navigation">
        {navigation.map((item) => <NavLink key={item.to} to={item.to} end={item.to === '/'} className={({ isActive }) => isActive ? 'nav-item active' : 'nav-item'}><span className="nav-icon">{item.icon}</span>{item.label}</NavLink>)}
      </nav>
      <div className="topbar-tools"><label className="global-search"><span>⌕</span><input aria-label="Search workspace" placeholder="Search" /></label><span className="pill pill-soft">Local mode</span><span className="avatar">P2</span></div>
    </header>
    <main className="main-content"><div className="page-content">{children}</div></main>
  </div>
}
