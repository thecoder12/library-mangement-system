'use client'

import { useEffect, useState } from 'react'
import { PlusIcon, PencilIcon, TrashIcon, MagnifyingGlassIcon } from '@heroicons/react/24/outline'
import { libraryClient } from '@/lib/grpc-client'
import { Book, CreateBookRequest, UpdateBookRequest } from '@/lib/types'
import { Table } from '@/components/Table'
import { Pagination } from '@/components/Pagination'
import { Modal } from '@/components/Modal'
import { useToast } from '@/components/Toast'
import { useConfirm } from '@/components/ConfirmDialog'
import { validateField, validateISBN, trimFormData, isEmptyOrWhitespace } from '@/lib/validation'

export default function BooksPage() {
  const [books, setBooks] = useState<Book[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [page, setPage] = useState(1)
  const [pageSize] = useState(10)
  const [totalCount, setTotalCount] = useState(0)
  const [search, setSearch] = useState('')
  const [searchInput, setSearchInput] = useState('')
  
  // Modal state
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingBook, setEditingBook] = useState<Book | null>(null)
  const [formData, setFormData] = useState<CreateBookRequest>({
    title: '',
    author: '',
    isbn: '',
    publishedYear: undefined,
    genre: '',
    totalCopies: 1,
  })
  const [formError, setFormError] = useState<string | null>(null)
  const [formLoading, setFormLoading] = useState(false)

  // UI feedback hooks
  const { showError, showSuccess } = useToast()
  const confirm = useConfirm()

  useEffect(() => {
    loadBooks()
  }, [page, search])

  const loadBooks = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await libraryClient.listBooks({ page, pageSize, search })
      setBooks(response.books)
      setTotalCount(response.totalCount)
    } catch (err) {
      setError('Failed to load books. Make sure the backend is running.')
      console.error('Error loading books:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    setSearch(searchInput)
    setPage(1)
  }

  const openCreateModal = () => {
    setEditingBook(null)
    setFormData({
      title: '',
      author: '',
      isbn: '',
      publishedYear: undefined,
      genre: '',
      totalCopies: 1,
    })
    setFormError(null)
    setIsModalOpen(true)
  }

  const openEditModal = (book: Book) => {
    setEditingBook(book)
    setFormData({
      title: book.title,
      author: book.author,
      isbn: book.isbn || '',
      publishedYear: book.publishedYear || undefined,
      genre: book.genre || '',
      totalCopies: book.totalCopies,
    })
    setFormError(null)
    setIsModalOpen(true)
  }

  const validateForm = (): boolean => {
    // Validate required fields with trimming
    const titleValidation = validateField({
      value: formData.title,
      fieldName: 'Title',
      required: true,
      minLength: 1,
    })
    if (!titleValidation.isValid) {
      setFormError(titleValidation.error || 'Invalid title')
      return false
    }

    const authorValidation = validateField({
      value: formData.author,
      fieldName: 'Author',
      required: true,
      minLength: 1,
    })
    if (!authorValidation.isValid) {
      setFormError(authorValidation.error || 'Invalid author')
      return false
    }

    // Validate ISBN format if provided
    if (formData.isbn && !isEmptyOrWhitespace(formData.isbn)) {
      const isbnValidation = validateISBN(formData.isbn)
      if (!isbnValidation.isValid) {
        setFormError(isbnValidation.error || 'Invalid ISBN')
        return false
      }
    }

<<<<<<< HEAD
    // Validate Published Year if provided
    if (formData.publishedYear !== undefined && formData.publishedYear !== null) {
      const currentYear = new Date().getFullYear()
      if (formData.publishedYear < 1000) {
        setFormError('Published Year must be 1000 or later')
        return false
      }
      if (formData.publishedYear > currentYear) {
        setFormError(`Published Year cannot be in the future (max: ${currentYear})`)
        return false
      }
    }

    // Validate Total Copies - must be between 1 and 10000
    const totalCopies = formData.totalCopies || 1
    if (totalCopies < 1) {
      setFormError('Total Copies must be at least 1')
      return false
    }
    if (totalCopies > 10000) {
      setFormError('Total Copies cannot exceed 10,000')
      return false
    }

=======
>>>>>>> 0d1e90b (feat(frontend): Implement FE feedback improvements)
    return true
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setFormError(null)

    // Validate form with custom validation
    if (!validateForm()) {
      return
    }

    setFormLoading(true)

    try {
      // Trim all string fields before submission
      const trimmedData = trimFormData(formData)
      
      if (editingBook) {
        const updateData: UpdateBookRequest = {
          id: editingBook.id,
          ...trimmedData,
        }
        await libraryClient.updateBook(updateData)
        showSuccess('Book updated successfully')
      } else {
        await libraryClient.createBook(trimmedData)
        showSuccess('Book created successfully')
      }
      setIsModalOpen(false)
      loadBooks()
    } catch (err) {
      // Handle different error types
      if (err instanceof Error) {
        setFormError(err.message)
      } else if (typeof err === 'object' && err !== null) {
        // Handle object errors from API
        const errorObj = err as Record<string, unknown>
        setFormError(errorObj.message as string || errorObj.detail as string || 'An error occurred')
      } else {
        setFormError('An error occurred')
      }
    } finally {
      setFormLoading(false)
    }
  }

  const handleDelete = async (book: Book) => {
    const confirmed = await confirm({
      title: 'Delete Book',
      message: `Are you sure you want to delete "${book.title}"? This action cannot be undone.`,
      confirmText: 'Delete',
      cancelText: 'Cancel',
      variant: 'danger',
    })

    if (!confirmed) return

    try {
      await libraryClient.deleteBook(book.id)
      showSuccess(`"${book.title}" has been deleted`)
      loadBooks()
    } catch (err) {
      showError(err instanceof Error ? err.message : 'Failed to delete book')
    }
  }

  const columns = [
    { header: 'Title', accessor: 'title' as keyof Book },
    { header: 'Author', accessor: 'author' as keyof Book },
    { header: 'ISBN', accessor: (row: Book) => row.isbn || '-' },
    { header: 'Genre', accessor: (row: Book) => row.genre || '-' },
    { 
      header: 'Availability', 
      accessor: (row: Book) => (
        <span className={row.availableCopies > 0 ? 'text-green-600' : 'text-red-600'}>
          {row.availableCopies} / {row.totalCopies}
        </span>
      )
    },
  ]

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Books</h1>
          <p className="mt-1 text-gray-600">Manage library books</p>
        </div>
        <button onClick={openCreateModal} className="btn btn-primary">
          <PlusIcon className="h-5 w-5 mr-2" />
          Add Book
        </button>
      </div>

      {/* Search */}
      <form onSubmit={handleSearch} className="mb-6">
        <div className="relative max-w-md">
          <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
          <input
            type="text"
            placeholder="Search by title or author..."
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            className="input pl-10"
          />
        </div>
      </form>

      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-700">{error}</p>
        </div>
      )}

      <div className="card">
        <Table
          columns={columns}
          data={books}
          keyExtractor={(book) => book.id}
          loading={loading}
          emptyMessage="No books found"
          actions={(book) => (
            <div className="flex space-x-2">
              <button
                onClick={() => openEditModal(book)}
                className="text-primary-600 hover:text-primary-800"
              >
                <PencilIcon className="h-5 w-5" />
              </button>
              <button
                onClick={() => handleDelete(book)}
                className="text-red-600 hover:text-red-800"
              >
                <TrashIcon className="h-5 w-5" />
              </button>
            </div>
          )}
        />
        <Pagination
          page={page}
          pageSize={pageSize}
          totalCount={totalCount}
          onPageChange={setPage}
        />
      </div>

      {/* Create/Edit Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title={editingBook ? 'Edit Book' : 'Add Book'}
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          {formError && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
              {formError}
            </div>
          )}
          
          <div>
            <label className="label">Title *</label>
            <input
              type="text"
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              className={`input ${formError && isEmptyOrWhitespace(formData.title) ? 'input-error' : ''}`}
              placeholder="Enter book title"
            />
          </div>
          
          <div>
            <label className="label">Author *</label>
            <input
              type="text"
              value={formData.author}
              onChange={(e) => setFormData({ ...formData, author: e.target.value })}
              className={`input ${formError && isEmptyOrWhitespace(formData.author) ? 'input-error' : ''}`}
              placeholder="Enter author name"
            />
          </div>
          
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="label">ISBN</label>
              <input
                type="text"
                value={formData.isbn || ''}
                onChange={(e) => setFormData({ ...formData, isbn: e.target.value })}
                className="input"
                placeholder="e.g., 978-0-123456-78-9"
              />
              <p className="mt-1 text-xs text-gray-500">Optional - 10 or 13 digits</p>
            </div>
            <div>
              <label className="label">Published Year</label>
              <input
                type="number"
                min="1000"
                max={new Date().getFullYear()}
                value={formData.publishedYear || ''}
                onChange={(e) => setFormData({ ...formData, publishedYear: e.target.value ? parseInt(e.target.value) : undefined })}
                className="input"
                placeholder="e.g., 2024"
              />
              <p className="mt-1 text-xs text-gray-500">1000 - {new Date().getFullYear()}</p>
            </div>
          </div>
          
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="label">Genre</label>
              <input
                type="text"
                value={formData.genre || ''}
                onChange={(e) => setFormData({ ...formData, genre: e.target.value })}
                className="input"
                placeholder="e.g., Fiction"
              />
            </div>
            <div>
              <label className="label">Total Copies</label>
              <input
                type="number"
                min="1"
                max="10000"
                value={formData.totalCopies || 1}
                onChange={(e) => setFormData({ ...formData, totalCopies: parseInt(e.target.value) || 1 })}
                className="input"
              />
              <p className="mt-1 text-xs text-gray-500">Max 10,000 copies</p>
            </div>
          </div>
          
          <div className="flex justify-end space-x-3 pt-4">
            <button
              type="button"
              onClick={() => setIsModalOpen(false)}
              className="btn btn-secondary"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={formLoading}
              className="btn btn-primary"
            >
              {formLoading ? 'Saving...' : (editingBook ? 'Update' : 'Create')}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  )
}
