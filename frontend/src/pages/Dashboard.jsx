import { useEffect, useMemo, useState } from 'react'
import { io } from 'socket.io-client'
import { useNavigate } from 'react-router-dom'
import { api } from '../api'
import { useAuth } from '../context/AuthContext'
import '../styles.css'

const currentMonth = new Date().toISOString().slice(0, 7)

const defaultTransactionForm = {
  type: 'expense',
  amount: '',
  category_id: '',
  transaction_date: new Date().toISOString().slice(0, 10),
  note: '',
  payment_method: '',
}

const defaultCategoryForm = {
  name: '',
  type: 'expense',
}

const defaultBudgetForm = {
  month: currentMonth,
  overall: '',
  byCategory: '',
  carry_forward: false,
}

function formatCurrency(value) {
  const amount = Number(value || 0)
  const curr = (typeof window !== 'undefined' && localStorage.getItem('currency')) || 'USD'
  try {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: String(curr || 'USD'),
      maximumFractionDigits: 2,
    }).format(amount)
  } catch (err) {
    return String(amount)
  }
}

function formatDate(value) {
  if (!value) return '-'
  const parsed = new Date(value)
  return Number.isNaN(parsed.getTime()) ? value : parsed.toLocaleDateString()
}

function monthKey(value) {
  return value ? String(value).slice(0, 7) : 'unknown'
}

function monthLabel(value) {
  if (value === 'unknown') return 'Unknown'

  const parsed = new Date(`${value}-01T00:00:00`)
  return Number.isNaN(parsed.getTime())
    ? value
    : parsed.toLocaleDateString(undefined, { month: 'short', year: 'numeric' })
}

function parseBudgetEntries(input) {
  const entries = {}

  input
    .split(',')
    .map((item) => item.trim())
    .filter(Boolean)
    .forEach((item) => {
      const [rawName, rawValue] = item.split('=')
      if (!rawName || !rawValue) return
      const name = rawName.trim()
      const amount = Number(rawValue.trim())
      if (name && Number.isFinite(amount) && amount >= 0) {
        entries[name] = amount
      }
    })

  return entries
}

function getUserInitials(user) {
  const fullName = String(user?.full_name || '').trim()
  if (fullName) {
    const parts = fullName.split(/\s+/).filter(Boolean)
    if (parts.length >= 2) {
      return `${parts[0][0]}${parts[1][0]}`.toUpperCase()
    }
    return fullName.slice(0, 2).toUpperCase()
  }

  const email = String(user?.email || '').trim()
  if (email) {
    return email.slice(0, 2).toUpperCase()
  }

  return 'U'
}

export default function Dashboard() {
  const [summary, setSummary] = useState(null)
  const [transactions, setTransactions] = useState([])
  const [categories, setCategories] = useState([])
  const [budgets, setBudgets] = useState({})
  const [monthlyReport, setMonthlyReport] = useState(null)
  const [monthlySummary, setMonthlySummary] = useState(null)
  const [transactionForm, setTransactionForm] = useState(defaultTransactionForm)
  const [categoryForm, setCategoryForm] = useState(defaultCategoryForm)
  const [budgetForm, setBudgetForm] = useState(defaultBudgetForm)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [loading, setLoading] = useState(true)
  const [generatingSummary, setGeneratingSummary] = useState(false)
  const [savingBudget, setSavingBudget] = useState(false)
  const [addingCategory, setAddingCategory] = useState(false)
  const [deletingTransactionId, setDeletingTransactionId] = useState(null)
  const [search, setSearch] = useState('')
  const [txTypeFilter, setTxTypeFilter] = useState('all')
  const { user, logout, login } = useAuth()
  const navigate = useNavigate()

  const categoryMap = useMemo(
    () => new Map(categories.map((category) => [String(category.id), category])),
    [categories],
  )

  const expenseCategories = useMemo(
    () => categories.filter((category) => category.type === transactionForm.type),
    [categories, transactionForm.type],
  )

  const selectedBudget = budgets?.[budgetForm.month] || null

  const filteredTransactions = useMemo(() => {
    return transactions.filter((transaction) => {
      const matchesType = txTypeFilter === 'all' || transaction.type === txTypeFilter
      const haystack = [transaction.note, transaction.payment_method, transaction.category_name]
        .join(' ')
        .toLowerCase()
      const matchesSearch = !search.trim() || haystack.includes(search.trim().toLowerCase())
      return matchesType && matchesSearch
    })
  }, [transactions, search, txTypeFilter])

  const expenseStats = useMemo(() => {
    const grouped = summary?.expenses_by_category || {}
    const ranked = Object.entries(grouped)
      .map(([categoryId, amount]) => ({
        categoryId,
        amount: Number(amount || 0),
        name: categoryMap.get(String(categoryId))?.name || 'Uncategorized',
      }))
      .sort((left, right) => right.amount - left.amount)

    return ranked
  }, [summary, categoryMap])

  const topExpenseCategory = expenseStats[0]
  const totalIncome = Number(summary?.income || 0)
  const totalExpenses = Number(summary?.expenses || 0)
  const balance = Number(summary?.balance || 0)
  const savingsRate = totalIncome > 0 ? ((balance / totalIncome) * 100).toFixed(1) : '0.0'

  const monthlyTrend = useMemo(() => {
    const grouped = new Map()

    transactions.forEach((transaction) => {
      const key = monthKey(transaction.transaction_date)
      const bucket = grouped.get(key) || { month: key, income: 0, expense: 0 }

      if (transaction.type === 'income') {
        bucket.income += Number(transaction.amount || 0)
      } else if (transaction.type === 'expense') {
        bucket.expense += Number(transaction.amount || 0)
      }

      grouped.set(key, bucket)
    })

    return Array.from(grouped.values())
      .sort((left, right) => left.month.localeCompare(right.month))
      .slice(-6)
  }, [transactions])

  const [currency, setCurrency] = useState(() => {
    try {
      const saved = localStorage.getItem('currency')
      return (user?.currency || saved || 'USD').toUpperCase()
    } catch (err) {
      return 'USD'
    }
  })

  useEffect(() => {
    if (user?.currency) {
      const c = String(user.currency || 'USD').toUpperCase()
      setCurrency(c)
      localStorage.setItem('currency', c)
    }
  }, [user])

  async function handleCurrencyChange(event) {
    const newCurrency = String(event.target.value || 'USD').toUpperCase()
    setCurrency(newCurrency)
    try {
      localStorage.setItem('currency', newCurrency)
      if (user?.id) {
        await api.setPreferences({ currency: newCurrency })
        const token = localStorage.getItem('token')
        const updatedUser = { ...user, currency: newCurrency }
        localStorage.setItem('user', JSON.stringify(updatedUser))
        if (token) login(updatedUser, token)
      }
      setSuccess(`Currency set to ${newCurrency}`)
    } catch (err) {
      setError(err.message || 'Could not set currency')
    }
  }

  const budgetStatus = useMemo(() => {
    if (!selectedBudget?.overall) return null

    const overall = Number(selectedBudget.overall || 0)
    const usage = overall > 0 ? Math.min((totalExpenses / overall) * 100, 999) : 0

    return {
      overall,
      usage,
      isOverBudget: totalExpenses > overall,
    }
  }, [selectedBudget, totalExpenses])

  async function loadData() {
    setLoading(true)
    try {
      const [summaryData, txData, categoryData, budgetData, reportData] = await Promise.all([
        api.getSummary(),
        api.listTransactions(),
        api.listCategories(),
        api.listBudgets(),
        api.getMonthlyReport(),
      ])

      const items = txData.items || []
      const categoriesList = categoryData.items || []
      const categoryLookup = new Map(categoriesList.map((category) => [category.id, category]))

      setSummary(summaryData)
      setTransactions(
        items.map((transaction) => ({
          ...transaction,
          category_name: categoryLookup.get(transaction.category_id)?.name || transaction.category_name || 'Uncategorized',
        })),
      )
      setCategories(categoriesList)
      setBudgets(budgetData || {})
      setMonthlyReport(reportData)
      setError('')
    } catch (err) {
      setError(err.message || 'Unable to load dashboard data')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData()
  }, [])

  // Realtime updates: listen for server-sent events and refresh dashboard
  useEffect(() => {
    const socketUrl = import.meta.env.VITE_SOCKET_IO_URL || 'http://localhost:5000'
    const socket = io(socketUrl)

    socket.on('connect', () => {
      // console.debug('socket connected')
    })

    const refresh = () => {
      loadData().catch(() => {})
    }

    socket.on('transaction_created', refresh)
    socket.on('transaction_updated', refresh)
    socket.on('transaction_deleted', refresh)
    socket.on('category_created', refresh)
    socket.on('category_updated', refresh)
    socket.on('category_deleted', refresh)

    return () => {
      socket.disconnect()
    }
  }, [])

  async function handleTransactionSubmit(event) {
    event.preventDefault()
    setError('')
    setSuccess('')

    try {
      await api.createTransaction({
        ...transactionForm,
        amount: Number(transactionForm.amount),
        category_id: transactionForm.category_id ? Number(transactionForm.category_id) : null,
      })
      setTransactionForm((current) => ({
        ...defaultTransactionForm,
        type: current.type,
        category_id: '',
      }))
      setSuccess('Transaction added successfully.')
      await loadData()
    } catch (err) {
      setError(err.message || 'Could not add transaction')
    }
  }

  async function handleDeleteTransaction(transactionId) {
    setDeletingTransactionId(transactionId)
    setError('')
    setSuccess('')
    try {
      await api.deleteTransaction(transactionId)
      setSuccess('Transaction removed.')
      await loadData()
    } catch (err) {
      setError(err.message || 'Could not delete transaction')
    } finally {
      setDeletingTransactionId(null)
    }
  }

  async function handleCategorySubmit(event) {
    event.preventDefault()
    setError('')
    setSuccess('')
    setAddingCategory(true)
    try {
      await api.createCategory(categoryForm)
      setCategoryForm(defaultCategoryForm)
      setSuccess('Category created.')
      await loadData()
    } catch (err) {
      setError(err.message || 'Could not create category')
    } finally {
      setAddingCategory(false)
    }
  }

  async function handleDeleteCategory(categoryId) {
    setError('')
    setSuccess('')
    try {
      await api.deleteCategory(categoryId)
      setSuccess('Category deleted.')
      await loadData()
    } catch (err) {
      setError(err.message || 'Could not delete category')
    }
  }

  async function handleBudgetSubmit(event) {
    event.preventDefault()
    setError('')
    setSuccess('')
    setSavingBudget(true)

    try {
      await api.setBudget({
        month: budgetForm.month,
        overall: budgetForm.overall === '' ? null : Number(budgetForm.overall),
        by_category: parseBudgetEntries(budgetForm.byCategory),
        carry_forward: budgetForm.carry_forward,
      })
      setSuccess(`Budget saved for ${budgetForm.month}.`)
      await loadData()
    } catch (err) {
      setError(err.message || 'Could not save budget')
    } finally {
      setSavingBudget(false)
    }
  }

  async function handleGenerateMonthlySummary() {
    setError('')
    setSuccess('')
    setGeneratingSummary(true)

    try {
      const result = await api.generateMonthlySummary({ month: currentMonth })
      setMonthlySummary(result)
      setSuccess(`AI summary generated for ${monthLabel(result.month || currentMonth)}.`)
    } catch (err) {
      setError(err.message || 'Could not generate monthly summary')
    } finally {
      setGeneratingSummary(false)
    }
  }

  function handleLogout() {
    logout()
    navigate('/login')
  }

  function exportCsv() {
    window.location.href = 'http://localhost:5000/api/reports/export/csv'
  }

  return (
    <div className="dashboard-shell">
      <div className="dashboard-bg" />
      <header className="dashboard-header">
        <div>
          <p className="eyebrow">Professional expense intelligence</p>
          <h1>Expense Tracker</h1>
          <p className="dashboard-subtitle">
            Track cash flow, manage budgets, and review spending patterns from one clean workspace.
          </p>
        </div>
        <div className="header-actions">
          <div className="user-pill">
            <span className="user-avatar" aria-hidden="true">
              {getUserInitials(user)}
            </span>
            <div>
              <strong>{user?.full_name || 'Account holder'}</strong>
              <span>{user?.email}</span>
            </div>
          </div>
          <label style={{ margin: '0 12px' }}>
            <select value={currency} onChange={handleCurrencyChange} aria-label="Currency selector">
              <option value="USD">USD</option>
              <option value="EUR">EUR</option>
              <option value="GBP">GBP</option>
              <option value="JPY">JPY</option>
              <option value="CAD">CAD</option>
              <option value="AUD">AUD</option>
              <option value="PKR">PKR</option>
            </select>
          </label>
          <button onClick={handleLogout} className="ghost-button">
            Logout
          </button>
        </div>
      </header>

      <main className="dashboard-content">
        {loading && <div className="loading-panel">Loading your financial workspace...</div>}
        {error && <div className="feedback error-state">{error}</div>}
        {success && <div className="feedback success-state">{success}</div>}

        <section className="hero-grid">
          <article className="hero-card accent-card">
            <span className="card-kicker">Monthly snapshot</span>
            <div className="metric-row">
              <div>
                <p className="metric-label">Balance</p>
                <h2>{formatCurrency(balance)}</h2>
              </div>
              <div className="metric-chip positive">{savingsRate}% saved</div>
            </div>
            <p className="metric-copy">
              Income and expenses are summarized automatically with a bias toward fast decision making.
            </p>
          </article>

          <article className="hero-card">
            <span className="card-kicker">Income</span>
            <h3>{formatCurrency(totalIncome)}</h3>
            <p className="metric-copy">{monthlyReport?.total || transactions.length} recorded activity items.</p>
          </article>

          <article className="hero-card">
            <span className="card-kicker">Expenses</span>
            <h3>{formatCurrency(totalExpenses)}</h3>
            <p className="metric-copy">
              {topExpenseCategory
                ? `Top category: ${topExpenseCategory.name} (${formatCurrency(topExpenseCategory.amount)})`
                : 'No expense data yet.'}
            </p>
          </article>
        </section>

        <section className="summary-grid">
          <article className="summary-card">
            <span>Net position</span>
            <strong>{formatCurrency(balance)}</strong>
            <p>Income minus expenses for the current dataset.</p>
          </article>
          <article className="summary-card">
            <span>Transactions</span>
            <strong>{transactions.length}</strong>
            <p>All recorded entries loaded from the API.</p>
          </article>
          <article className="summary-card">
            <span>Categories</span>
            <strong>{categories.length}</strong>
            <p>Reusable income and expense buckets.</p>
          </article>
          <article className="summary-card">
            <span>Monthly report</span>
            <strong>{monthlyReport?.total ?? 0}</strong>
            <p>Quick view of exported and tracked activity.</p>
          </article>
        </section>

        <section className="analytics-grid">
          <article className="panel-card analytics-card">
            <div className="panel-heading">
              <div>
                <span className="card-kicker">Analytics</span>
                <h2>Monthly trend</h2>
              </div>
            </div>

            {monthlyTrend.length === 0 ? (
              <p className="empty-state">Add transactions across a few months to reveal trend lines.</p>
            ) : (
              <div className="trend-list">
                {monthlyTrend.map((item) => {
                  const total = item.income + item.expense
                  const incomeShare = total > 0 ? (item.income / total) * 100 : 0
                  const expenseShare = total > 0 ? (item.expense / total) * 100 : 0

                  return (
                    <div className="trend-item" key={item.month}>
                      <div className="trend-meta">
                        <strong>{monthLabel(item.month)}</strong>
                        <span>{formatCurrency(item.net ?? item.income - item.expense)}</span>
                      </div>
                      <div className="trend-bars">
                        <div className="trend-bar income" style={{ width: `${incomeShare}%` }} />
                        <div className="trend-bar expense" style={{ width: `${expenseShare}%` }} />
                      </div>
                      <div className="trend-footnote">
                        <span>{formatCurrency(item.income)} in</span>
                        <span>{formatCurrency(item.expense)} out</span>
                      </div>
                    </div>
                  )
                })}
              </div>
            )}
          </article>

          <article className="panel-card analytics-card">
            <div className="panel-heading">
              <div>
                <span className="card-kicker">Executive view</span>
                <h2>Actionable insights</h2>
              </div>
            </div>

            <div className="insight-stack">
              <div className="insight-callout">
                <span>Budget position</span>
                <strong>
                  {budgetStatus ? `${budgetStatus.usage.toFixed(0)}% used` : 'Set a monthly budget'}
                </strong>
                <p>
                  {budgetStatus
                    ? budgetStatus.isOverBudget
                      ? 'You are currently over budget for the selected month.'
                      : 'You still have room left in your current monthly plan.'
                    : 'Use the budget planner to compare planned spend against actual spend.'}
                </p>
              </div>

              <div className="insight-callout subdued">
                <span>Spending concentration</span>
                <strong>{topExpenseCategory?.name || 'No expenses yet'}</strong>
                <p>
                  {topExpenseCategory
                    ? `${formatCurrency(topExpenseCategory.amount)} is flowing into your top category.`
                    : 'Once expenses arrive, the app will surface concentration risk automatically.'}
                </p>
              </div>

              <div className="insight-callout subdued">
                <span>Trend note</span>
                <strong>{transactions.length > 3 ? 'Enough data for pattern review' : 'Build a richer history'}</strong>
                <p>
                  Keep logging daily transactions to unlock better trend comparisons and budget forecasting.
                </p>
              </div>

                <div className="insight-callout ai-summary-callout">
                  <div className="insight-row ai-summary-header">
                    <div>
                      <span>AI monthly summary</span>
                      <strong>
                        {monthlySummary
                          ? `Generated for ${monthLabel(monthlySummary.month || currentMonth)}`
                          : 'Ask the assistant to draft a spending review'}
                      </strong>
                    </div>
                    <button
                      type="button"
                      className="ghost-button compact"
                      onClick={handleGenerateMonthlySummary}
                      disabled={generatingSummary}
                    >
                      {generatingSummary ? 'Generating...' : 'Generate'}
                    </button>
                  </div>

                  {monthlySummary ? (
                    <div className="ai-summary-body">
                      <p>{monthlySummary.summary}</p>
                      <div className="ai-summary-meta">
                        <span className="pill muted">
                          {monthlySummary.source === 'llm' ? 'AI generated' : 'Local fallback'}
                        </span>
                        <span className="pill muted">{monthLabel(monthlySummary.month || currentMonth)}</span>
                      </div>
                      {monthlySummary.recommendations?.length ? (
                        <ul className="ai-summary-list">
                          {monthlySummary.recommendations.map((item) => (
                            <li key={item}>{item}</li>
                          ))}
                        </ul>
                      ) : null}
                    </div>
                  ) : (
                    <p>
                      Generate a concise monthly finance summary with recommendations based on your current
                      transaction data.
                    </p>
                  )}
                </div>
            </div>
          </article>
        </section>

        <section className="workspace-grid">
          <div className="stack">
            <article className="panel-card">
              <div className="panel-heading">
                <div>
                  <span className="card-kicker">Action center</span>
                  <h2>Add Transaction</h2>
                </div>
              </div>
              <form className="stack-form" onSubmit={handleTransactionSubmit}>
                <div className="form-grid two-up">
                  <label>
                    Type
                    <select
                      value={transactionForm.type}
                      onChange={(event) =>
                        setTransactionForm({
                          ...transactionForm,
                          type: event.target.value,
                          category_id: '',
                        })
                      }
                    >
                      <option value="expense">Expense</option>
                      <option value="income">Income</option>
                    </select>
                  </label>

                  <label>
                    Amount
                    <input
                      type="number"
                      min="0"
                      step="0.01"
                      value={transactionForm.amount}
                      onChange={(event) => setTransactionForm({ ...transactionForm, amount: event.target.value })}
                      placeholder="0.00"
                      required
                    />
                  </label>

                  <label>
                    Category
                    <select
                      value={transactionForm.category_id}
                      onChange={(event) => setTransactionForm({ ...transactionForm, category_id: event.target.value })}
                      required
                    >
                      <option value="">Select a category</option>
                      {expenseCategories.map((category) => (
                        <option key={category.id} value={category.id}>
                          {category.name}
                        </option>
                      ))}
                    </select>
                  </label>

                  <label>
                    Date
                    <input
                      type="date"
                      value={transactionForm.transaction_date}
                      onChange={(event) =>
                        setTransactionForm({ ...transactionForm, transaction_date: event.target.value })
                      }
                      required
                    />
                  </label>

                  <label>
                    Payment method
                    <input
                      type="text"
                      value={transactionForm.payment_method}
                      onChange={(event) =>
                        setTransactionForm({ ...transactionForm, payment_method: event.target.value })
                      }
                      placeholder="Card, cash, bank transfer"
                    />
                  </label>

                  <label>
                    Note
                    <input
                      type="text"
                      value={transactionForm.note}
                      onChange={(event) => setTransactionForm({ ...transactionForm, note: event.target.value })}
                      placeholder="Context for this entry"
                    />
                  </label>
                </div>

                <button type="submit" className="primary-button">
                  Add transaction
                </button>
              </form>
            </article>

            <article className="panel-card">
              <div className="panel-heading">
                <div>
                  <span className="card-kicker">Planning</span>
                  <h2>Budget Planner</h2>
                </div>
              </div>
              <form className="stack-form" onSubmit={handleBudgetSubmit}>
                <div className="form-grid two-up">
                  <label>
                    Month
                    <input
                      type="month"
                      value={budgetForm.month}
                      onChange={(event) => setBudgetForm({ ...budgetForm, month: event.target.value })}
                      required
                    />
                  </label>

                  <label>
                    Overall budget
                    <input
                      type="number"
                      min="0"
                      step="0.01"
                      value={budgetForm.overall}
                      onChange={(event) => setBudgetForm({ ...budgetForm, overall: event.target.value })}
                      placeholder="Monthly ceiling"
                    />
                  </label>
                </div>

                <label>
                  Category budgets
                  <textarea
                    rows="3"
                    value={budgetForm.byCategory}
                    onChange={(event) => setBudgetForm({ ...budgetForm, byCategory: event.target.value })}
                    placeholder="Food=500, Rent=1200, Travel=200"
                  />
                </label>

                <label className="checkbox-row">
                  <input
                    type="checkbox"
                    checked={budgetForm.carry_forward}
                    onChange={(event) => setBudgetForm({ ...budgetForm, carry_forward: event.target.checked })}
                  />
                  Carry unused budget forward
                </label>

                <button type="submit" className="primary-button" disabled={savingBudget}>
                  {savingBudget ? 'Saving budget...' : 'Save budget'}
                </button>
              </form>

              {selectedBudget && (
                <div className="budget-preview">
                  <div>
                    <span>Selected month</span>
                    <strong>{budgetForm.month}</strong>
                  </div>
                  <div>
                    <span>Overall</span>
                    <strong>{selectedBudget.overall ?? 'Not set'}</strong>
                  </div>
                  <div>
                    <span>Carry forward</span>
                    <strong>{selectedBudget.carry_forward ? 'Enabled' : 'Disabled'}</strong>
                  </div>
                </div>
              )}
            </article>

            <article className="panel-card">
              <div className="panel-heading with-actions">
                <div>
                  <span className="card-kicker">Ledger</span>
                  <h2>Transactions</h2>
                </div>
                <div className="filter-row">
                  <input
                    type="search"
                    value={search}
                    onChange={(event) => setSearch(event.target.value)}
                    placeholder="Search note, category, method"
                  />
                  <select value={txTypeFilter} onChange={(event) => setTxTypeFilter(event.target.value)}>
                    <option value="all">All types</option>
                    <option value="expense">Expenses</option>
                    <option value="income">Income</option>
                  </select>
                </div>
              </div>

              <div className="table-shell">
                {filteredTransactions.length === 0 ? (
                  <p className="empty-state">No transactions match the current filters.</p>
                ) : (
                  <table className="ledger-table">
                    <thead>
                      <tr>
                        <th>Date</th>
                        <th>Category</th>
                        <th>Amount</th>
                        <th>Type</th>
                        <th>Payment</th>
                        <th>Note</th>
                        <th />
                      </tr>
                    </thead>
                    <tbody>
                      {filteredTransactions.map((transaction) => (
                        <tr key={transaction.id}>
                          <td>{formatDate(transaction.transaction_date)}</td>
                          <td>{transaction.category_name || '-'}</td>
                          <td>{formatCurrency(transaction.amount)}</td>
                          <td>
                            <span className={`type-badge ${transaction.type}`}>{transaction.type}</span>
                          </td>
                          <td>{transaction.payment_method || '-'}</td>
                          <td>{transaction.note || '-'}</td>
                          <td>
                            <button
                              type="button"
                              className="text-button danger"
                              disabled={deletingTransactionId === transaction.id}
                              onClick={() => handleDeleteTransaction(transaction.id)}
                            >
                              {deletingTransactionId === transaction.id ? 'Removing...' : 'Delete'}
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}
              </div>
            </article>
          </div>

          <aside className="stack">
            <article className="panel-card">
              <div className="panel-heading">
                <div>
                  <span className="card-kicker">Management</span>
                  <h2>Category Studio</h2>
                </div>
              </div>

              <form className="stack-form compact" onSubmit={handleCategorySubmit}>
                <label>
                  Category name
                  <input
                    type="text"
                    value={categoryForm.name}
                    onChange={(event) => setCategoryForm({ ...categoryForm, name: event.target.value })}
                    placeholder="Health, Travel, Consulting"
                    required
                  />
                </label>

                <label>
                  Category type
                  <select
                    value={categoryForm.type}
                    onChange={(event) => setCategoryForm({ ...categoryForm, type: event.target.value })}
                  >
                    <option value="expense">Expense</option>
                    <option value="income">Income</option>
                  </select>
                </label>

                <button type="submit" className="primary-button" disabled={addingCategory}>
                  {addingCategory ? 'Creating...' : 'Create category'}
                </button>
              </form>

              <div className="category-list">
                {categories.map((category) => (
                  <div className="category-item" key={category.id}>
                    <div>
                      <strong>{category.name}</strong>
                      <span>{category.type}</span>
                    </div>
                    <div className="category-actions">
                      {category.is_default && <span className="pill muted">Default</span>}
                      <button
                        type="button"
                        className="text-button"
                        onClick={() => handleDeleteCategory(category.id)}
                        disabled={category.is_default}
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </article>

            <article className="panel-card">
              <div className="panel-heading">
                <div>
                  <span className="card-kicker">Insights</span>
                  <h2>Spending breakdown</h2>
                </div>
                <button type="button" className="ghost-button compact" onClick={exportCsv}>
                  Export CSV
                </button>
              </div>

              <div className="insight-list">
                {expenseStats.length === 0 ? (
                  <p className="empty-state">Add an expense to unlock category breakdowns.</p>
                ) : (
                  expenseStats.map((entry) => {
                    const budgetValue = selectedBudget?.by_category?.[entry.name]
                    const progress = budgetValue ? Math.min((entry.amount / budgetValue) * 100, 100) : 0

                    return (
                      <div className="insight-item" key={entry.categoryId}>
                        <div className="insight-row">
                          <strong>{entry.name}</strong>
                          <span>{formatCurrency(entry.amount)}</span>
                        </div>
                        <div className="progress-track">
                          <div className="progress-fill" style={{ width: `${progress}%` }} />
                        </div>
                        <small>
                          {budgetValue ? `${progress.toFixed(0)}% of ${formatCurrency(budgetValue)} budget` : 'No budget set'}
                        </small>
                      </div>
                    )
                  })
                )}
              </div>
            </article>

            <article className="panel-card">
              <div className="panel-heading">
                <div>
                  <span className="card-kicker">Report</span>
                  <h2>Monthly recap</h2>
                </div>
              </div>
              <div className="report-card">
                <div>
                  <span>Loaded items</span>
                  <strong>{monthlyReport?.total ?? 0}</strong>
                </div>
                <div>
                  <span>Latest activity</span>
                  <strong>{transactions[0] ? formatDate(transactions[0].transaction_date) : '-'}</strong>
                </div>
                <div>
                  <span>Current month budget</span>
                  <strong>{selectedBudget?.overall ?? 'Not set'}</strong>
                </div>
              </div>
            </article>
          </aside>
        </section>
      </main>
    </div>
  )
}
