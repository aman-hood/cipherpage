'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import {
  GoogleAuthProvider,
  reload,
  sendPasswordResetEmail,
  signInWithEmailAndPassword,
  signInWithPopup,
  signOut,
} from 'firebase/auth'
import { ensureFirebaseSessionPersistence, getFirebaseAuth } from '@/lib/firebase/client'

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [notice, setNotice] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const router = useRouter()

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    
    try {
      const auth = getFirebaseAuth()
      await ensureFirebaseSessionPersistence(auth)
      const credential = await signInWithEmailAndPassword(auth, email.trim(), password)
      await reload(credential.user)
      if (!credential.user.emailVerified) {
        await signOut(auth)
        throw new Error('Verify your email address before signing in.')
      }
      await credential.user.getIdToken(true)
      router.push('/dashboard')
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : 'Unable to sign in. Check your credentials and try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleGoogleLogin = async () => {
    setLoading(true)
    setError(null)
    try {
      const auth = getFirebaseAuth()
      await ensureFirebaseSessionPersistence(auth)
      const credential = await signInWithPopup(auth, new GoogleAuthProvider())
      await credential.user.getIdToken(true)
      router.push('/dashboard')
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : 'Google sign-in failed.')
    } finally {
      setLoading(false)
    }
  }

  const handlePasswordReset = async () => {
    setError(null)
    setNotice(null)
    if (!email.trim()) {
      setError('Enter your email address first.')
      return
    }
    try {
      await sendPasswordResetEmail(getFirebaseAuth(), email.trim())
      setNotice('If an account exists for that address, Firebase will send a password reset email.')
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : 'Unable to send a password reset email.')
    }
  }


  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50 dark:bg-gray-900 px-4">
      <div className="w-full max-w-md space-y-8 bg-white dark:bg-gray-800 p-8 rounded-xl shadow-lg">
        <div className="text-center">
          <h2 className="text-3xl font-extrabold text-gray-900 dark:text-white">
            CipherPage
          </h2>
          <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
            LAG — Learn • Apply • Grow
          </p>
        </div>
        
        <form className="mt-8 space-y-6" onSubmit={handleLogin}>
          {error && (
            <div className="bg-red-100 text-red-700 p-3 rounded text-sm">
              {error}
            </div>
          )}
          {notice && <div className="bg-green-100 text-green-700 p-3 rounded text-sm">{notice}</div>}
          <div className="space-y-4">
            <div>
              <label htmlFor="email" className="sr-only">Email address</label>
              <input
                id="email"
                name="email"
                type="email"
                required
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-md bg-white dark:bg-gray-900 text-gray-900 dark:text-white focus:ring-blue-500 focus:border-blue-500"
                placeholder="Email address"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>
            <div>
              <label htmlFor="password" className="sr-only">Password</label>
              <input
                id="password"
                name="password"
                type="password"
                required
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-md bg-white dark:bg-gray-900 text-gray-900 dark:text-white focus:ring-blue-500 focus:border-blue-500"
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>
          </div>

          <div className="text-right">
            <button type="button" onClick={handlePasswordReset} className="text-sm text-blue-600 hover:text-blue-500">
              Forgot password?
            </button>
          </div>

          <div>
            <button
              type="submit"
              disabled={loading}
              className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
            >
              {loading ? 'Signing in...' : 'Sign in'}
            </button>
          </div>
        </form>

        <button
          type="button"
          disabled={loading}
          onClick={handleGoogleLogin}
          className="w-full flex justify-center py-2 px-4 border border-gray-300 dark:border-gray-700 rounded-md text-sm font-medium text-gray-900 dark:text-white disabled:opacity-50"
        >
          Continue with Google
        </button>



        <p className="mt-2 text-center text-sm text-gray-600 dark:text-gray-400">
          Don&apos;t have an account?{' '}
          <Link href="/register" className="font-medium text-blue-600 hover:text-blue-500">
            Sign up
          </Link>
        </p>
      </div>
    </div>
  )
}
