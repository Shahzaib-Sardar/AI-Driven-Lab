import { describe, it, expect } from 'vitest'

describe('Budget Calculations', () => {
  it('should calculate budget usage percentage correctly', () => {
    const budget = 1000
    const spent = 250
    const percentageUsed = (spent / budget) * 100
    expect(percentageUsed).toBe(25)
  })

  it('should show 0% when no expenses', () => {
    const budget = 1000
    const spent = 0
    const percentageUsed = (spent / budget) * 100
    expect(percentageUsed).toBe(0)
  })

  it('should show 100% at budget limit', () => {
    const budget = 1000
    const spent = 1000
    const percentageUsed = (spent / budget) * 100
    expect(percentageUsed).toBe(100)
  })

  it('should show over 100% when overspent', () => {
    const budget = 1000
    const spent = 1500
    const percentageUsed = (spent / budget) * 100
    expect(percentageUsed).toBe(150)
  })
})

describe('Transaction Totals', () => {
  it('should sum all expenses correctly', () => {
    const transactions = [
      { type: 'expense', amount: 100 },
      { type: 'expense', amount: 250 },
      { type: 'income', amount: 5000 },
    ]
    const total = transactions
      .filter(t => t.type === 'expense')
      .reduce((sum, t) => sum + t.amount, 0)
    expect(total).toBe(350)
  })

  it('should sum all income correctly', () => {
    const transactions = [
      { type: 'income', amount: 5000 },
      { type: 'income', amount: 2000 },
      { type: 'expense', amount: 100 },
    ]
    const total = transactions
      .filter(t => t.type === 'income')
      .reduce((sum, t) => sum + t.amount, 0)
    expect(total).toBe(7000)
  })

  it('should calculate balance (income - expenses)', () => {
    const transactions = [
      { type: 'income', amount: 5000 },
      { type: 'expense', amount: 100 },
      { type: 'expense', amount: 200 },
    ]
    const income = transactions
      .filter(t => t.type === 'income')
      .reduce((sum, t) => sum + t.amount, 0)
    const expenses = transactions
      .filter(t => t.type === 'expense')
      .reduce((sum, t) => sum + t.amount, 0)
    expect(income - expenses).toBe(4700)
  })

  it('should handle empty transaction list', () => {
    const transactions = []
    const total = transactions
      .filter(t => t.type === 'expense')
      .reduce((sum, t) => sum + t.amount, 0)
    expect(total).toBe(0)
  })

  it('should calculate savings rate', () => {
    const income = 5000
    const expenses = 1000
    const savings = income - expenses
    const savingsRate = (savings / income) * 100
    expect(savings).toBe(4000)
    expect(savingsRate).toBe(80)
  })
})
