'use client'

import { useEffect, useState } from 'react'
import { BookOpenIcon, UserGroupIcon, ArrowPathIcon } from '@heroicons/react/24/outline'
import { libraryClient } from '@/lib/grpc-client'

interface Stats {
  totalBooks: number
  totalMembers: number
  activeBorrows: number
}

export default function Dashboard() {
  const [stats, setStats] = useState<Stats>({ totalBooks: 0, totalMembers: 0, activeBorrows: 0 })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadStats()
  }, [])

  const loadStats = async () => {
    setLoading(true)
    setError(null)
    try {
      const [booksRes, membersRes, borrowsRes] = await Promise.all([
        libraryClient.listBooks({ page: 1, pageSize: 1 }),
        libraryClient.listMembers({ page: 1, pageSize: 1 }),
        libraryClient.listBorrowRecords({ page: 1, pageSize: 1, status: 'BORROWED' }),
      ])
      
      setStats({
        totalBooks: booksRes.totalCount,
        totalMembers: membersRes.totalCount,
        activeBorrows: borrowsRes.totalCount,
      })
    } catch (err) {
      setError('Failed to load statistics. Make sure the backend is running.')
      console.error('Error loading stats:', err)
    } finally {
      setLoading(false)
    }
  }

  const statCards = [
    { name: 'Total Books', value: stats.totalBooks, icon: BookOpenIcon, color: 'bg-blue-500' },
    { name: 'Total Members', value: stats.totalMembers, icon: UserGroupIcon, color: 'bg-green-500' },
    { name: 'Active Borrows', value: stats.activeBorrows, icon: ArrowPathIcon, color: 'bg-amber-500' },
  ]

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-2 text-gray-600">Welcome to the Neighborhood Library Management System</p>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-700">{error}</p>
          <button onClick={loadStats} className="mt-2 text-red-600 hover:text-red-800 font-medium">
            Try Again
          </button>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        {statCards.map((stat) => (
          <div key={stat.name} className="card p-6">
            <div className="flex items-center">
              <div className={`${stat.color} p-3 rounded-lg`}>
                <stat.icon className="h-6 w-6 text-white" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">{stat.name}</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {loading ? '...' : stat.value}
                </p>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="card p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <a href="/books" className="btn btn-secondary">
            <BookOpenIcon className="h-5 w-5 mr-2" />
            Manage Books
          </a>
          <a href="/members" className="btn btn-secondary">
            <UserGroupIcon className="h-5 w-5 mr-2" />
            Manage Members
          </a>
          <a href="/borrow" className="btn btn-primary">
            <ArrowPathIcon className="h-5 w-5 mr-2" />
            Borrow / Return
          </a>
        </div>
      </div>
    </div>
  )
}
