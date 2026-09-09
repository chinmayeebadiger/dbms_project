import { Link } from 'react-router-dom'
import { useEffect, useMemo, useState } from 'react'
import RiskBadge from '../components/RiskBadge'
import { mockHistory } from '../types'
import { api } from '../services/api'

export default function History() {
  const [items, setItems] = useState(mockHistory)
  const [search, setSearch] = useState('')
  const [level, setLevel] = useState('')
  useEffect(() => { api.history().then((data) => setItems(data.items || [])).catch(() => {}) }, [])
  const filtered = useMemo(() => items.filter((item) => (!level || item.risk_level === level) && item.title.toLowerCase().includes(search.toLowerCase())), [items, search, level])
  return <div className="page-stack"><section className="page-intro inline-intro"><div><span className="eyebrow">MIGRATION HISTORY</span><h2>Every review in one place.</h2><p className="lede">A searchable record of analyzed migrations and their risk levels.</p></div><Link className="button primary" to="/analyze">＋ New analysis</Link></section><div className="filter-row"><input aria-label="Search migrations" placeholder="Search migrations" value={search} onChange={(e) => setSearch(e.target.value)} /><select aria-label="Filter by risk" value={level} onChange={(e) => setLevel(e.target.value)}><option value="">All risk levels</option><option>Critical</option><option>High</option><option>Medium</option><option>Low</option></select></div><section className="panel table-panel"><table><thead><tr><th>Migration</th><th>Reviewed</th><th>Findings</th><th>Risk</th><th>Score</th><th></th></tr></thead><tbody>{filtered.map((item) => <tr key={item.id}><td><strong>{item.title}</strong><small>{item.id}</small></td><td>{item.created_at}</td><td>{item.findings_count}</td><td><RiskBadge level={item.risk_level} /></td><td><strong>{item.risk_score}</strong></td><td><Link className="text-link" to={`/history/${item.id}`}>Open →</Link></td></tr>)}</tbody></table>{filtered.length === 0 && <div className="status-state empty-state"><strong>No matching migrations.</strong><span>Try a different search or risk level.</span></div>}</section></div>
}
