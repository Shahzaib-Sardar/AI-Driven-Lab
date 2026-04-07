import { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api'
import { useAuth } from '../context/AuthContext'
import '../styles.css'

const defaultForm = {
  type: 'expense',
  amount: '',
  category_id: '',
  transaction_date: '',
  note: '',
  payment_method: '',
}

export default function Dashboard() {
  const [summary, setSummary] = useState(null)
  const [transactions, setTransactions] = useState([])
  const [categories, setCategories] = useState([])
  const [form, setForm] = useState(defaultForm)
  const [error, setError] = useState('')
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const expenseCategories = useMemo(
    () => categories.filter((category) => category.type === form.type),
    [categories, form.type],
  )

  async function loadData() {
    try {
      const [summaryData, txData, categoryData] = await Promise.all([
        api.getSummary(),
        api.listTransactions(),
        api.listCategories(),
      ])
      setSummary(summaryData)
      setTransactions(txData.items || [])
      setCategories(categoryData.items || [])
      setError('')
    } catch (err) {
      setError(err.message)
    }
  }

  useEffect(() => {
    loadData()
  }, [])

  async function onSubmit(event) {
    event.preventDefault()
    try {
      await api.createTransaction({
        ...form,
        amount: Number(form.amount),
        category_id: Number(form.category_id),
      })
      setForm(defaultForm)
      loadData()
    } catch (err) {
      setError(err.message)
    }
  }

  function handleLogout() {
    logout()
    navigate('/login')
  }

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>Expense Tracker</h1>
        <div className="user-info">
          <span>Welcome, {user?.full_name || user?.email}</span>
          <button onClick={handleLogout} className="logout-btn">
            Logout
          </button>
        </div>
      </header>

      <main className="dashboard-content">
        {error && <div className="error-message">{error}</div>}

        {summary && (
          <div className="summary">
            <div className="summary-item">
              <h3>Total Balance</h3>
              <p className="amount">${summary.balance?.toFixed(2) || '0.00'}</p>
            </div>
            <div className="summary-item">
              <h3>Total Income</h3>
              <p className="amount income">${summary.income?.toFixed(2) || '0.00'}</p>
            </div>
            <div className="summary-item">
              <h3>Total Expenses</h3>
              <p className="amount expense">${summary.expenses?.toFixed(2) || '0.00'}</p>
            </div>
          </div>
        )}

        <section className="transaction-form">
          <h2>Add Transaction</h2>
          <form onSubmit={onSubmit}>
            <div className="form-row">
              <div className="form-group">
                <label>Type</label>
                <select
                  value={form.type}
                  onChange={(e) => setForm({ ...form, type: e.target.value, category_id: '' })}
                >
                  <option value="expense">Expense</option>
                  <option value="income">Income</option>
                </select>
              </div>

              <div className="form-group">
                <label>Amount</label>
                <input
                  type="number"
                  step="0.01"
                  value={form.amount}
                  onChange={(e) => setForm({ ...form, amount: e.target.value })}
                  required
                />
              </div>

              <div className="form-group">
                <label>Category</label>
                <select
                  value={form.category_id}
                  onChange={(e) => setForm({ ...form, category_id: e.target.value })}
                  required
                >
                  <option value="">Select a category</option>
                  {expenseCategories.map((cat) => (
                    <option key={cat.id} value={cat.id}>
                      {cat.name}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Date</label>
                <input
                  type="date"
                  value={form.transaction_date}
                  onChange={(e) => setForm({ ...form, transaction_date: e.target.value })}
                  required
                />
              </div>

              <div className="form-group">
                <label>Payment Method</label>
                <input
                  type="text"
                  value={form.payment_method}
                  onChange={(e) => setForm({ ...form, payment_method: e.target.value })}
                  placeholder="e.g., Credit Card, Cash"
                />
              </div>

              <div className="form-group">
                <label>Note</label>
                <input
                  type="text"
                  value={form.note}
                  onChange={(e) => setForm({ ...form, note: e.target.value })}
                  placeholder="Optional note"
                />
              </div>
            </div>

            <button type="submit" className="submit-btn">
              Add Transaction
            </button>
          </form>
        </section>

        <section className="transactions-list">
          <h2>Recent Transactions</h2>
          {transactions.length === 0 ? (
            <p className="no-data">No transactions yet</p>
          ) : (
            <table>
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Category</th>
                  <th>Amount</th>
                  <th>Type</th>
                  <th>Payment Method</th>
                  <th>Note</th>
                </tr>
              </thead>
              <tbody>
                {transactions.map((tx) => (
                  <tr key={tx.id}>
                    <td>{new Date(tx.transaction_date).toLocaleDateString()}</td>
                    <td>{tx.category_name}</td>
                    <td>${tx.amount?.toFixed(2)}</td>
                    <td>
                      <span className={`type-badge ${tx.type}`}>{tx.type}</span>
                    </td>
                    <td>{tx.payment_method || '-'}</td>
                    <td>{tx.note || '-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </section>
      </main>
    </div>
  )
}
