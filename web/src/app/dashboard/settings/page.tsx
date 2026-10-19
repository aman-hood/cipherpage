'use client'

import { useState, type FormEvent } from 'react'
import { sendPasswordResetEmail } from 'firebase/auth'
import { BadgeCheck, KeyRound, LoaderCircle, Mail, Save, ShieldCheck, UserRound } from 'lucide-react'
import { useAuth } from '@/features/auth/hooks/useAuth'
import { getFirebaseAuth } from '@/lib/firebase/client'

export default function SettingsPage() {
  const { user, profile, saveProfileName } = useAuth()
  const [nameDraft, setNameDraft] = useState<string | null>(null)
  const name = nameDraft ?? profile?.name ?? ''
  const [saving, setSaving] = useState(false)
  const [sendingReset, setSendingReset] = useState(false)
  const [message, setMessage] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  const canResetPassword = Boolean(
    user?.email && user.providerData.some((provider) => provider.providerId === 'password'),
  )
  const normalizedName = name.trim().replace(/\s+/g, ' ')
  const nameChanged = normalizedName !== profile?.name

  const handleSave = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (!nameChanged || normalizedName.length < 1 || normalizedName.length > 120) return

    setSaving(true)
    setMessage(null)
    setError(null)
    try {
      await saveProfileName(normalizedName)
      setNameDraft(normalizedName)
      setMessage('Your CipherPage display name has been updated.')
    } catch (saveError) {
      setError(saveError instanceof Error ? saveError.message : 'Unable to save your profile right now.')
    } finally {
      setSaving(false)
    }
  }

  const handlePasswordReset = async () => {
    if (!user?.email) return

    setSendingReset(true)
    setMessage(null)
    setError(null)
    try {
      await sendPasswordResetEmail(getFirebaseAuth(), user.email)
      setMessage(`Password reset instructions were sent to ${user.email}.`)
    } catch {
      setError('Firebase could not send the password reset email. Check your connection and try again.')
    } finally {
      setSendingReset(false)
    }
  }

  return (
    <div className="mx-auto max-w-4xl space-y-8 animate-in fade-in duration-500">
      <header>
        <p className="text-sm font-medium text-cyan-400">Account</p>
        <h1 className="mt-2 text-3xl font-bold tracking-tight text-white">Settings</h1>
        <p className="mt-2 text-zinc-400">Manage the information and sign-in options for your CipherPage account.</p>
      </header>

      {message && <p role="status" className="rounded-xl border border-emerald-500/20 bg-emerald-500/10 px-4 py-3 text-sm text-emerald-300">{message}</p>}
      {error && <p role="alert" className="rounded-xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-300">{error}</p>}

      <section className="rounded-2xl border border-white/10 bg-zinc-900/60 p-6 shadow-xl shadow-black/10 sm:p-8">
        <div className="mb-6 flex items-start gap-4">
          <span className="rounded-xl bg-cyan-500/10 p-3 text-cyan-300"><UserRound className="h-5 w-5" aria-hidden="true" /></span>
          <div>
            <h2 className="text-lg font-semibold text-white">General</h2>
            <p className="mt-1 text-sm text-zinc-400">Choose the name shown on your CipherPage profile.</p>
          </div>
        </div>

        <form onSubmit={handleSave} className="space-y-5">
          <label className="block space-y-2">
            <span className="text-sm font-medium text-zinc-200">Display name</span>
            <input
              value={name}
              onChange={(event) => setNameDraft(event.target.value)}
              maxLength={120}
              autoComplete="name"
              required
              className="w-full rounded-xl border border-white/10 bg-zinc-950 px-4 py-3 text-sm text-white outline-none transition focus:border-cyan-400/60 focus:ring-2 focus:ring-cyan-500/20"
            />
            <span className="block text-xs text-zinc-500">This updates your CipherPage profile only; your Google or Firebase account name is unchanged.</span>
          </label>

          <div className="grid gap-4 sm:grid-cols-2">
            <div className="rounded-xl border border-white/5 bg-zinc-950/60 p-4">
              <div className="flex items-center gap-2 text-xs font-medium uppercase tracking-wide text-zinc-500"><Mail className="h-3.5 w-3.5" aria-hidden="true" /> Email</div>
              <p className="mt-2 break-all text-sm text-zinc-200">{profile?.email || user?.email || 'Unavailable'}</p>
              <p className="mt-1 text-xs text-zinc-500">Managed by your sign-in provider.</p>
            </div>
            <div className="rounded-xl border border-white/5 bg-zinc-950/60 p-4">
              <div className="flex items-center gap-2 text-xs font-medium uppercase tracking-wide text-zinc-500"><ShieldCheck className="h-3.5 w-3.5" aria-hidden="true" /> Email status</div>
              <p className="mt-2 flex items-center gap-2 text-sm text-zinc-200">
                {user?.emailVerified ? <BadgeCheck className="h-4 w-4 text-emerald-400" aria-hidden="true" /> : <ShieldCheck className="h-4 w-4 text-amber-400" aria-hidden="true" />}
                {user?.emailVerified ? 'Verified' : 'Not verified'}
              </p>
              <p className="mt-1 text-xs text-zinc-500">Your verified identity is used to access your account.</p>
            </div>
          </div>

          <div className="flex flex-col gap-3 border-t border-white/5 pt-5 sm:flex-row sm:items-center sm:justify-between">
            <p className="text-xs text-zinc-500">Account role: <span className="font-medium text-zinc-300">{profile?.role.replaceAll('_', ' ') || 'Loading'}</span></p>
            <button
              type="submit"
              disabled={!nameChanged || normalizedName.length < 1 || normalizedName.length > 120 || saving}
              className="inline-flex items-center justify-center gap-2 rounded-xl bg-cyan-500 px-4 py-2.5 text-sm font-semibold text-zinc-950 transition hover:bg-cyan-400 disabled:cursor-not-allowed disabled:opacity-40"
            >
              {saving ? <LoaderCircle className="h-4 w-4 animate-spin" aria-hidden="true" /> : <Save className="h-4 w-4" aria-hidden="true" />}
              {saving ? 'Saving…' : 'Save changes'}
            </button>
          </div>
        </form>
      </section>

      <section className="rounded-2xl border border-white/10 bg-zinc-900/60 p-6 shadow-xl shadow-black/10 sm:p-8">
        <div className="mb-5 flex items-start gap-4">
          <span className="rounded-xl bg-purple-500/10 p-3 text-purple-300"><KeyRound className="h-5 w-5" aria-hidden="true" /></span>
          <div>
            <h2 className="text-lg font-semibold text-white">Security</h2>
            <p className="mt-1 text-sm text-zinc-400">Password changes are handled securely by Firebase Authentication.</p>
          </div>
        </div>

        {canResetPassword ? (
          <div className="flex flex-col gap-4 rounded-xl border border-white/5 bg-zinc-950/60 p-4 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <p className="text-sm font-medium text-zinc-200">Reset your password</p>
              <p className="mt-1 text-xs text-zinc-500">Firebase will email a password reset link to your account email.</p>
            </div>
            <button
              type="button"
              onClick={() => void handlePasswordReset()}
              disabled={sendingReset}
              className="inline-flex shrink-0 items-center justify-center gap-2 rounded-xl border border-white/10 px-4 py-2.5 text-sm font-medium text-zinc-200 transition hover:border-cyan-400/40 hover:bg-cyan-500/5 hover:text-white disabled:cursor-wait disabled:opacity-50"
            >
              {sendingReset && <LoaderCircle className="h-4 w-4 animate-spin" aria-hidden="true" />}
              {sendingReset ? 'Sending…' : 'Send reset email'}
            </button>
          </div>
        ) : (
          <p className="rounded-xl border border-white/5 bg-zinc-950/60 p-4 text-sm text-zinc-400">
            Your account signs in with an external provider, so password changes are managed by that provider.
          </p>
        )}
      </section>
    </div>
  )
}
