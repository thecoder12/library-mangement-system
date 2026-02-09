/**
 * Centralized API endpoint constants.
 * All API paths should be defined here to ensure consistency
 * between frontend and backend.
 */

const API_PREFIX = '/api'

export const ENDPOINTS = {
  // Books
  BOOKS: {
    BASE: `${API_PREFIX}/books`,
    BY_ID: (id: number) => `${API_PREFIX}/books/${id}`,
  },

  // Members
  MEMBERS: {
    BASE: `${API_PREFIX}/members`,
    BY_ID: (id: number) => `${API_PREFIX}/members/${id}`,
    BORROWED: (id: number) => `${API_PREFIX}/members/${id}/borrowed`,
  },

  // Borrows
  BORROWS: {
    BASE: `${API_PREFIX}/borrows`,
    BY_ID: (id: number) => `${API_PREFIX}/borrows/${id}`,
    RETURN: (id: number) => `${API_PREFIX}/borrows/${id}/return`,
  },
} as const
