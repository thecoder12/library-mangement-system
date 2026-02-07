// TypeScript types matching the protobuf definitions

export interface Book {
  id: number
  title: string
  author: string
  isbn: string
  publishedYear: number
  genre: string
  totalCopies: number
  availableCopies: number
  createdAt: string
  updatedAt: string
}

export interface Member {
  id: number
  name: string
  email: string
  phone: string
  address: string
  membershipDate: string
  isActive: boolean
  createdAt: string
  updatedAt: string
}

export interface BorrowRecord {
  id: number
  bookId: number
  memberId: number
  borrowDate: string
  dueDate: string
  returnDate: string
  status: 'BORROWED' | 'RETURNED'
  book?: Book
  member?: Member
}

export interface CreateBookRequest {
  title: string
  author: string
  isbn?: string
  publishedYear?: number
  genre?: string
  totalCopies?: number
}

export interface UpdateBookRequest {
  id: number
  title?: string
  author?: string
  isbn?: string
  publishedYear?: number
  genre?: string
  totalCopies?: number
}

export interface CreateMemberRequest {
  name: string
  email: string
  phone?: string
  address?: string
}

export interface UpdateMemberRequest {
  id: number
  name?: string
  email?: string
  phone?: string
  address?: string
  isActive?: boolean
}

export interface ListRequest {
  page?: number
  pageSize?: number
  search?: string
}

export interface ListBooksResponse {
  books: Book[]
  totalCount: number
  page: number
  pageSize: number
}

export interface ListMembersResponse {
  members: Member[]
  totalCount: number
  page: number
  pageSize: number
}

export interface ListBorrowRecordsRequest {
  page?: number
  pageSize?: number
  memberId?: number
  bookId?: number
  status?: string
}

export interface ListBorrowRecordsResponse {
  records: BorrowRecord[]
  totalCount: number
  page: number
  pageSize: number
}

export interface BorrowBookRequest {
  bookId: number
  memberId: number
}

export interface ReturnBookRequest {
  borrowId: number
}
