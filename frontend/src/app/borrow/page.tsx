'use client'

import { useEffect, useState } from 'react'
import { ArrowPathIcon, CheckCircleIcon, MagnifyingGlassIcon } from '@heroicons/react/24/outline'
import { libraryClient } from '@/lib/grpc-client'
import { Book, Member, BorrowRecord } from '@/lib/types'
import { Table } from '@/components/Table'
import { Pagination } from '@/components/Pagination'
import { Modal } from '@/components/Modal'
import { useToast } from '@/components/Toast'
import { useConfirm } from '@/components/ConfirmDialog'
import { FormField, Select } from '@/components/FormField'
import { ValidationErrors, hasErrors } from '@/lib/validation'

export default function BorrowPage() {
  const toast = useToast()
  const { confirm } = useConfirm()
  const [records, setRecords] = useState<BorrowRecord[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [page, setPage] = useState(1)
  const [pageSize] = useState(10)
  const [totalCount, setTotalCount] = useState(0)
  const [statusFilter, setStatusFilter] = useState<string>('BORROWED')
  const [search, setSearch] = useState('')
  const [searchInput, setSearchInput] = useState('')
  
  // Borrow modal state
  const [isBorrowModalOpen, setIsBorrowModalOpen] = useState(false)
  const [books, setBooks] = useState<Book[]>([])
  const [members, setMembers] = useState<Member[]>([])
  const [selectedBookId, setSelectedBookId] = useState<number | ''>('')
  const [selectedMemberId, setSelectedMemberId] = useState<number | ''>('')
  const [borrowLoading, setBorrowLoading] = useState(false)
  const [borrowError, setBorrowError] = useState<string | null>(null)
  const [fieldErrors, setFieldErrors] = useState<ValidationErrors>({})

  useEffect(() => {
    loadRecords()
  }, [page, statusFilter, search])

  const loadRecords = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await libraryClient.listBorrowRecords({ 
        page, 
        pageSize, 
        status: statusFilter || undefined,
        search: search || undefined,
      })
      setRecords(response.records)
      setTotalCount(response.totalCount)
    } catch (err) {
      setError('Failed to load borrow records. Make sure the backend is running.')
      console.error('Error loading records:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    setSearch(searchInput)
    setPage(1)
  }

  const loadBooksAndMembers = async () => {
    try {
      const [booksRes, membersRes] = await Promise.all([
        libraryClient.listBooks({ page: 1, pageSize: 100 }),
        libraryClient.listMembers({ page: 1, pageSize: 100 }),
      ])
      setBooks(booksRes.books.filter(b => b.availableCopies > 0))
      setMembers(membersRes.members.filter(m => m.isActive))
    } catch (err) {
      console.error('Error loading books/members:', err)
    }
  }

  const openBorrowModal = () => {
    setSelectedBookId('')
    setSelectedMemberId('')
    setBorrowError(null)
    setFieldErrors({})
    setIsBorrowModalOpen(true)
    loadBooksAndMembers()
  }

  const validateBorrowForm = (): boolean => {
    const errors: ValidationErrors = {
      memberId: !selectedMemberId ? 'Please select a member' : null,
      bookId: !selectedBookId ? 'Please select a book' : null,
    }
    
    setFieldErrors(errors)
    return !hasErrors(errors)
  }

  const handleBorrow = async (e: React.FormEvent) => {
    e.preventDefault()
    setBorrowError(null)
    
    if (!validateBorrowForm()) {
      return
    }

    setBorrowLoading(true)

    try {
      await libraryClient.borrowBook({
        bookId: selectedBookId as number,
        memberId: selectedMemberId as number,
      })
      toast.success('Book borrowed successfully')
      setIsBorrowModalOpen(false)
      loadRecords()
    } catch (err) {
      setBorrowError(err instanceof Error ? err.message : 'Failed to borrow book')
    } finally {
      setBorrowLoading(false)
    }
  }

  const handleReturn = async (record: BorrowRecord) => {
    const bookTitle = record.book?.title || 'this book'
    const confirmed = await confirm({
      title: 'Return Book',
      message: `Are you sure you want to return "${bookTitle}"?`,
      confirmText: 'Return',
      cancelText: 'Cancel',
      variant: 'info',
    })
    
    if (!confirmed) return

    try {
      await libraryClient.returnBook({ borrowId: record.id })
      toast.success('Book returned successfully')
      loadRecords()
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Failed to return book')
    }
  }

  const columns = [
    { 
      header: 'Book', 
      accessor: (row: BorrowRecord) => row.book?.title || `Book #${row.bookId}` 
    },
    { 
      header: 'Member', 
      accessor: (row: BorrowRecord) => row.member?.name || `Member #${row.memberId}` 
    },
    { 
      header: 'Borrow Date', 
      accessor: (row: BorrowRecord) => row.borrowDate ? new Date(row.borrowDate).toLocaleDateString() : '-'
    },
    { 
      header: 'Due Date', 
      accessor: (row: BorrowRecord) => {
        if (!row.dueDate) return '-'
        const dueDate = new Date(row.dueDate)
        const isOverdue = row.status === 'BORROWED' && dueDate < new Date()
        return (
          <span className={isOverdue ? 'text-red-600 font-medium' : ''}>
            {dueDate.toLocaleDateString()}
            {isOverdue && ' (Overdue)'}
          </span>
        )
      }
    },
    { 
      header: 'Return Date', 
      accessor: (row: BorrowRecord) => row.returnDate ? new Date(row.returnDate).toLocaleDateString() : '-'
    },
    { 
      header: 'Status', 
      accessor: (row: BorrowRecord) => (
        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
          row.status === 'BORROWED' ? 'bg-amber-100 text-amber-800' : 'bg-green-100 text-green-800'
        }`}>
          {row.status}
        </span>
      )
    },
  ]

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Borrow / Return</h1>
          <p className="mt-1 text-gray-600">Manage book borrowing and returns</p>
        </div>
        <button onClick={openBorrowModal} className="btn btn-primary">
          <ArrowPathIcon className="h-5 w-5 mr-2" />
          Borrow Book
        </button>
      </div>

      {/* Search and Status Filter */}
      <div className="mb-6 flex flex-col sm:flex-row gap-4">
        {/* Search */}
        <form onSubmit={handleSearch} className="flex-1">
          <div className="relative">
            <MagnifyingGlassIcon className="h-5 w-5 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              placeholder="Search by book title, author, member name or email..."
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            />
            {searchInput && (
              <button
                type="button"
                onClick={() => { setSearchInput(''); setSearch(''); setPage(1) }}
                className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
              >
                &times;
              </button>
            )}
          </div>
        </form>

        {/* Status Filter */}
        <div className="flex space-x-2">
          {['BORROWED', 'RETURNED', ''].map((status) => (
            <button
              key={status || 'all'}
              onClick={() => { setStatusFilter(status); setPage(1) }}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                statusFilter === status
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {status === 'BORROWED' ? 'Currently Borrowed' : status === 'RETURNED' ? 'Returned' : 'All Records'}
            </button>
          ))}
        </div>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-700">{error}</p>
        </div>
      )}

      <div className="card">
        <Table
          columns={columns}
          data={records}
          keyExtractor={(record) => record.id}
          loading={loading}
          emptyMessage="No borrow records found"
          actions={(record) => (
            record.status === 'BORROWED' ? (
              <button
                onClick={() => handleReturn(record)}
                className="btn btn-secondary text-xs py-1"
              >
                <CheckCircleIcon className="h-4 w-4 mr-1" />
                Return
              </button>
            ) : null
          )}
        />
        <Pagination
          page={page}
          pageSize={pageSize}
          totalCount={totalCount}
          onPageChange={setPage}
        />
      </div>

      {/* Borrow Modal */}
      <Modal
        isOpen={isBorrowModalOpen}
        onClose={() => setIsBorrowModalOpen(false)}
        title="Borrow a Book"
      >
        <form onSubmit={handleBorrow} className="space-y-4">
          {borrowError && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
              {borrowError}
            </div>
          )}
          
          <FormField label="Select Member" required error={fieldErrors.memberId}>
            <Select
              value={selectedMemberId}
              onChange={(e) => {
                setSelectedMemberId(e.target.value ? parseInt(e.target.value) : '')
                if (fieldErrors.memberId) setFieldErrors({ ...fieldErrors, memberId: null })
              }}
              error={fieldErrors.memberId}
            >
              <option value="">Choose a member...</option>
              {members.map((member) => (
                <option key={member.id} value={member.id}>
                  {member.name} ({member.email})
                </option>
              ))}
            </Select>
            {members.length === 0 && !fieldErrors.memberId && (
              <p className="mt-1 text-sm text-gray-500">No active members available</p>
            )}
          </FormField>
          
          <FormField label="Select Book" required error={fieldErrors.bookId}>
            <Select
              value={selectedBookId}
              onChange={(e) => {
                setSelectedBookId(e.target.value ? parseInt(e.target.value) : '')
                if (fieldErrors.bookId) setFieldErrors({ ...fieldErrors, bookId: null })
              }}
              error={fieldErrors.bookId}
            >
              <option value="">Choose a book...</option>
              {books.map((book) => (
                <option key={book.id} value={book.id}>
                  {book.title} by {book.author} ({book.availableCopies} available)
                </option>
              ))}
            </Select>
            {books.length === 0 && !fieldErrors.bookId && (
              <p className="mt-1 text-sm text-gray-500">No books available for borrowing</p>
            )}
          </FormField>
          
          <div className="flex justify-end space-x-3 pt-4">
            <button
              type="button"
              onClick={() => setIsBorrowModalOpen(false)}
              className="btn btn-secondary"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={borrowLoading}
              className="btn btn-primary"
            >
              {borrowLoading ? 'Processing...' : 'Borrow Book'}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  )
}
