'use client'

import { ReactNode } from 'react'
import { ToastProvider } from './Toast'
import { ConfirmDialogProvider } from './ConfirmDialog'

interface ProvidersProps {
  children: ReactNode
}

/**
 * Client-side providers wrapper for the application.
 * Includes Toast notifications and Confirm dialogs.
 */
export function Providers({ children }: ProvidersProps) {
  return (
    <ToastProvider>
      <ConfirmDialogProvider>
        {children}
      </ConfirmDialogProvider>
    </ToastProvider>
  )
}
