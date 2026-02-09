/**
 * Centralized API endpoint paths for the Library Management System.
 * This file is shared between frontend and backend to maintain consistency.
 */

// API version prefix
export const API_PREFIX = '/api'

// Books endpoints
export const BOOKS_ENDPOINTS = {
  BASE: `${API_PREFIX}/books`,
  BY_ID: (id: number | string) => `${API_PREFIX}/books/${id}`,
} as const

// Members endpoints
export const MEMBERS_ENDPOINTS = {
  BASE: `${API_PREFIX}/members`,
  BY_ID: (id: number | string) => `${API_PREFIX}/members/${id}`,
  BORROWED_BOOKS: (memberId: number | string) => `${API_PREFIX}/members/${memberId}/borrowed`,
} as const

// Borrow records endpoints
export const BORROWS_ENDPOINTS = {
  BASE: `${API_PREFIX}/borrows`,
  BY_ID: (id: number | string) => `${API_PREFIX}/borrows/${id}`,
  RETURN: (borrowId: number | string) => `${API_PREFIX}/borrows/${borrowId}/return`,
} as const

// All endpoints grouped
export const API_ENDPOINTS = {
  BOOKS: BOOKS_ENDPOINTS,
  MEMBERS: MEMBERS_ENDPOINTS,
  BORROWS: BORROWS_ENDPOINTS,
} as const

// Export type for type safety
export type ApiEndpoints = typeof API_ENDPOINTS
