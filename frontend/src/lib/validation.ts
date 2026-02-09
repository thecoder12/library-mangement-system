// Form validation utilities

export type ValidationError = string | null

export interface ValidationErrors {
  [key: string]: ValidationError
}

/**
 * Check if a value is blank (empty or whitespace only)
 */
export function isBlank(value: string | undefined | null): boolean {
  return !value || value.trim().length === 0
}

/**
 * Validate required field (not blank)
 */
export function validateRequired(value: string | undefined | null, fieldName: string): ValidationError {
  if (isBlank(value)) {
    return `${fieldName} is required`
  }
  return null
}

/**
 * Validate email format
 */
export function validateEmail(email: string | undefined | null): ValidationError {
  if (isBlank(email)) {
    return 'Email is required'
  }
  
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRegex.test(email!.trim())) {
    return 'Please enter a valid email address'
  }
  
  return null
}

/**
 * Validate minimum value
 */
export function validateMin(value: number | undefined | null, min: number, fieldName: string): ValidationError {
  if (value === undefined || value === null || value < min) {
    return `${fieldName} must be at least ${min}`
  }
  return null
}

/**
 * Validate value within range (min and max)
 */
export function validateRange(
  value: number | undefined | null, 
  min: number, 
  max: number, 
  fieldName: string
): ValidationError {
  if (value === undefined || value === null) {
    return `${fieldName} is required`
  }
  if (value < min || value > max) {
    return `${fieldName} must be between ${min.toLocaleString()} and ${max.toLocaleString()}`
  }
  return null
}

/**
 * Validate year range
 */
export function validateYear(value: number | undefined | null, fieldName: string): ValidationError {
  if (value === undefined || value === null) {
    return null // Optional field
  }
  
  const currentYear = new Date().getFullYear()
  if (value < 1000 || value > currentYear + 1) {
    return `${fieldName} must be between 1000 and ${currentYear + 1}`
  }
  
  return null
}

/**
 * Validate ISBN format (basic validation)
 */
export function validateISBN(isbn: string | undefined | null): ValidationError {
  if (isBlank(isbn)) {
    return null // Optional field
  }
  
  // Remove hyphens and spaces for validation
  const cleanISBN = isbn!.replace(/[-\s]/g, '')
  
  // ISBN-10 or ISBN-13
  if (cleanISBN.length !== 10 && cleanISBN.length !== 13) {
    return 'ISBN must be 10 or 13 characters'
  }
  
  // Check if contains only digits (and X for ISBN-10 checksum)
  if (!/^[\d]+[Xx]?$/.test(cleanISBN)) {
    return 'ISBN must contain only digits'
  }
  
  return null
}

/**
 * Validate phone number (basic validation)
 */
export function validatePhone(phone: string | undefined | null): ValidationError {
  if (isBlank(phone)) {
    return null // Optional field
  }
  
  // Remove common separators
  const cleanPhone = phone!.replace(/[-\s().]/g, '')
  
  if (cleanPhone.length < 7 || cleanPhone.length > 15) {
    return 'Please enter a valid phone number'
  }
  
  if (!/^[\d+]+$/.test(cleanPhone)) {
    return 'Phone number can only contain digits'
  }
  
  return null
}

/**
 * Check if there are any validation errors
 */
export function hasErrors(errors: ValidationErrors): boolean {
  return Object.values(errors).some((error) => error !== null)
}

/**
 * Trim all string values in an object
 */
export function trimFormData<T extends object>(data: T): T {
  const result: Record<string, unknown> = {}
  
  for (const key in data) {
    if (Object.prototype.hasOwnProperty.call(data, key)) {
      const value = (data as Record<string, unknown>)[key]
      result[key] = typeof value === 'string' ? value.trim() : value
    }
  }
  
  return result as T
}
