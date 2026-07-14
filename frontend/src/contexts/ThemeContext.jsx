import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'
import userService from '@/src/services/user'
import { useAuth } from '@/src/contexts/AuthContext'

const ThemeContext = createContext(null)

/**
 * Applique ou retire la classe `dark` sur <html>.
 * Le CSS index.css repose sur .dark pour switcher les variables de couleur.
 */
function applyTheme(theme) {
  if (theme === 'dark') {
    document.documentElement.classList.add('dark')
  } else {
    document.documentElement.classList.remove('dark')
  }
}

export function ThemeProvider({ children }) {
  const { isAuthenticated } = useAuth()
  // Initialisation depuis localStorage pour éviter le flash au démarrage
  const [theme, setTheme] = useState(() => {
    const stored = localStorage.getItem('theme')
    return stored === 'dark' ? 'dark' : 'light'
  })

  // Applique le thème dès le rendu initial (synchrone)
  useEffect(() => {
    applyTheme(theme)
  }, [theme])

  // Récupère le thème depuis le backend après connexion
  useEffect(() => {
    if (!isAuthenticated) return
    userService.getTheme().then((data) => {
      const serverTheme = data.theme
      setTheme(serverTheme)
      localStorage.setItem('theme', serverTheme)
      applyTheme(serverTheme)
    }).catch(() => {
      // Silencieux — on garde le thème local
    })
  }, [isAuthenticated])

  const toggleTheme = useCallback(async () => {
    const next = theme === 'light' ? 'dark' : 'light'
    // Mise à jour immédiate de l'interface
    setTheme(next)
    localStorage.setItem('theme', next)
    applyTheme(next)

    // Sauvegarde en arrière-plan — silencieuse en cas d'erreur
    if (isAuthenticated) {
      userService.updateTheme(next).catch(() => {})
    }
  }, [theme, isAuthenticated])

  const value = useMemo(() => ({ theme, toggleTheme }), [theme, toggleTheme])

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>
}

export function useTheme() {
  const context = useContext(ThemeContext)
  if (!context) {
    throw new Error('useTheme doit être utilisé dans un ThemeProvider')
  }
  return context
}
