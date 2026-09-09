export function LoadingState({ label = 'Loading' }) {
  return <div className="status-state" role="status"><span className="spinner" aria-hidden="true" />{label}</div>
}

export function EmptyState({ title, message, action }) {
  return <div className="status-state empty-state"><strong>{title}</strong><span>{message}</span>{action}</div>
}

export function ErrorState({ title = 'Something went wrong', message }) {
  return <div className="status-state error-state" role="alert"><strong>{title}</strong><span>{message}</span></div>
}
