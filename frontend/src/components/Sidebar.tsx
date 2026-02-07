'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import clsx from 'clsx'
import {
  HomeIcon,
  BookOpenIcon,
  UserGroupIcon,
  ArrowPathIcon,
} from '@heroicons/react/24/outline'

const navigation = [
  { name: 'Dashboard', href: '/', icon: HomeIcon },
  { name: 'Books', href: '/books', icon: BookOpenIcon },
  { name: 'Members', href: '/members', icon: UserGroupIcon },
  { name: 'Borrow / Return', href: '/borrow', icon: ArrowPathIcon },
]

export function Sidebar() {
  const pathname = usePathname()

  return (
    <div className="flex flex-col w-64 bg-white border-r border-gray-200">
      <div className="flex items-center h-16 px-6 border-b border-gray-200">
        <BookOpenIcon className="h-8 w-8 text-primary-600" />
        <span className="ml-3 text-xl font-bold text-gray-900">Library</span>
      </div>
      
      <nav className="flex-1 px-3 py-4 space-y-1">
        {navigation.map((item) => {
          const isActive = pathname === item.href
          return (
            <Link
              key={item.name}
              href={item.href}
              className={clsx(
                'flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-colors',
                isActive
                  ? 'bg-primary-50 text-primary-700'
                  : 'text-gray-700 hover:bg-gray-100'
              )}
            >
              <item.icon className={clsx('h-5 w-5 mr-3', isActive ? 'text-primary-600' : 'text-gray-400')} />
              {item.name}
            </Link>
          )
        })}
      </nav>
      
      <div className="p-4 border-t border-gray-200">
        <p className="text-xs text-gray-500 text-center">
          Neighborhood Library v1.0
        </p>
      </div>
    </div>
  )
}
