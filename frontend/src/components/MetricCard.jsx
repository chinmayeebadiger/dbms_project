export default function MetricCard({ label, value, hint, tone = 'neutral' }) {
  return <div className={`metric-card ${tone}`}><span className="metric-label">{label}</span><strong>{value}</strong><span className="metric-hint">{hint}</span></div>
}
