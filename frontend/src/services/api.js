const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000').replace(/\/$/, '')

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: { ...(options.body instanceof FormData ? {} : { 'Content-Type': 'application/json' }), ...options.headers },
    ...options,
  })

  if (!response.ok) {
    let detail = `Request failed with status ${response.status}`
    try {
      const payload = await response.json()
      detail = payload.detail || detail
    } catch {
      // Keep the status-based message when the server does not return JSON.
    }
    throw new Error(detail)
  }
  return response.json()
}

export const api = {
  baseUrl: API_BASE_URL,
  health: () => request('/health'),
  analyze: (payload) => request('/analyze', { method: 'POST', body: JSON.stringify(payload) }),
  analyzeFile: (file, title = '') => {
    const form = new FormData()
    form.append('file', file)
    form.append('title', title)
    return request('/analyze-file', { method: 'POST', body: form })
  },
  history: (query = '') => request(`/history${query ? `?${query}` : ''}`),
  historyItem: (id) => request(`/history/${id}`),
  graph: (id) => request(`/graph/${id}`),
  stats: () => request('/stats'),
}
