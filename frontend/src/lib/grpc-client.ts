// REST API Client for the Library Service

import {
  Book,
  Member,
  BorrowRecord,
  CreateBookRequest,
  UpdateBookRequest,
  CreateMemberRequest,
  UpdateMemberRequest,
  ListRequest,
  ListBooksResponse,
  ListMembersResponse,
  ListBorrowRecordsRequest,
  ListBorrowRecordsResponse,
  BorrowBookRequest,
  ReturnBookRequest,
} from './types'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

class LibraryClient {
  private baseUrl: string

  constructor(baseUrl: string = API_URL) {
    this.baseUrl = baseUrl
  }

  private async request<T>(path: string, options: RequestInit = {}): Promise<T> {
    const response = await fetch(`${this.baseUrl}${path}`, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    })

    if (!response.ok) {
      let errorMessage = `HTTP ${response.status}`
      try {
        const errorData = await response.json()
        errorMessage = errorData.detail || errorMessage
      } catch {
        // Ignore JSON parse error
      }
      throw new Error(errorMessage)
    }

    return response.json()
  }

  // Book operations
  async createBook(request: CreateBookRequest): Promise<Book> {
    return this.request<Book>('/api/books', {
      method: 'POST',
      body: JSON.stringify(request),
    })
  }

  async getBook(id: number): Promise<Book> {
    return this.request<Book>(`/api/books/${id}`)
  }

  async updateBook(request: UpdateBookRequest): Promise<Book> {
    return this.request<Book>(`/api/books/${request.id}`, {
      method: 'PUT',
      body: JSON.stringify(request),
    })
  }

  async deleteBook(id: number): Promise<void> {
    await this.request(`/api/books/${id}`, { method: 'DELETE' })
  }

  async listBooks(params: ListRequest = {}): Promise<ListBooksResponse> {
    const searchParams = new URLSearchParams()
    if (params.page) searchParams.set('page', params.page.toString())
    if (params.pageSize) searchParams.set('page_size', params.pageSize.toString())
    if (params.search) searchParams.set('search', params.search)
    
    const query = searchParams.toString()
    return this.request<ListBooksResponse>(`/api/books${query ? `?${query}` : ''}`)
  }

  // Member operations
  async createMember(request: CreateMemberRequest): Promise<Member> {
    return this.request<Member>('/api/members', {
      method: 'POST',
      body: JSON.stringify(request),
    })
  }

  async getMember(id: number): Promise<Member> {
    return this.request<Member>(`/api/members/${id}`)
  }

  async updateMember(request: UpdateMemberRequest): Promise<Member> {
    return this.request<Member>(`/api/members/${request.id}`, {
      method: 'PUT',
      body: JSON.stringify(request),
    })
  }

  async deleteMember(id: number): Promise<void> {
    await this.request(`/api/members/${id}`, { method: 'DELETE' })
  }

  async listMembers(params: ListRequest = {}): Promise<ListMembersResponse> {
    const searchParams = new URLSearchParams()
    if (params.page) searchParams.set('page', params.page.toString())
    if (params.pageSize) searchParams.set('page_size', params.pageSize.toString())
    if (params.search) searchParams.set('search', params.search)
    
    const query = searchParams.toString()
    return this.request<ListMembersResponse>(`/api/members${query ? `?${query}` : ''}`)
  }

  // Borrow operations
  async borrowBook(request: BorrowBookRequest): Promise<BorrowRecord> {
    return this.request<BorrowRecord>('/api/borrows', {
      method: 'POST',
      body: JSON.stringify(request),
    })
  }

  async returnBook(request: ReturnBookRequest): Promise<BorrowRecord> {
    return this.request<BorrowRecord>(`/api/borrows/${request.borrowId}/return`, {
      method: 'POST',
    })
  }

  async getBorrowRecord(id: number): Promise<BorrowRecord> {
    return this.request<BorrowRecord>(`/api/borrows/${id}`)
  }

  async listBorrowRecords(params: ListBorrowRecordsRequest = {}): Promise<ListBorrowRecordsResponse> {
    const searchParams = new URLSearchParams()
    if (params.page) searchParams.set('page', params.page.toString())
    if (params.pageSize) searchParams.set('page_size', params.pageSize.toString())
    if (params.memberId) searchParams.set('member_id', params.memberId.toString())
    if (params.bookId) searchParams.set('book_id', params.bookId.toString())
    if (params.status) searchParams.set('status', params.status)
    
    const query = searchParams.toString()
    return this.request<ListBorrowRecordsResponse>(`/api/borrows${query ? `?${query}` : ''}`)
  }

  async getMemberBorrowedBooks(memberId: number): Promise<{ records: BorrowRecord[], member: Member }> {
    return this.request(`/api/members/${memberId}/borrowed`)
  }
}

export const libraryClient = new LibraryClient()
