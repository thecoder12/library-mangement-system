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
import { FormField, Input } from '@/components/FormField'
import { 
  ValidationErrors, 
  validateRequired, 
  validateRange, 
  validateYear, 
  validateISBN,
  hasErrors,
  trimFormData 
} from '@/lib/validation'

export default function BooksPage() {
  const toast = useToast()
  const { confirm } = useConfirm()
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
  const [fieldErrors, setFieldErrors] = useState<ValidationErrors>({})

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
    setFieldErrors({})
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
    setFieldErrors({})
    setIsModalOpen(true)
  }

  const validateForm = (): boolean => {
    const errors: ValidationErrors = {
      title: validateRequired(formData.title, 'Title'),
      author: validateRequired(formData.author, 'Author'),
      isbn: validateISBN(formData.isbn),
      publishedYear: validateYear(formData.publishedYear, 'Published Year'),
      totalCopies: validateRange(formData.totalCopies, 1, 10000, 'Total Copies'),
    }
    
    setFieldErrors(errors)
    return !hasErrors(errors)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setFormError(null)

    // Trim and validate
    const trimmedData = trimFormData(formData)
    setFormData(trimmedData)
    
    if (!validateForm()) {
      return
    }

    setFormLoading(true)

    try {
      if (editingBook) {
        const updateData: UpdateBookRequest = {
          id: editingBook.id,
          ...trimmedData,
        }
        await libraryClient.updateBook(updateData)
        toast.success(`Book "${trimmedData.title}" updated successfully`)
      } else {
        await libraryClient.createBook(trimmedData)
        toast.success(`Book "${trimmedData.title}" created successfully`)
      }
      setIsModalOpen(false)
      loadBooks()
    } catch (err) {
      setFormError(err instanceof Error ? err.message : 'An error occurred')
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
      toast.success(`Book "${book.title}" deleted successfully`)
      loadBooks()
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Failed to delete book')
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
          
          <FormField label="Title" required error={fieldErrors.title}>
            <Input
              type="text"
              value={formData.title}
              onChange={(e) => {
                setFormData({ ...formData, title: e.target.value })
                if (fieldErrors.title) setFieldErrors({ ...fieldErrors, title: null })
              }}
              error={fieldErrors.title}
              placeholder="Enter book title"
            />
          </FormField>
          
          <FormField label="Author" required error={fieldErrors.author}>
            <Input
              type="text"
              value={formData.author}
              onChange={(e) => {
                setFormData({ ...formData, author: e.target.value })
                if (fieldErrors.author) setFieldErrors({ ...fieldErrors, author: null })
              }}
              error={fieldErrors.author}
              placeholder="Enter author name"
            />
          </FormField>
          
          <div className="grid grid-cols-2 gap-4">
            <FormField label="ISBN" error={fieldErrors.isbn}>
              <Input
                type="text"
                value={formData.isbn || ''}
                onChange={(e) => {
                  setFormData({ ...formData, isbn: e.target.value })
                  if (fieldErrors.isbn) setFieldErrors({ ...fieldErrors, isbn: null })
                }}
                error={fieldErrors.isbn}
                placeholder="e.g., 978-0-123456-78-9"
              />
            </FormField>
            <FormField label="Published Year" error={fieldErrors.publishedYear}>
              <Input
                type="number"
                value={formData.publishedYear || ''}
                onChange={(e) => {
                  setFormData({ ...formData, publishedYear: e.target.value ? parseInt(e.target.value) : undefined })
                  if (fieldErrors.publishedYear) setFieldErrors({ ...fieldErrors, publishedYear: null })
                }}
                error={fieldErrors.publishedYear}
                placeholder="e.g., 2024"
              />
            </FormField>
          </div>
          
          <div className="grid grid-cols-2 gap-4">
            <FormField label="Genre">
              <Input
                type="text"
                value={formData.genre || ''}
                onChange={(e) => setFormData({ ...formData, genre: e.target.value })}
                placeholder="e.g., Fiction, Non-fiction"
              />
            </FormField>
            <FormField label="Total Copies" error={fieldErrors.totalCopies}>
              <Input
                type="number"
                min="1"
                max="10000"
                value={formData.totalCopies || 1}
                onChange={(e) => {
                  setFormData({ ...formData, totalCopies: parseInt(e.target.value) || 1 })
                  if (fieldErrors.totalCopies) setFieldErrors({ ...fieldErrors, totalCopies: null })
                }}
                error={fieldErrors.totalCopies}
              />
            </FormField>
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
