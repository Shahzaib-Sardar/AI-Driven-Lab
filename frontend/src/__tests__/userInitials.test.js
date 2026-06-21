import { describe, it, expect } from 'vitest'

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

describe('getUserInitials', () => {
  it('should return first letter of first and second name', () => {
    const user = { full_name: 'Test User', email: 'test@example.com' }
    expect(getUserInitials(user)).toBe('TU')
  })

  it('should handle single name by taking first 2 letters', () => {
    const user = { full_name: 'Thomas', email: 'thomas@example.com' }
    expect(getUserInitials(user)).toBe('TH')
  })

  it('should use email if no full name provided', () => {
    const user = { full_name: '', email: 'alex@example.com' }
    expect(getUserInitials(user)).toBe('AL')
  })

  it('should return U as fallback', () => {
    const user = { full_name: '', email: '' }
    expect(getUserInitials(user)).toBe('U')
  })

  it('should handle extra whitespace in name', () => {
    const user = { full_name: '  John   Doe  ', email: 'john@example.com' }
    expect(getUserInitials(user)).toBe('JD')
  })

  it('should handle null or undefined user', () => {
    expect(getUserInitials(null)).toBe('U')
    expect(getUserInitials(undefined)).toBe('U')
  })

  it('should uppercase the initials', () => {
    const user = { full_name: 'alice bob', email: 'alice@example.com' }
    expect(getUserInitials(user)).toBe('AB')
  })
})
