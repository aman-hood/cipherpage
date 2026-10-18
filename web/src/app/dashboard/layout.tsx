'use client';

import Link from 'next/link';
import { Home, BookOpen, Trophy, Settings, LogOut, Code2 } from 'lucide-react';
import Image from 'next/image';
import { useEffect, useState } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { useAuth } from '@/features/auth/hooks/useAuth';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const [logoutError, setLogoutError] = useState<string | null>(null);
  const router = useRouter();
  const pathname = usePathname();
  const { user, profile, loading, profileError, signOut } = useAuth();

  useEffect(() => {
    if (!loading && !user) router.replace('/login');
  }, [loading, user, router]);

  const handleLogout = async () => {
    setLogoutError(null);
    try {
      await signOut();
    } catch (error) {
      setLogoutError(error instanceof Error ? error.message : 'Unable to revoke the session on the server.');
    } finally {
      router.replace('/login');
    }
  };

  const parts = (profile?.name || user?.displayName || 'User').trim().split(/\s+/);
  const initials = `${parts[0]?.[0] || 'U'}${parts.length > 1 ? parts[parts.length - 1][0] : ''}`.toUpperCase();

  const isDashboard = pathname === '/dashboard';
  const isCourses = pathname?.startsWith('/dashboard/courses');
  const isPractice = pathname?.startsWith('/dashboard/practice');
  const isAchievements = pathname?.startsWith('/dashboard/achievements');
  const isSettings = pathname?.startsWith('/dashboard/settings');

  if (loading) {
    return <div className="min-h-screen bg-zinc-950 text-zinc-50 grid place-items-center">Loading your account…</div>;
  }
  if (!user) return null;
  if (!profile) {
    return (
      <div className="min-h-screen bg-zinc-950 text-zinc-50 grid place-items-center px-6">
        <div className="max-w-lg text-center space-y-4">
          <h1 className="text-xl font-semibold">Account profile unavailable</h1>
          <p>{profileError || 'Your account could not be loaded.'}</p>
          <button onClick={handleLogout} className="rounded bg-cyan-700 px-4 py-2">Sign out</button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-screen bg-zinc-950 text-zinc-50 font-sans selection:bg-cyan-500/30">
      {/* Sidebar */}
      <aside className="w-64 border-r border-white/5 bg-zinc-950/80 backdrop-blur-md flex flex-col">
        <div className="h-20 flex items-center gap-3 px-6 border-b border-white/5">
          <Image src="/logo.png" alt="CipherPage Logo" width={32} height={32} className="w-8 h-8 object-contain" priority />
          <span className="text-lg font-bold tracking-tight">CipherPage</span>
        </div>
        
        <nav className="flex-1 py-6 px-4 flex flex-col gap-2">
          <Link
            href="/dashboard"
            className={`flex items-center gap-3 px-4 py-3 rounded-xl font-medium transition-colors ${
              isDashboard
                ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20'
                : 'hover:bg-white/5 text-zinc-400 hover:text-white'
            }`}
          >
            <Home className="w-5 h-5" />
            Dashboard
          </Link>
          <Link
            href="/dashboard/courses"
            className={`flex items-center gap-3 px-4 py-3 rounded-xl font-medium transition-colors ${
              isCourses
                ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20'
                : 'hover:bg-white/5 text-zinc-400 hover:text-white'
            }`}
          >
            <BookOpen className="w-5 h-5" />
            Courses (Learn)
          </Link>
          <Link
            href="/dashboard/practice"
            className={`flex items-center gap-3 px-4 py-3 rounded-xl font-medium transition-colors ${
              isPractice
                ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20'
                : 'hover:bg-white/5 text-zinc-400 hover:text-white'
            }`}
          >
            <Code2 className="w-5 h-5" />
            Practice (Apply)
          </Link>
          <Link
            href="/dashboard/achievements"
            className={`flex items-center gap-3 px-4 py-3 rounded-xl font-medium transition-colors ${
              isAchievements
                ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20'
                : 'hover:bg-white/5 text-zinc-400 hover:text-white'
            }`}
          >
            <Trophy className="w-5 h-5" />
            Achievements (Grow)
          </Link>
          <Link
            href="/dashboard/settings"
            className={`flex items-center gap-3 px-4 py-3 rounded-xl font-medium transition-colors mt-auto ${
              isSettings
                ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20'
                : 'hover:bg-white/5 text-zinc-400 hover:text-white'
            }`}
          >
            <Settings className="w-5 h-5" />
            Settings
          </Link>
        </nav>
        
        <div className="p-4 border-t border-white/5">
          {logoutError && <p className="mb-2 text-xs text-red-400">{logoutError}</p>}
          <button onClick={handleLogout} className="flex items-center gap-3 px-4 py-3 w-full rounded-xl hover:bg-red-500/10 text-zinc-400 hover:text-red-400 transition-colors">
            <LogOut className="w-5 h-5" />
            Sign Out
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto">
        <div className="h-20 flex items-center justify-end px-8 border-b border-white/5 bg-zinc-950/80 backdrop-blur-md sticky top-0 z-10">
          <div className="flex items-center gap-4">
            <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-cyan-500 to-purple-500 p-[2px]">
              <div className="w-full h-full rounded-full bg-zinc-900 border-2 border-transparent flex items-center justify-center overflow-hidden">
                <span className="font-semibold text-sm">{initials}</span>
              </div>
            </div>
          </div>
        </div>
        <div className="p-8">
          {children}
        </div>
      </main>
    </div>
  );
}
