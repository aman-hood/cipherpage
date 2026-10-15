'use client'

import { useEffect, useState } from 'react'
import { createClient } from '@/lib/supabase/client'
import { User, Session } from '@supabase/supabase-js'

export type CipherPageUser = {
  id: number
  supabase_user_id: string
  name: string
  email: string
  role: string
}

export function useAuth() {
  const supabase = createClient()
  const [user, setUser] = useState<User | null>(null)
  const [session, setSession] = useState<Session | null>(null)
  const [cipherPageProfile, setCipherPageProfile] = useState<CipherPageUser | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Fetch initial session
    const initializeAuth = async () => {
      const { data: { session } } = await supabase.auth.getSession()
      setSession(session)
      setUser(session?.user ?? null)
      
      if (session) {
        await syncWithBackend(session.access_token)
      } else {
        setLoading(false)
      }
    }

    initializeAuth()

    // Listen for changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange(async (_event, newSession) => {
      setSession(newSession)
      setUser(newSession?.user ?? null)
      
      if (newSession) {
        await syncWithBackend(newSession.access_token)
      } else {
        setCipherPageProfile(null)
        setLoading(false)
      }
    })

    return () => {
      subscription.unsubscribe()
    }
  }, [])

  const syncWithBackend = async (token: string) => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'
      const response = await fetch(`${apiUrl}/api/v1/auth/me`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      if (response.ok) {
        const profile = await response.json()
        setCipherPageProfile(profile)
      } else {
        console.error('Failed to sync with backend:', await response.text())
      }
    } catch (error) {
      console.error('Error syncing with backend:', error)
    } finally {
      setLoading(false)
    }
  }

  const signOut = async () => {
    await supabase.auth.signOut()
  }

  return {
    user,
    session,
    profile: cipherPageProfile,
    loading,
    signOut,
    supabase
  }
}
