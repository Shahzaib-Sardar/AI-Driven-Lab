const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:5000/api'

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { 
      'Content-Type': 'application/json',
      ...(options.headers || {}),
      ...(localStorage.getItem('token') ? { 'Authorization': `Bearer ${localStorage.getItem('token')}` } : {})
    },
    ...options,
  })

  if (!response.ok) {
    const body = await response.json().catch(() => ({}))
    throw new Error(body.error || 'Request failed')
  }

  return response.json().catch(() => ({}))
}

export const api = {
  login: (email, password) => request('/auth/login', { method: 'POST', body: JSON.stringify({ email, password }) }),
  signup: (email, password, full_name) => request('/auth/signup', { method: 'POST', body: JSON.stringify({ email, password, full_name }) }),
  getSummary: () => request('/dashboard/summary'),
  listTransactions: () => request('/transactions'),
  createTransaction: (payload) => request('/transactions', { method: 'POST', body: JSON.stringify(payload) }),
  listCategories: () => request('/categories'),
}
