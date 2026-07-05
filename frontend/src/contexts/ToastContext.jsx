import { createContext, useCallback, useContext, useMemo, useState } from 'react'
import { cn } from '@/lib/utils'

const ToastContext = createContext(null)

/** Notifications toast légères pour confirmer les actions utilisateur */
export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([])

  const showToast = useCallback((message, type = 'success') => {
    const id = Date.now()
    setToasts((prev) => [...prev, { id, message, type }])
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id))
    }, 3000)
  }, [])

  const value = useMemo(() => ({ showToast }), [showToast])

  return (
    <ToastContext.Provider value={value}>
      {children}
      <div className="fixed right-4 bottom-4 z-[100] flex flex-col gap-2">
        {toasts.map((toast) => (
          <div
            key={toast.id}
            className={cn(
              'animate-in fade-in slide-in-from-bottom-2 rounded-lg px-4 py-3 text-sm font-medium shadow-lg',
              toast.type === 'success'
                ? 'bg-green-600 text-white'
                : 'bg-destructive text-white'
            )}
          >
            {toast.message}
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  )
}

export function useToast() {
  const context = useContext(ToastContext)
  if (!context) {
    throw new Error('useToast doit être utilisé dans un ToastProvider')
  }
  return context
}
