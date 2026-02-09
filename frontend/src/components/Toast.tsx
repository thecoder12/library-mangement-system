'use client'

import { useEffect, useState } from 'react'
import { 
  CheckCircleIcon, 
  XCircleIcon, 
  ExclamationTriangleIcon, 
  InformationCircleIcon,
  XMarkIcon 
} from '@heroicons/react/24/outline'

export type ToastType = 'success' | 'error' | 'warning' | 'info'

export interface ToastMessage {
  id: string
  type: ToastType
  message: string
  duration?: number
}

interface ToastProps {
  toast: ToastMessage
  onDismiss: (id: string) => void
}

const toastConfig = {
  success: {
    icon: CheckCircleIcon,
    bgColor: 'bg-green-50',
    borderColor: 'border-green-200',
    iconColor: 'text-green-500',
    textColor: 'text-green-800',
  },
  error: {
    icon: XCircleIcon,
    bgColor: 'bg-red-50',
    borderColor: 'border-red-200',
    iconColor: 'text-red-500',
    textColor: 'text-red-800',
  },
  warning: {
    icon: ExclamationTriangleIcon,
    bgColor: 'bg-amber-50',
    borderColor: 'border-amber-200',
    iconColor: 'text-amber-500',
    textColor: 'text-amber-800',
  },
  info: {
    icon: InformationCircleIcon,
    bgColor: 'bg-blue-50',
    borderColor: 'border-blue-200',
    iconColor: 'text-blue-500',
    textColor: 'text-blue-800',
  },
}

function Toast({ toast, onDismiss }: ToastProps) {
  const config = toastConfig[toast.type]
  const Icon = config.icon

  useEffect(() => {
    if (toast.duration !== 0) {
      const timer = setTimeout(() => {
        onDismiss(toast.id)
      }, toast.duration || 5000)

      return () => clearTimeout(timer)
    }
  }, [toast, onDismiss])

  return (
    <div
      className={`flex items-start p-4 rounded-lg border shadow-lg ${config.bgColor} ${config.borderColor} animate-slide-in`}
      role="alert"
    >
      <Icon className={`h-5 w-5 flex-shrink-0 ${config.iconColor}`} />
      <p className={`ml-3 text-sm font-medium ${config.textColor} flex-1`}>
        {toast.message}
      </p>
      <button
        onClick={() => onDismiss(toast.id)}
        className={`ml-4 inline-flex flex-shrink-0 ${config.textColor} hover:opacity-70 focus:outline-none`}
      >
        <XMarkIcon className="h-5 w-5" />
      </button>
    </div>
  )
}

interface ToastContainerProps {
  toasts: ToastMessage[]
  onDismiss: (id: string) => void
}

export function ToastContainer({ toasts, onDismiss }: ToastContainerProps) {
  if (toasts.length === 0) return null

  return (
    <div className="fixed bottom-4 right-4 z-50 flex flex-col space-y-2 max-w-sm">
      {toasts.map((toast) => (
        <Toast key={toast.id} toast={toast} onDismiss={onDismiss} />
      ))}
    </div>
  )
}

// Toast context and hook for global toast management
import { createContext, useContext, useCallback, ReactNode } from 'react'

interface ToastContextType {
  showToast: (type: ToastType, message: string, duration?: number) => void
  showSuccess: (message: string) => void
  showError: (message: string) => void
  showWarning: (message: string) => void
  showInfo: (message: string) => void
}

const ToastContext = createContext<ToastContextType | null>(null)

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<ToastMessage[]>([])

  const showToast = useCallback((type: ToastType, message: string, duration?: number) => {
    const id = Math.random().toString(36).substring(2, 9)
    setToasts((prev) => [...prev, { id, type, message, duration }])
  }, [])

  const dismissToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((toast) => toast.id !== id))
  }, [])

  const showSuccess = useCallback((message: string) => showToast('success', message), [showToast])
  const showError = useCallback((message: string) => showToast('error', message), [showToast])
  const showWarning = useCallback((message: string) => showToast('warning', message), [showToast])
  const showInfo = useCallback((message: string) => showToast('info', message), [showToast])

  return (
    <ToastContext.Provider value={{ showToast, showSuccess, showError, showWarning, showInfo }}>
      {children}
      <ToastContainer toasts={toasts} onDismiss={dismissToast} />
    </ToastContext.Provider>
  )
}

export function useToast(): ToastContextType {
  const context = useContext(ToastContext)
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider')
  }
  return context
}
