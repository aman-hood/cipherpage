'use client';

import Link from 'next/link';
import { Home, BookOpen, Trophy, Settings, LogOut, Code2 } from 'lucide-react';
import Image from 'next/image';
import { useState, useEffect } from 'react';
import { useRouter, usePathname } from 'next/navigation';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const [initials, setInitials] = useState('US');
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    const savedUser = localStorage.getItem('cipherpage_user');
    if (savedUser) {
      try {
        const user = JSON.parse(savedUser);
        if (user.name) {
          const parts = user.name.split(' ');
          let inits = parts[0].charAt(0).toUpperCase();
          if (parts.length > 1) {
            inits += parts[parts.length - 1].charAt(0).toUpperCase();
          }
          setInitials(inits);
        }
      } catch (e) {}
    }
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('cipherpage_user');
    router.push('/login');
  };

  const isDashboard = pathname === '/dashboard';
  const isCourses = pathname?.startsWith('/dashboard/courses');
  const isPractice = pathname?.startsWith('/dashboard/practice');
  const isAchievements = pathname?.startsWith('/dashboard/achievements');
  const isSettings = pathname?.startsWith('/dashboard/settings');

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
