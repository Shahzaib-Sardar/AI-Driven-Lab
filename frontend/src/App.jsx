import { useEffect, useMemo, useState } from 'react'
import { api } from './api'

const defaultForm = {
  type: 'expense',
  amount: '',
  category_id: '',
  transaction_date: '',
  note: '',
  payment_method: '',
}

export default function App() {
  const [summary, setSummary] = useState(null)
  const [transactions, setTransactions] = useState([])
  const [categories, setCategories] = useState([])
  const [form, setForm] = useState(defaultForm)
  const [error, setError] = useState('')

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
        category_id: form.category_id ? Number(form.category_id) : null,
      })
      setForm(defaultForm)
      loadData()
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <main className="layout">
      <section className="hero">
        <h1>Expense Tracking App</h1>
        <p>Track expenses, monitor budgets, and review spending insights.</p>
      </section>

      {error ? <p className="error">{error}</p> : null}

      <section className="cards">
        <article>
          <h2>Total Income</h2>
          <p>${summary?.total_income?.toFixed?.(2) ?? '0.00'}</p>
        </article>
        <article>
          <h2>Total Expense</h2>
          <p>${summary?.total_expense?.toFixed?.(2) ?? '0.00'}</p>
        </article>
        <article>
          <h2>Net Balance</h2>
          <p>${summary?.net_balance?.toFixed?.(2) ?? '0.00'}</p>
        </article>
      </section>

      <section className="panel">
        <h2>Add Transaction</h2>
        <form className="form" onSubmit={onSubmit}>
          <label>
            Type
            <select value={form.type} onChange={(event) => setForm((prev) => ({ ...prev, type: event.target.value }))}>
              <option value="expense">Expense</option>
              <option value="income">Income</option>
            </select>
          </label>
          <label>
            Amount
            <input
              value={form.amount}
              onChange={(event) => setForm((prev) => ({ ...prev, amount: event.target.value }))}
              type="number"
              min="0.01"
              step="0.01"
              required
            />
          </label>
          <label>
            Category
            <select
              value={form.category_id}
              onChange={(event) => setForm((prev) => ({ ...prev, category_id: event.target.value }))}
            >
              <option value="">Select category</option>
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
              value={form.transaction_date}
              onChange={(event) => setForm((prev) => ({ ...prev, transaction_date: event.target.value }))}
              type="date"
              required
            />
          </label>
          <label>
            Note
            <input value={form.note} onChange={(event) => setForm((prev) => ({ ...prev, note: event.target.value }))} />
          </label>
          <label>
            Payment Method
            <input
              value={form.payment_method}
              onChange={(event) => setForm((prev) => ({ ...prev, payment_method: event.target.value }))}
            />
          </label>
          <button type="submit">Save Transaction</button>
        </form>
      </section>

      <section className="panel">
        <h2>Recent Transactions</h2>
        <ul className="list">
          {transactions.length === 0 ? <li>No transactions yet.</li> : null}
          {transactions.map((tx) => (
            <li key={tx.id}>
              <strong>{tx.type}</strong> ${Number(tx.amount).toFixed(2)} - {tx.note || 'No note'}
            </li>
          ))}
        </ul>
      </section>
    </main>
  )
}
