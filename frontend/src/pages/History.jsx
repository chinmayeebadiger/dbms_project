import { Link } from 'react-router-dom'
import RiskBadge from '../components/RiskBadge'
import { mockHistory } from '../types'

export default function History() {
  return <div className="page-stack"><section className="page-intro inline-intro"><div><span className="eyebrow">MIGRATION HISTORY</span><h2>Every review in one place.</h2><p className="lede">A searchable record of analyzed migrations and their risk levels.</p></div><Link className="button primary" to="/analyze">＋ New analysis</Link></section><div className="filter-row"><input aria-label="Search migrations" placeholder="Search migrations" /><select aria-label="Filter by risk"><option>All risk levels</option><option>Critical</option><option>High</option><option>Medium</option><option>Low</option></select></div><section className="panel table-panel"><table><thead><tr><th>Migration</th><th>Reviewed</th><th>Findings</th><th>Risk</th><th>Score</th><th></th></tr></thead><tbody>{mockHistory.map((item) => <tr key={item.id}><td><strong>{item.title}</strong><small>{item.id}</small></td><td>{item.created_at}</td><td>{item.findings_count}</td><td><RiskBadge level={item.risk_level} /></td><td><strong>{item.risk_score}</strong></td><td><Link className="text-link" to={`/history/${item.id}`}>Open →</Link></td></tr>)}</tbody></table></section></div>
}
