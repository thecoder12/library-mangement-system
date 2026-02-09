'use client'

import { ReactNode } from 'react'
import clsx from 'clsx'

interface FormFieldProps {
  label: string
  required?: boolean
  error?: string | null
  children: ReactNode
  className?: string
}

export function FormField({ label, required, error, children, className }: FormFieldProps) {
  return (
    <div className={className}>
      <label className="label">
        {label}
        {required && <span className="text-red-500 ml-1">*</span>}
      </label>
      {children}
      {error && (
        <p className="mt-1 text-sm text-red-600">{error}</p>
      )}
    </div>
  )
}

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  error?: string | null
}

export function Input({ error, className, ...props }: InputProps) {
  return (
    <input
      {...props}
      className={clsx(
        'input',
        error && 'border-red-300 focus:border-red-500 focus:ring-red-500',
        className
      )}
    />
  )
}

interface TextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  error?: string | null
}

export function Textarea({ error, className, ...props }: TextareaProps) {
  return (
    <textarea
      {...props}
      className={clsx(
        'input',
        error && 'border-red-300 focus:border-red-500 focus:ring-red-500',
        className
      )}
    />
  )
}

interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  error?: string | null
}

export function Select({ error, className, children, ...props }: SelectProps) {
  return (
    <select
      {...props}
      className={clsx(
        'input',
        error && 'border-red-300 focus:border-red-500 focus:ring-red-500',
        className
      )}
    >
      {children}
    </select>
  )
}
