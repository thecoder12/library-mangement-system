'use client'

import { createContext, useContext, useState, useCallback, ReactNode } from 'react'
import { ExclamationTriangleIcon } from '@heroicons/react/24/outline'

interface ConfirmDialogOptions {
  title?: string
  message: string
  confirmText?: string
  cancelText?: string
  variant?: 'danger' | 'warning' | 'info'
}

interface ConfirmDialogState extends ConfirmDialogOptions {
  isOpen: boolean
  resolve: ((value: boolean) => void) | null
}

interface ConfirmDialogContextType {
  confirm: (options: ConfirmDialogOptions) => Promise<boolean>
}

const ConfirmDialogContext = createContext<ConfirmDialogContextType | null>(null)

const variantConfig = {
  danger: {
    iconBg: 'bg-red-100',
    iconColor: 'text-red-600',
    buttonColor: 'bg-red-600 hover:bg-red-700 focus:ring-red-500',
  },
  warning: {
    iconBg: 'bg-amber-100',
    iconColor: 'text-amber-600',
    buttonColor: 'bg-amber-600 hover:bg-amber-700 focus:ring-amber-500',
  },
  info: {
    iconBg: 'bg-blue-100',
    iconColor: 'text-blue-600',
    buttonColor: 'bg-blue-600 hover:bg-blue-700 focus:ring-blue-500',
  },
}

function ConfirmDialogComponent({
  state,
  onClose,
}: {
  state: ConfirmDialogState
  onClose: (confirmed: boolean) => void
}) {
  if (!state.isOpen) return null

  const variant = state.variant || 'danger'
  const config = variantConfig[variant]

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex min-h-screen items-center justify-center p-4">
        {/* Backdrop */}
        <div
          className="fixed inset-0 bg-black/50 transition-opacity"
          onClick={() => onClose(false)}
        />

        {/* Dialog */}
        <div className="relative bg-white rounded-xl shadow-xl max-w-md w-full mx-auto transform transition-all">
          <div className="p-6">
            <div className="flex items-start space-x-4">
              {/* Icon */}
              <div className={`flex-shrink-0 w-12 h-12 rounded-full ${config.iconBg} flex items-center justify-center`}>
                <ExclamationTriangleIcon className={`h-6 w-6 ${config.iconColor}`} />
              </div>

              {/* Content */}
              <div className="flex-1 pt-1">
                <h3 className="text-lg font-semibold text-gray-900">
                  {state.title || 'Confirm Action'}
                </h3>
                <p className="mt-2 text-sm text-gray-600">
                  {state.message}
                </p>
              </div>
            </div>

            {/* Actions */}
            <div className="mt-6 flex justify-end space-x-3">
              <button
                type="button"
                onClick={() => onClose(false)}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500 transition-colors"
              >
                {state.cancelText || 'Cancel'}
              </button>
              <button
                type="button"
                onClick={() => onClose(true)}
                className={`px-4 py-2 text-sm font-medium text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-offset-2 transition-colors ${config.buttonColor}`}
              >
                {state.confirmText || 'Confirm'}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export function ConfirmDialogProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<ConfirmDialogState>({
    isOpen: false,
    message: '',
    resolve: null,
  })

  const confirm = useCallback((options: ConfirmDialogOptions): Promise<boolean> => {
    return new Promise((resolve) => {
      setState({
        ...options,
        isOpen: true,
        resolve,
      })
    })
  }, [])

  const handleClose = useCallback((confirmed: boolean) => {
    if (state.resolve) {
      state.resolve(confirmed)
    }
    setState((prev) => ({
      ...prev,
      isOpen: false,
      resolve: null,
    }))
  }, [state.resolve])

  return (
    <ConfirmDialogContext.Provider value={{ confirm }}>
      {children}
      <ConfirmDialogComponent state={state} onClose={handleClose} />
    </ConfirmDialogContext.Provider>
  )
}

export function useConfirm(): (options: ConfirmDialogOptions) => Promise<boolean> {
  const context = useContext(ConfirmDialogContext)
  if (!context) {
    throw new Error('useConfirm must be used within a ConfirmDialogProvider')
  }
  return context.confirm
}
