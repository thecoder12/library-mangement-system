'use client'

import { useEffect, useState } from 'react'
import { PlusIcon, PencilIcon, TrashIcon, MagnifyingGlassIcon } from '@heroicons/react/24/outline'
import { libraryClient } from '@/lib/grpc-client'
import { Member, CreateMemberRequest, UpdateMemberRequest } from '@/lib/types'
import { Table } from '@/components/Table'
import { Pagination } from '@/components/Pagination'
import { Modal } from '@/components/Modal'

export default function MembersPage() {
  const [members, setMembers] = useState<Member[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [page, setPage] = useState(1)
  const [pageSize] = useState(10)
  const [totalCount, setTotalCount] = useState(0)
  const [search, setSearch] = useState('')
  const [searchInput, setSearchInput] = useState('')
  
  // Modal state
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingMember, setEditingMember] = useState<Member | null>(null)
  const [formData, setFormData] = useState<CreateMemberRequest & { isActive?: boolean }>({
    name: '',
    email: '',
    phone: '',
    address: '',
  })
  const [formError, setFormError] = useState<string | null>(null)
  const [formLoading, setFormLoading] = useState(false)

  useEffect(() => {
    loadMembers()
  }, [page, search])

  const loadMembers = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await libraryClient.listMembers({ page, pageSize, search })
      setMembers(response.members)
      setTotalCount(response.totalCount)
    } catch (err) {
      setError('Failed to load members. Make sure the backend is running.')
      console.error('Error loading members:', err)
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
    setEditingMember(null)
    setFormData({
      name: '',
      email: '',
      phone: '',
      address: '',
    })
    setFormError(null)
    setIsModalOpen(true)
  }

  const openEditModal = (member: Member) => {
    setEditingMember(member)
    setFormData({
      name: member.name,
      email: member.email,
      phone: member.phone || '',
      address: member.address || '',
      isActive: member.isActive,
    })
    setFormError(null)
    setIsModalOpen(true)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setFormLoading(true)
    setFormError(null)

    try {
      if (editingMember) {
        const updateData: UpdateMemberRequest = {
          id: editingMember.id,
          name: formData.name,
          email: formData.email,
          phone: formData.phone,
          address: formData.address,
          isActive: formData.isActive,
        }
        await libraryClient.updateMember(updateData)
      } else {
        await libraryClient.createMember(formData)
      }
      setIsModalOpen(false)
      loadMembers()
    } catch (err) {
      setFormError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setFormLoading(false)
    }
  }

  const handleDelete = async (member: Member) => {
    if (!confirm(`Are you sure you want to delete "${member.name}"?`)) return

    try {
      await libraryClient.deleteMember(member.id)
      loadMembers()
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to delete member')
    }
  }

  const columns = [
    { header: 'Name', accessor: 'name' as keyof Member },
    { header: 'Email', accessor: 'email' as keyof Member },
    { header: 'Phone', accessor: (row: Member) => row.phone || '-' },
    { 
      header: 'Status', 
      accessor: (row: Member) => (
        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
          row.isActive ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
        }`}>
          {row.isActive ? 'Active' : 'Inactive'}
        </span>
      )
    },
    { 
      header: 'Member Since', 
      accessor: (row: Member) => row.membershipDate ? new Date(row.membershipDate).toLocaleDateString() : '-'
    },
  ]

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Members</h1>
          <p className="mt-1 text-gray-600">Manage library members</p>
        </div>
        <button onClick={openCreateModal} className="btn btn-primary">
          <PlusIcon className="h-5 w-5 mr-2" />
          Add Member
        </button>
      </div>

      {/* Search */}
      <form onSubmit={handleSearch} className="mb-6">
        <div className="relative max-w-md">
          <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
          <input
            type="text"
            placeholder="Search by name or email..."
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
          data={members}
          keyExtractor={(member) => member.id}
          loading={loading}
          emptyMessage="No members found"
          actions={(member) => (
            <div className="flex space-x-2">
              <button
                onClick={() => openEditModal(member)}
                className="text-primary-600 hover:text-primary-800"
              >
                <PencilIcon className="h-5 w-5" />
              </button>
              <button
                onClick={() => handleDelete(member)}
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
        title={editingMember ? 'Edit Member' : 'Add Member'}
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          {formError && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
              {formError}
            </div>
          )}
          
          <div>
            <label className="label">Name *</label>
            <input
              type="text"
              required
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="input"
            />
          </div>
          
          <div>
            <label className="label">Email *</label>
            <input
              type="email"
              required
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              className="input"
            />
          </div>
          
          <div>
            <label className="label">Phone</label>
            <input
              type="tel"
              value={formData.phone || ''}
              onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
              className="input"
            />
          </div>
          
          <div>
            <label className="label">Address</label>
            <textarea
              value={formData.address || ''}
              onChange={(e) => setFormData({ ...formData, address: e.target.value })}
              className="input"
              rows={2}
            />
          </div>
          
          {editingMember && (
            <div className="flex items-center">
              <input
                type="checkbox"
                id="isActive"
                checked={formData.isActive ?? true}
                onChange={(e) => setFormData({ ...formData, isActive: e.target.checked })}
                className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
              />
              <label htmlFor="isActive" className="ml-2 text-sm text-gray-700">
                Active Member
              </label>
            </div>
          )}
          
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
              {formLoading ? 'Saving...' : (editingMember ? 'Update' : 'Create')}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  )
}
