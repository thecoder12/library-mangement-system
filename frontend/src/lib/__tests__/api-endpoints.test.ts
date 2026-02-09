/**
 * Unit tests for API endpoints constants
 */

import { ENDPOINTS } from '../api-endpoints'

describe('ENDPOINTS', () => {
  describe('BOOKS endpoints', () => {
    test('BASE returns correct path', () => {
      expect(ENDPOINTS.BOOKS.BASE).toBe('/api/books')
    })

    test('BY_ID returns correct path with id', () => {
      expect(ENDPOINTS.BOOKS.BY_ID(1)).toBe('/api/books/1')
      expect(ENDPOINTS.BOOKS.BY_ID(123)).toBe('/api/books/123')
    })
  })

  describe('MEMBERS endpoints', () => {
    test('BASE returns correct path', () => {
      expect(ENDPOINTS.MEMBERS.BASE).toBe('/api/members')
    })

    test('BY_ID returns correct path with id', () => {
      expect(ENDPOINTS.MEMBERS.BY_ID(1)).toBe('/api/members/1')
      expect(ENDPOINTS.MEMBERS.BY_ID(456)).toBe('/api/members/456')
    })

    test('BORROWED returns correct path with id', () => {
      expect(ENDPOINTS.MEMBERS.BORROWED(1)).toBe('/api/members/1/borrowed')
      expect(ENDPOINTS.MEMBERS.BORROWED(789)).toBe('/api/members/789/borrowed')
    })
  })

  describe('BORROWS endpoints', () => {
    test('BASE returns correct path', () => {
      expect(ENDPOINTS.BORROWS.BASE).toBe('/api/borrows')
    })

    test('BY_ID returns correct path with id', () => {
      expect(ENDPOINTS.BORROWS.BY_ID(1)).toBe('/api/borrows/1')
      expect(ENDPOINTS.BORROWS.BY_ID(999)).toBe('/api/borrows/999')
    })

    test('RETURN returns correct path with id', () => {
      expect(ENDPOINTS.BORROWS.RETURN(1)).toBe('/api/borrows/1/return')
      expect(ENDPOINTS.BORROWS.RETURN(100)).toBe('/api/borrows/100/return')
    })
  })

  describe('Consistency', () => {
    test('all endpoints start with /api prefix', () => {
      expect(ENDPOINTS.BOOKS.BASE).toMatch(/^\/api\//)
      expect(ENDPOINTS.MEMBERS.BASE).toMatch(/^\/api\//)
      expect(ENDPOINTS.BORROWS.BASE).toMatch(/^\/api\//)
    })

    test('dynamic endpoints return strings', () => {
      expect(typeof ENDPOINTS.BOOKS.BY_ID(1)).toBe('string')
      expect(typeof ENDPOINTS.MEMBERS.BY_ID(1)).toBe('string')
      expect(typeof ENDPOINTS.MEMBERS.BORROWED(1)).toBe('string')
      expect(typeof ENDPOINTS.BORROWS.BY_ID(1)).toBe('string')
      expect(typeof ENDPOINTS.BORROWS.RETURN(1)).toBe('string')
    })
  })
})
