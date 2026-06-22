const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:5000/api'

function buildQuery(params = {}) {
  const searchParams = new URLSearchParams()

  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      searchParams.set(key, value)
    }
  })

  const query = searchParams.toString()
  return query ? `?${query}` : ''
}

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
  getPreferences: () => request('/auth/preferences'),
  setPreferences: (payload) => request('/auth/preferences', { method: 'POST', body: JSON.stringify(payload) }),
  getSummary: () => request('/dashboard/summary'),
  listTransactions: (params = {}) => request(`/transactions${buildQuery(params)}`),
  createTransaction: (payload) => request('/transactions', { method: 'POST', body: JSON.stringify(payload) }),
  updateTransaction: (transactionId, payload) => request(`/transactions/${transactionId}`, { method: 'PUT', body: JSON.stringify(payload) }),
  deleteTransaction: (transactionId) => request(`/transactions/${transactionId}`, { method: 'DELETE' }),
  listCategories: () => request('/categories'),
  createCategory: (payload) => request('/categories', { method: 'POST', body: JSON.stringify(payload) }),
  deleteCategory: (categoryId) => request(`/categories/${categoryId}`, { method: 'DELETE' }),
  listBudgets: () => request('/budgets'),
  setBudget: (payload) => request('/budgets', { method: 'POST', body: JSON.stringify(payload) }),
  getMonthlyReport: () => request('/reports/monthly'),
  generateMonthlySummary: (payload = {}) => request('/reports/ai-summary', { method: 'POST', body: JSON.stringify(payload) }),
}
