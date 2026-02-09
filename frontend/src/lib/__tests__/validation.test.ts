/**
 * Unit tests for validation utilities
 */

import {
  isBlank,
  validateRequired,
  validateEmail,
  validateMin,
  validateRange,
  validateYear,
  validateISBN,
  validatePhone,
  hasErrors,
  trimFormData,
} from '../validation'

describe('isBlank', () => {
  test('returns true for null', () => {
    expect(isBlank(null)).toBe(true)
  })

  test('returns true for undefined', () => {
    expect(isBlank(undefined)).toBe(true)
  })

  test('returns true for empty string', () => {
    expect(isBlank('')).toBe(true)
  })

  test('returns true for whitespace only', () => {
    expect(isBlank('   ')).toBe(true)
    expect(isBlank('\t\n')).toBe(true)
  })

  test('returns false for non-empty string', () => {
    expect(isBlank('hello')).toBe(false)
    expect(isBlank('  hello  ')).toBe(false)
  })
})

describe('validateRequired', () => {
  test('returns error for blank value', () => {
    expect(validateRequired('', 'Name')).toBe('Name is required')
    expect(validateRequired('   ', 'Name')).toBe('Name is required')
    expect(validateRequired(null, 'Name')).toBe('Name is required')
    expect(validateRequired(undefined, 'Name')).toBe('Name is required')
  })

  test('returns null for valid value', () => {
    expect(validateRequired('John', 'Name')).toBeNull()
    expect(validateRequired('  John  ', 'Name')).toBeNull()
  })
})

describe('validateEmail', () => {
  test('returns error for blank email', () => {
    expect(validateEmail('')).toBe('Email is required')
    expect(validateEmail(null)).toBe('Email is required')
  })

  test('returns error for invalid email format', () => {
    expect(validateEmail('invalid')).toBe('Please enter a valid email address')
    expect(validateEmail('invalid@')).toBe('Please enter a valid email address')
    expect(validateEmail('@example.com')).toBe('Please enter a valid email address')
    expect(validateEmail('user@.com')).toBe('Please enter a valid email address')
  })

  test('returns null for valid email', () => {
    expect(validateEmail('user@example.com')).toBeNull()
    expect(validateEmail('user.name@example.co.uk')).toBeNull()
    expect(validateEmail('user+tag@example.com')).toBeNull()
  })
})

describe('validateMin', () => {
  test('returns error for undefined/null', () => {
    expect(validateMin(undefined, 1, 'Count')).toBe('Count must be at least 1')
    expect(validateMin(null, 1, 'Count')).toBe('Count must be at least 1')
  })

  test('returns error for value below minimum', () => {
    expect(validateMin(0, 1, 'Count')).toBe('Count must be at least 1')
    expect(validateMin(-5, 0, 'Value')).toBe('Value must be at least 0')
  })

  test('returns null for valid value', () => {
    expect(validateMin(1, 1, 'Count')).toBeNull()
    expect(validateMin(10, 1, 'Count')).toBeNull()
    expect(validateMin(0, 0, 'Value')).toBeNull()
  })
})

describe('validateRange', () => {
  test('returns error for undefined/null', () => {
    expect(validateRange(undefined, 1, 100, 'Count')).toBe('Count is required')
    expect(validateRange(null, 1, 100, 'Count')).toBe('Count is required')
  })

  test('returns error for value below minimum', () => {
    expect(validateRange(0, 1, 100, 'Count')).toBe('Count must be between 1 and 100')
  })

  test('returns error for value above maximum', () => {
    expect(validateRange(101, 1, 100, 'Count')).toBe('Count must be between 1 and 100')
  })

  test('returns null for value within range', () => {
    expect(validateRange(1, 1, 100, 'Count')).toBeNull()
    expect(validateRange(50, 1, 100, 'Count')).toBeNull()
    expect(validateRange(100, 1, 100, 'Count')).toBeNull()
  })

  test('formats large numbers with commas', () => {
    expect(validateRange(20000, 1, 10000, 'Copies')).toBe('Copies must be between 1 and 10,000')
  })
})

describe('validateYear', () => {
  test('returns null for undefined/null (optional field)', () => {
    expect(validateYear(undefined, 'Year')).toBeNull()
    expect(validateYear(null, 'Year')).toBeNull()
  })

  test('returns error for year below minimum', () => {
    expect(validateYear(999, 'Year')).toContain('must be between')
  })

  test('returns error for year too far in future', () => {
    const farFuture = new Date().getFullYear() + 10
    expect(validateYear(farFuture, 'Year')).toContain('must be between')
  })

  test('returns null for valid year', () => {
    expect(validateYear(2024, 'Year')).toBeNull()
    expect(validateYear(1990, 'Year')).toBeNull()
    expect(validateYear(1500, 'Year')).toBeNull()
  })
})

describe('validateISBN', () => {
  test('returns null for blank (optional field)', () => {
    expect(validateISBN('')).toBeNull()
    expect(validateISBN(null)).toBeNull()
    expect(validateISBN(undefined)).toBeNull()
  })

  test('returns error for invalid length', () => {
    expect(validateISBN('12345')).toBe('ISBN must be 10 or 13 characters')
    expect(validateISBN('12345678901234')).toBe('ISBN must be 10 or 13 characters')
  })

  test('returns error for non-numeric characters', () => {
    expect(validateISBN('123456789A')).toBe('ISBN must contain only digits')
    expect(validateISBN('12345678901AB')).toBe('ISBN must contain only digits')
  })

  test('returns null for valid ISBN-10', () => {
    expect(validateISBN('0123456789')).toBeNull()
    expect(validateISBN('012345678X')).toBeNull() // X is valid for ISBN-10
  })

  test('returns null for valid ISBN-13', () => {
    expect(validateISBN('9780123456789')).toBeNull()
  })

  test('handles ISBN with hyphens', () => {
    expect(validateISBN('978-0-12345-678-9')).toBeNull()
    expect(validateISBN('0-12-345678-9')).toBeNull()
  })
})

describe('validatePhone', () => {
  test('returns null for blank (optional field)', () => {
    expect(validatePhone('')).toBeNull()
    expect(validatePhone(null)).toBeNull()
    expect(validatePhone(undefined)).toBeNull()
  })

  test('returns error for too short', () => {
    expect(validatePhone('123')).toBe('Please enter a valid phone number')
  })

  test('returns error for too long', () => {
    expect(validatePhone('1234567890123456')).toBe('Please enter a valid phone number')
  })

  test('returns error for invalid characters', () => {
    expect(validatePhone('123-456-ABCD')).toBe('Phone number can only contain digits')
  })

  test('returns null for valid phone', () => {
    expect(validatePhone('5550100')).toBeNull()
    expect(validatePhone('555-010-0100')).toBeNull()
    expect(validatePhone('(555) 010-0100')).toBeNull()
    expect(validatePhone('+15550100100')).toBeNull()
  })
})

describe('hasErrors', () => {
  test('returns false for empty errors object', () => {
    expect(hasErrors({})).toBe(false)
  })

  test('returns false when all errors are null', () => {
    expect(hasErrors({ name: null, email: null })).toBe(false)
  })

  test('returns true when any error exists', () => {
    expect(hasErrors({ name: 'Name is required', email: null })).toBe(true)
    expect(hasErrors({ name: null, email: 'Invalid email' })).toBe(true)
  })
})

describe('trimFormData', () => {
  test('trims string values', () => {
    const data = { name: '  John  ', email: '  john@example.com  ' }
    const trimmed = trimFormData(data)
    
    expect(trimmed.name).toBe('John')
    expect(trimmed.email).toBe('john@example.com')
  })

  test('preserves non-string values', () => {
    const data = { name: '  John  ', age: 30, active: true }
    const trimmed = trimFormData(data)
    
    expect(trimmed.name).toBe('John')
    expect(trimmed.age).toBe(30)
    expect(trimmed.active).toBe(true)
  })

  test('handles empty object', () => {
    const trimmed = trimFormData({})
    expect(trimmed).toEqual({})
  })

  test('handles undefined string values', () => {
    const data = { name: '  John  ', optional: undefined }
    const trimmed = trimFormData(data)
    
    expect(trimmed.name).toBe('John')
    expect(trimmed.optional).toBeUndefined()
  })
})
