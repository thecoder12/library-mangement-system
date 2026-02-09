import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { Sidebar } from '@/components/Sidebar'
import { ToastProvider } from '@/components/Toast'
import { ConfirmProvider } from '@/components/ConfirmDialog'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Neighborhood Library',
  description: 'Library Management System',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <ToastProvider>
          <ConfirmProvider>
            <div className="flex h-screen bg-gray-50">
              <Sidebar />
              <main className="flex-1 overflow-auto">
                <div className="p-8">
                  {children}
                </div>
              </main>
            </div>
          </ConfirmProvider>
        </ToastProvider>
      </body>
    </html>
  )
}
