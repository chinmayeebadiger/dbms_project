import { Link } from 'react-router-dom'
import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import RiskBadge from '../components/RiskBadge'
import { mockAnalysis } from '../types'
import { api } from '../services/api'

function getAnalysis() {
  try {
    const saved = sessionStorage.getItem('latestAnalysis')
    return saved ? JSON.parse(saved) : mockAnalysis
  } catch {
    return mockAnalysis
  }
}

export default function Report() {
  const { id } = useParams()
  const [analysis, setAnalysis] = useState(id ? null : getAnalysis())
  const [error, setError] = useState('')
  useEffect(() => {
    if (!id || id.startsWith('demo-')) return
    api.historyItem(id).then(setAnalysis).catch((requestError) => { setError(requestError.message); setAnalysis(getAnalysis()) })
  }, [id])
  if (!analysis) return <div className="status-state"><span className="spinner" />Loading saved report…</div>
  const findings = analysis.findings || []
  const statementCount = analysis.statements?.length || 0
  return <div className="page-stack">
    <div className="breadcrumb"><Link to="/history">Migration history</Link><span>/</span>{analysis.title || 'Untitled migration'}</div>
    <section className="report-header"><div><span className="eyebrow">RISK REPORT · {analysis.migration_id ? 'LIVE ANALYSIS' : 'PREVIEW'}</span><h2>{analysis.title || 'Untitled migration'}</h2><p className="lede">{statementCount} statements reviewed · Results are ready to review</p></div><Link className="button secondary" to="/analyze">New analysis</Link></section>
    <section className="report-summary"><div className="score-ring"><strong>{analysis.overall_score}</strong><span>risk score</span></div><div><RiskBadge level={analysis.risk_level} /><h3>{findings.length ? 'Review recommended' : 'No cataloged risks found'}</h3><p>{findings.length ? 'The migration contains changes that deserve attention before deployment.' : 'The current catalog did not identify a known unsafe pattern.'}</p></div></section>
    {error && <div className="validation-message" role="alert">Could not load the saved report: {error}</div>}
    {analysis.warnings?.length > 0 && <div className="validation-message" role="status"><strong>Parser warnings:</strong> {analysis.warnings.map((warning) => `Line ${warning.line_number}: ${warning.message}`).join(' ')}</div>}
    <section className="panel"><div className="panel-heading"><div><span className="eyebrow">FINDINGS</span><h3>Detected risks</h3></div><span className="muted-note">{findings.length} findings</span></div>{findings.length ? <div className="findings-list">{findings.map((finding) => <article className="finding-card" key={`${finding.operation}-${finding.line_number}`}><div className="finding-top"><span className="line-ref">Line {finding.line_number}</span><RiskBadge level={finding.severity[0] + finding.severity.slice(1).toLowerCase()} /></div><h4>{finding.operation} <span>·</span> {finding.affected_object}</h4><p>{finding.explanation}</p><div className="finding-detail"><strong>Impact</strong><span>{finding.impact}</span></div><div className="finding-detail alternative"><strong>Safer alternative</strong><span>{finding.alternative}</span></div></article>)}</div> : <div className="status-state empty-state"><strong>No findings for this migration.</strong><span>Review the parser warnings or add a supported migration operation.</span></div>}</section>
  </div>
}
