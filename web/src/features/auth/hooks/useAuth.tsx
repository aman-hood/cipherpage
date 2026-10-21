'use client'

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
  type ReactNode,
} from 'react'
import { onAuthStateChanged, signOut as firebaseSignOut, type User } from 'firebase/auth'
import { ensureFirebaseSessionPersistence, getFirebaseAuth } from '@/lib/firebase/client'

const API_BASE_URL =   process.env.NEXT_PUBLIC_API_URL ||   process.env.NEXT_PUBLIC_API_BASE_URL ||   (process.env.NODE_ENV === 'development' ? 'http://localhost:8000' : '')  if (   typeof window !== 'undefined' &&   window.location.protocol === 'https:' &&   API_BASE_URL.startsWith('http://') ) {   throw new Error('Insecure API URL: HTTPS pages must use an HTTPS backend.') }  if (!API_BASE_URL) {   throw new Error('API URL is not configured. Set NEXT_PUBLIC_API_URL in your deployment environment.') }

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
  retryProfile: () => Promise<void>
  signOut: () => Promise<void>
  saveProfileName: (name: string) => Promise<CipherPageUser>
}

function profileRequestError(status: number): Error {
  if (status === 401) return new Error('Your sign-in session could not be verified. Try again, or sign out and sign in again.')
  if (status === 403) return new Error('This account is not currently allowed to access CipherPage.')
  if (status === 409) return new Error('This account needs an administrator-reviewed identity mapping.')
  if (status === 503) return new Error('Account services are temporarily unavailable. Check the backend Firebase and database configuration, then try again.')
  return new Error(`CipherPage could not load your profile (HTTP ${status}). Please try again.`)
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [profile, setProfile] = useState<CipherPageUser | null>(null)
  const [loading, setLoading] = useState(true)
  const [profileError, setProfileError] = useState<string | null>(null)
  const mountedRef = useRef(false)

  const loadProfile = useCallback(async (nextUser: User) => {
    if (mountedRef.current) {
      setLoading(true)
      setProfileError(null)
    }
    try {
      const idToken = await nextUser.getIdToken()
      const response = await fetch(`${API_BASE_URL}/api/v1/auth/me`, {
        headers: { Authorization: `Bearer ${idToken}` },
      })
      if (!response.ok) throw profileRequestError(response.status)
      const nextProfile = (await response.json()) as CipherPageUser
      if (mountedRef.current) setProfile(nextProfile)
    } catch (error) {
      if (mountedRef.current) {
        setProfileError(error instanceof Error ? error.message : 'Unable to load your profile.')
      }
    } finally {
      if (mountedRef.current) setLoading(false)
    }
  }, [])

  useEffect(() => {
    mountedRef.current = true
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

          await loadProfile(nextUser)
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
      mountedRef.current = false
      unsubscribe()
    }
  }, [loadProfile])

  const retryProfile = useCallback(async () => {
    const currentUser = getFirebaseAuth().currentUser
    if (!currentUser) {
      setProfileError('Your sign-in session ended. Sign in again to continue.')
      return
    }
    setLoading(true)
    setProfileError(null)
    try {
      await currentUser.getIdToken(true)
      await loadProfile(currentUser)
    } catch {
      setProfileError('Could not refresh your sign-in session. Sign out and sign in again.')
      setLoading(false)
    }
  }, [loadProfile])

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
    setUser(null);
    setProfile(null);
    setProfileError(null);
    await firebaseSignOut(auth)
    if (revokeError) throw revokeError
  }, [])

  const saveProfileName = useCallback(async (name: string) => {
    const currentUser = getFirebaseAuth().currentUser
    if (!currentUser) throw new Error('Sign in again to update your profile.')

    const idToken = await currentUser.getIdToken()
    const response = await fetch(`${API_BASE_URL}/api/v1/auth/me`, {
      method: 'PATCH',
      headers: {
        Authorization: `Bearer ${idToken}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ name }),
    })

    if (!response.ok) {
      if (response.status === 401) throw new Error('Your session expired. Sign in again and retry.')
      if (response.status === 422) throw new Error('Enter a name between 1 and 120 characters.')
      throw new Error('Unable to save your profile right now. Please try again.')
    }

    const updatedProfile = (await response.json()) as CipherPageUser
    setProfile(updatedProfile)
    return updatedProfile
  }, [])

  const value = useMemo(
    () => ({ user, profile, loading, profileError, retryProfile, signOut, saveProfileName }),
    [user, profile, loading, profileError, retryProfile, signOut, saveProfileName],
  )
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext)
  if (!context) throw new Error('useAuth must be used inside AuthProvider')
  return context
}
