'use client'

import { useEffect, useState } from 'react'
import { PlusIcon, PencilIcon, TrashIcon, MagnifyingGlassIcon } from '@heroicons/react/24/outline'
import { libraryClient } from '@/lib/grpc-client'
import { Member, CreateMemberRequest, UpdateMemberRequest } from '@/lib/types'
import { Table } from '@/components/Table'
import { Pagination } from '@/components/Pagination'
import { Modal } from '@/components/Modal'
import { useToast } from '@/components/Toast'
import { useConfirm } from '@/components/ConfirmDialog'
import { FormField, Input, Textarea } from '@/components/FormField'
import { 
  ValidationErrors, 
  validateRequired, 
  validateEmail,
  validatePhone,
  hasErrors,
  trimFormData 
} from '@/lib/validation'

export default function MembersPage() {
  const toast = useToast()
  const { confirm } = useConfirm()
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
  const [fieldErrors, setFieldErrors] = useState<ValidationErrors>({})

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
    setFieldErrors({})
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
    setFieldErrors({})
    setIsModalOpen(true)
  }

  const validateForm = (): boolean => {
    const errors: ValidationErrors = {
      name: validateRequired(formData.name, 'Name'),
      email: validateEmail(formData.email),
      phone: validatePhone(formData.phone),
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
      if (editingMember) {
        const updateData: UpdateMemberRequest = {
          id: editingMember.id,
          name: trimmedData.name,
          email: trimmedData.email,
          phone: trimmedData.phone,
          address: trimmedData.address,
          isActive: trimmedData.isActive,
        }
        await libraryClient.updateMember(updateData)
        toast.success(`Member "${trimmedData.name}" updated successfully`)
      } else {
        await libraryClient.createMember(trimmedData)
        toast.success(`Member "${trimmedData.name}" created successfully`)
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
    const confirmed = await confirm({
      title: 'Delete Member',
      message: `Are you sure you want to delete "${member.name}"? This action cannot be undone.`,
      confirmText: 'Delete',
      cancelText: 'Cancel',
      variant: 'danger',
    })
    
    if (!confirmed) return

    try {
      const response = await libraryClient.deleteMember(member.id)
      if (response.deactivated) {
        toast.success(`Member "${member.name}" deactivated (has borrow history)`)
      } else {
        toast.success(`Member "${member.name}" deleted successfully`)
      }
      loadMembers()
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Failed to delete member')
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
          
          <FormField label="Name" required error={fieldErrors.name}>
            <Input
              type="text"
              value={formData.name}
              onChange={(e) => {
                setFormData({ ...formData, name: e.target.value })
                if (fieldErrors.name) setFieldErrors({ ...fieldErrors, name: null })
              }}
              error={fieldErrors.name}
              placeholder="Enter full name"
            />
          </FormField>
          
          <FormField label="Email" required error={fieldErrors.email}>
            <Input
              type="email"
              value={formData.email}
              onChange={(e) => {
                setFormData({ ...formData, email: e.target.value })
                if (fieldErrors.email) setFieldErrors({ ...fieldErrors, email: null })
              }}
              error={fieldErrors.email}
              placeholder="Enter email address"
            />
          </FormField>
          
          <FormField label="Phone" error={fieldErrors.phone}>
            <Input
              type="tel"
              value={formData.phone || ''}
              onChange={(e) => {
                setFormData({ ...formData, phone: e.target.value })
                if (fieldErrors.phone) setFieldErrors({ ...fieldErrors, phone: null })
              }}
              error={fieldErrors.phone}
              placeholder="Enter phone number"
            />
          </FormField>
          
          <FormField label="Address">
            <Textarea
              value={formData.address || ''}
              onChange={(e) => setFormData({ ...formData, address: e.target.value })}
              rows={2}
              placeholder="Enter address"
            />
          </FormField>
          
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
