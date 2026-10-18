'use client'

import { getApp, getApps, initializeApp } from 'firebase/app'
import {
  browserSessionPersistence,
  getAuth,
  getIdToken,
  setPersistence,
  type Auth,
} from 'firebase/auth'

let persistenceReady: Promise<void> | null = null

function firebaseOptions() {
  const options = {
    apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY,
    authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN,
    projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
    appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID,
    messagingSenderId: process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID,
    storageBucket: process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET,
  }

  if (!options.apiKey || !options.authDomain || !options.projectId || !options.appId) {
    throw new Error('Firebase client configuration is missing. Set the NEXT_PUBLIC_FIREBASE_* values.')
  }
  return options
}

export function getFirebaseAuth(): Auth {
  const app = getApps().length ? getApp() : initializeApp(firebaseOptions())
  return getAuth(app)
}

export function ensureFirebaseSessionPersistence(auth: Auth): Promise<void> {
  persistenceReady ??= setPersistence(auth, browserSessionPersistence)
  return persistenceReady
}

export async function getFirebaseIdToken(): Promise<string | undefined> {
  try {
    const auth = getFirebaseAuth()
    const user = auth.currentUser
    return user ? await getIdToken(user) : undefined
  } catch {
    return undefined
  }
}
