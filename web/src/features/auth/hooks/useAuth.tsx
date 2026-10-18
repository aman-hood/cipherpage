'use client'

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react'
import { onAuthStateChanged, signOut as firebaseSignOut, type User } from 'firebase/auth'
import { ensureFirebaseSessionPersistence, getFirebaseAuth } from '@/lib/firebase/client'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'

export type CipherPageUser = {
  id: number
  firebase_uid: string
  name: string
  email: string
  role: string
}

type AuthContextValue = {
  user: User | null
  profile: CipherPageUser | null
  loading: boolean
  profileError: string | null
  signOut: () => Promise<void>
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [profile, setProfile] = useState<CipherPageUser | null>(null)
  const [loading, setLoading] = useState(true)
  const [profileError, setProfileError] = useState<string | null>(null)

  useEffect(() => {
    let mounted = true
    let unsubscribe = () => {}

    const initialize = async () => {
      try {
        const auth = getFirebaseAuth()
        await ensureFirebaseSessionPersistence(auth)
        if (!mounted) return

        unsubscribe = onAuthStateChanged(auth, async (nextUser) => {
          setUser(nextUser)
          setProfile(null)
          setProfileError(null)
          if (!nextUser) {
            setLoading(false)
            return
          }

          if (!nextUser.emailVerified) {
            setProfileError('Verify your email address before using CipherPage.')
            setLoading(false)
            return
          }

          setLoading(true)
          try {
            const idToken = await nextUser.getIdToken()
            const response = await fetch(`${API_BASE_URL}/api/v1/auth/me`, {
              headers: { Authorization: `Bearer ${idToken}` },
            })
            if (!response.ok) {
              throw new Error(response.status === 409
                ? 'This account needs an administrator-reviewed identity mapping.'
                : 'Unable to load your CipherPage profile.')
            }
            const nextProfile = (await response.json()) as CipherPageUser
            if (mounted) setProfile(nextProfile)
          } catch (error) {
            if (mounted) {
              setProfileError(error instanceof Error ? error.message : 'Unable to load your profile.')
            }
          } finally {
            if (mounted) setLoading(false)
          }
        })
      } catch (error) {
        if (mounted) {
          setProfileError(error instanceof Error ? error.message : 'Firebase authentication is unavailable.')
          setLoading(false)
        }
      }
    }

    void initialize()
    return () => {
      mounted = false
      unsubscribe()
    }
  }, [])

  const signOut = useCallback(async () => {
    const auth = getFirebaseAuth()
    const currentUser = auth.currentUser
    let revokeError: Error | null = null
    if (currentUser) {
      try {
        const idToken = await currentUser.getIdToken()
        const response = await fetch(`${API_BASE_URL}/api/v1/auth/logout`, {
          method: 'POST',
          headers: { Authorization: `Bearer ${idToken}` },
        })
        if (!response.ok) revokeError = new Error('The server could not revoke the Firebase session.')
      } catch {
        revokeError = new Error('The server could not revoke the Firebase session.')
      }
    }
    await firebaseSignOut(auth)
    if (revokeError) throw revokeError
  }, [])

  const value = useMemo(
    () => ({ user, profile, loading, profileError, signOut }),
    [user, profile, loading, profileError, signOut],
  )
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext)
  if (!context) throw new Error('useAuth must be used inside AuthProvider')
  return context
}
