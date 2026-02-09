/**
 * Form validation utilities with trimming and whitespace prevention
 */

export interface ValidationResult {
  isValid: boolean
  error?: string
}

export interface FieldValidation {
  value: string
  fieldName: string
  required?: boolean
  minLength?: number
  maxLength?: number
  pattern?: RegExp
  patternMessage?: string
}

/**
 * Trims whitespace from a string value
 */
export function trimValue(value: string): string {
  return value.trim()
}

/**
 * Checks if a value is empty or contains only whitespace
 */
export function isEmptyOrWhitespace(value: string): boolean {
  return !value || value.trim().length === 0
}

/**
 * Validates a single field with trimming and various rules
 */
export function validateField(config: FieldValidation): ValidationResult {
  const trimmedValue = trimValue(config.value)
  
  // Required check (after trimming)
  if (config.required && isEmptyOrWhitespace(config.value)) {
    return {
      isValid: false,
      error: `${config.fieldName} is required and cannot be empty or contain only whitespace`,
    }
  }
  
  // Skip other validations if field is optional and empty
  if (!config.required && isEmptyOrWhitespace(config.value)) {
    return { isValid: true }
  }
  
  // Min length check
  if (config.minLength !== undefined && trimmedValue.length < config.minLength) {
    return {
      isValid: false,
      error: `${config.fieldName} must be at least ${config.minLength} characters`,
    }
  }
  
  // Max length check
  if (config.maxLength !== undefined && trimmedValue.length > config.maxLength) {
    return {
      isValid: false,
      error: `${config.fieldName} must be no more than ${config.maxLength} characters`,
    }
  }
  
  // Pattern check
  if (config.pattern && !config.pattern.test(trimmedValue)) {
    return {
      isValid: false,
      error: config.patternMessage || `${config.fieldName} has an invalid format`,
    }
  }
  
  return { isValid: true }
}

/**
 * Validates multiple fields and returns all errors
 */
export function validateFields(fields: FieldValidation[]): ValidationResult {
  for (const field of fields) {
    const result = validateField(field)
    if (!result.isValid) {
      return result
    }
  }
  return { isValid: true }
}

/**
 * Email validation pattern
 * Note: This is a basic email pattern for client-side validation.
 * Backend should perform more thorough validation.
 */
export const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

/**
 * ISBN validation patterns (supports ISBN-10 and ISBN-13)
 * Note: This is a basic format check. Backend should validate checksum.
 */
export const ISBN_10_PATTERN = /^(?:\d{9}[\dXx]|\d{10})$/
export const ISBN_13_PATTERN = /^(?:\d{13}|97[89]\d{10})$/
export const ISBN_PATTERN = /^(?:\d{9}[\dXx]|\d{10}|\d{13}|97[89]\d{10})$/

/**
 * Validates email format
 */
export function validateEmail(email: string): ValidationResult {
  return validateField({
    value: email,
    fieldName: 'Email',
    required: true,
    pattern: EMAIL_PATTERN,
    patternMessage: 'Please enter a valid email address',
  })
}

/**
 * Validates ISBN format (optional field - only validates format if provided)
 */
export function validateISBN(isbn: string): ValidationResult {
  if (isEmptyOrWhitespace(isbn)) {
    return { isValid: true } // ISBN is optional
  }
  
  // Remove hyphens and spaces for validation
  const cleanedISBN = isbn.replace(/[-\s]/g, '')
  
  if (!ISBN_PATTERN.test(cleanedISBN)) {
    return {
      isValid: false,
      error: 'Please enter a valid ISBN (10 or 13 digits)',
    }
  }
  
  return { isValid: true }
}

/**
 * Trims all string fields in a form data object
 */
export function trimFormData<T extends Record<string, unknown>>(data: T): T {
  const trimmed = { ...data }
  for (const key in trimmed) {
    if (typeof trimmed[key] === 'string') {
      (trimmed as Record<string, unknown>)[key] = (trimmed[key] as string).trim()
    }
  }
  return trimmed
}
