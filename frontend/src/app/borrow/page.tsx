'use client'

import { useEffect, useState } from 'react'
import { ArrowPathIcon, CheckCircleIcon } from '@heroicons/react/24/outline'
import { libraryClient } from '@/lib/grpc-client'
import { Book, Member, BorrowRecord } from '@/lib/types'
import { Table } from '@/components/Table'
import { Pagination } from '@/components/Pagination'
import { Modal } from '@/components/Modal'

export default function BorrowPage() {
  const [records, setRecords] = useState<BorrowRecord[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [page, setPage] = useState(1)
  const [pageSize] = useState(10)
  const [totalCount, setTotalCount] = useState(0)
  const [statusFilter, setStatusFilter] = useState<string>('BORROWED')
  
  // Borrow modal state
  const [isBorrowModalOpen, setIsBorrowModalOpen] = useState(false)
  const [books, setBooks] = useState<Book[]>([])
  const [members, setMembers] = useState<Member[]>([])
  const [selectedBookId, setSelectedBookId] = useState<number | ''>('')
  const [selectedMemberId, setSelectedMemberId] = useState<number | ''>('')
  const [borrowLoading, setBorrowLoading] = useState(false)
  const [borrowError, setBorrowError] = useState<string | null>(null)

  useEffect(() => {
    loadRecords()
  }, [page, statusFilter])

  const loadRecords = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await libraryClient.listBorrowRecords({ 
        page, 
        pageSize, 
        status: statusFilter || undefined 
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
    setIsBorrowModalOpen(true)
    loadBooksAndMembers()
  }

  const handleBorrow = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!selectedBookId || !selectedMemberId) return

    setBorrowLoading(true)
    setBorrowError(null)

    try {
      await libraryClient.borrowBook({
        bookId: selectedBookId as number,
        memberId: selectedMemberId as number,
      })
      setIsBorrowModalOpen(false)
      loadRecords()
    } catch (err) {
      setBorrowError(err instanceof Error ? err.message : 'Failed to borrow book')
    } finally {
      setBorrowLoading(false)
    }
  }

  const handleReturn = async (record: BorrowRecord) => {
    if (!confirm('Are you sure you want to return this book?')) return

    try {
      await libraryClient.returnBook({ borrowId: record.id })
      loadRecords()
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to return book')
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

      {/* Status Filter */}
      <div className="mb-6">
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
          
          <div>
            <label className="label">Select Member *</label>
            <select
              required
              value={selectedMemberId}
              onChange={(e) => setSelectedMemberId(e.target.value ? parseInt(e.target.value) : '')}
              className="input"
            >
              <option value="">Choose a member...</option>
              {members.map((member) => (
                <option key={member.id} value={member.id}>
                  {member.name} ({member.email})
                </option>
              ))}
            </select>
            {members.length === 0 && (
              <p className="mt-1 text-sm text-gray-500">No active members available</p>
            )}
          </div>
          
          <div>
            <label className="label">Select Book *</label>
            <select
              required
              value={selectedBookId}
              onChange={(e) => setSelectedBookId(e.target.value ? parseInt(e.target.value) : '')}
              className="input"
            >
              <option value="">Choose a book...</option>
              {books.map((book) => (
                <option key={book.id} value={book.id}>
                  {book.title} by {book.author} ({book.availableCopies} available)
                </option>
              ))}
            </select>
            {books.length === 0 && (
              <p className="mt-1 text-sm text-gray-500">No books available for borrowing</p>
            )}
          </div>
          
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
              disabled={borrowLoading || !selectedBookId || !selectedMemberId}
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
