'use client'

import { useEffect, useState } from 'react'
import { PlusIcon, PencilIcon, TrashIcon, MagnifyingGlassIcon } from '@heroicons/react/24/outline'
import { libraryClient } from '@/lib/grpc-client'
import { Book, CreateBookRequest, UpdateBookRequest } from '@/lib/types'
import { Table } from '@/components/Table'
import { Pagination } from '@/components/Pagination'
import { Modal } from '@/components/Modal'

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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setFormLoading(true)
    setFormError(null)

    try {
      if (editingBook) {
        const updateData: UpdateBookRequest = {
          id: editingBook.id,
          ...formData,
        }
        await libraryClient.updateBook(updateData)
      } else {
        await libraryClient.createBook(formData)
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
    if (!confirm(`Are you sure you want to delete "${book.title}"?`)) return

    try {
      await libraryClient.deleteBook(book.id)
      loadBooks()
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to delete book')
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
              required
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              className="input"
            />
          </div>
          
          <div>
            <label className="label">Author *</label>
            <input
              type="text"
              required
              value={formData.author}
              onChange={(e) => setFormData({ ...formData, author: e.target.value })}
              className="input"
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
              />
            </div>
            <div>
              <label className="label">Published Year</label>
              <input
                type="number"
                value={formData.publishedYear || ''}
                onChange={(e) => setFormData({ ...formData, publishedYear: e.target.value ? parseInt(e.target.value) : undefined })}
                className="input"
              />
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
              />
            </div>
            <div>
              <label className="label">Total Copies</label>
              <input
                type="number"
                min="1"
                value={formData.totalCopies || 1}
                onChange={(e) => setFormData({ ...formData, totalCopies: parseInt(e.target.value) || 1 })}
                className="input"
              />
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
