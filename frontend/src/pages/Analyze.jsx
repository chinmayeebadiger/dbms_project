import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { api } from '../services/api'

export default function Analyze() {
  const navigate = useNavigate()
  const [sql, setSql] = useState('ALTER TABLE customers DROP COLUMN email;\nUPDATE customers SET active = false;')
  const [title, setTitle] = useState('Customer table cleanup')
  const [fileName, setFileName] = useState('')
  const [isSubmitting, setSubmitting] = useState(false)
  const [message, setMessage] = useState('')

  async function submit(event) {
    event.preventDefault()
    if (!sql.trim() && !fileName) { setMessage('Add a migration query or choose a .sql file before analyzing.'); return }
    setSubmitting(true); setMessage('')
    try {
      const result = fileName ? await api.analyzeFile(event.currentTarget.querySelector('input[type="file"]').files[0], title) : await api.analyze({ title, sql_text: sql })
      sessionStorage.setItem('latestAnalysis', JSON.stringify({ ...result, title }))
      navigate('/report')
    } catch (error) {
      setMessage(error.message || 'The analysis service could not be reached.')
    } finally {
      setSubmitting(false)
    }
  }

  return <div className="page-stack narrow-page"><section className="page-intro"><span className="eyebrow">ANALYZE MIGRATION</span><h2>Check a migration before it reaches production.</h2><p className="lede">Paste SQL or upload a migration file. The analyzer will identify risky operations and explain safer alternatives.</p></section><form className="panel form-panel" onSubmit={submit}><label htmlFor="title">Migration title<span className="required">*</span></label><input id="title" value={title} onChange={(e) => setTitle(e.target.value)} placeholder="e.g. Customer table cleanup" /><div className="label-row"><label htmlFor="sql">Migration SQL<span className="required">*</span></label><span className="field-hint">PostgreSQL · SQL only</span></div><textarea id="sql" value={sql} onChange={(e) => setSql(e.target.value)} rows="9" spellCheck="false" /><div className="upload-row"><label className="upload-control"><span>＋</span>{fileName || 'Upload .sql file'}<input type="file" accept=".sql,text/sql" onChange={(e) => setFileName(e.target.files?.[0]?.name || '')} /></label><span className="field-hint">Max 1 MB</span></div>{message && <p className={message.startsWith('Preview') ? 'success-message' : 'validation-message'} role="status">{message}</p>}<div className="form-footer"><span className="muted-note">Your SQL is analyzed only and never executed.</span><button className="button primary" disabled={isSubmitting}>{isSubmitting ? 'Analyzing…' : 'Analyze migration →'}</button></div></form><div className="preview-link">Using preview data for Phase 1? <Link to="/report">Open sample risk report →</Link></div></div>
}
