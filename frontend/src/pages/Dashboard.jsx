import { Link } from 'react-router-dom'
import MetricCard from '../components/MetricCard'
import RiskBadge from '../components/RiskBadge'
import { mockHistory } from '../types'

export default function Dashboard() {
  return <div className="page-stack">
    <section className="hero-row"><div><span className="eyebrow">OVERVIEW</span><h2>Know the risk before you migrate.</h2><p className="lede">Review SQL changes, trace their impact, and give your team a safer path to deployment.</p></div><Link className="button primary" to="/analyze">Analyze a migration <span>→</span></Link></section>
    <section className="metrics-grid"><MetricCard label="Analyses this week" value="14" hint="↑ 4 from last week" tone="blue" /><MetricCard label="Average risk score" value="46" hint="Across recent reviews" tone="amber" /><MetricCard label="Critical findings" value="03" hint="Require attention" tone="red" /></section>
    <section className="content-grid"><div className="panel"><div className="panel-heading"><div><span className="eyebrow">RECENT REVIEWS</span><h3>Migration history</h3></div><Link to="/history" className="text-link">View all →</Link></div><div className="history-list">{mockHistory.map((item) => <Link to={`/history/${item.id}`} className="history-row" key={item.id}><span className="history-icon">⌁</span><span className="history-main"><strong>{item.title}</strong><small>{item.created_at} · {item.findings_count} findings</small></span><span className="history-score"><RiskBadge level={item.risk_level} /><strong>{item.risk_score}</strong></span></Link>)}</div></div><div className="panel insight-panel"><span className="eyebrow">SAFETY NOTE</span><h3>Destructive changes deserve a second look.</h3><p>Dropping a column can break both stored data and application queries. A staged deprecation is usually safer.</p><Link to="/graph" className="text-link">Explore the knowledge graph →</Link></div></section>
  </div>
}
