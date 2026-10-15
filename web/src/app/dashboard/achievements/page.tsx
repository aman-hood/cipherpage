'use client';

import { useState, useEffect } from 'react';
import { 
  Trophy, 
  Award, 
  Flame, 
  CheckCircle2, 
  Sparkles, 
  Zap, 
  ShieldCheck, 
  ExternalLink, 
  Share2, 
  Copy, 
  Check, 
  Lock, 
  ChevronRight, 
  BookOpen, 
  Terminal, 
  TrendingUp, 
  Calendar as CalendarIcon,
  Download,
  Eye,
  Star
} from 'lucide-react';
import { 
  Badge, 
  Certificate, 
  UserProgressData, 
  getUserProgress, 
  calculateLevel 
} from '@/lib/gamificationData';
import { createClient } from '@/lib/supabase/client';
import { 
  fetchLiveUserStats, 
  fetchLiveCertificates 
} from '@/services/gamificationService';

export default function AchievementsPage() {
  const [progress, setProgress] = useState<UserProgressData>(getUserProgress);
  const [selectedBadge, setSelectedBadge] = useState<Badge | null>(null);
  const [selectedCertificate, setSelectedCertificate] = useState<Certificate | null>(null);
  const [badgeFilter, setBadgeFilter] = useState<'all' | 'unlocked' | 'locked'>('all');
  const [copiedCertId, setCopiedCertId] = useState<string | null>(null);
  const [userName, setUserName] = useState('Developer');

  useEffect(() => {
    const loadGamificationData = async () => {
      // 1. Initial local base
      const initial = getUserProgress();
      setProgress(initial);

      try {
        const savedUser = localStorage.getItem('cipherpage_user');
        if (savedUser) {
          const u = JSON.parse(savedUser);
          if (u.name) setUserName(u.name);
        }
      } catch (e) {}

      // 2. Fetch active Supabase session
      let token: string | undefined;
      try {
        const supabase = createClient();
        const { data: { session } } = await supabase.auth.getSession();
        if (session?.access_token) {
          token = session.access_token;
          if (session.user?.user_metadata?.name) {
            setUserName(session.user.user_metadata.name);
          } else if (session.user?.email) {
            setUserName(session.user.email.split('@')[0]);
          }
        }
      } catch (e) {}

      // 3. Hydrate live stats and certificates from backend
      try {
        const [liveStats, liveCertificates] = await Promise.all([
          fetchLiveUserStats(token).catch(() => null),
          fetchLiveCertificates(token).catch(() => []),
        ]);

        if (liveStats) {
          const levelInfo = calculateLevel(liveStats.total_xp);

          // Map backend badges into Badge interface, syncing unlock status
          const mappedBadges: Badge[] = initial.badges.map(ib => {
            const backendMatch = liveStats.badges.find(
              b => b.slug === ib.id || b.name.toLowerCase() === ib.name.toLowerCase()
            );
            if (backendMatch) {
              return {
                ...ib,
                unlocked: backendMatch.unlocked,
                unlockedAt: backendMatch.unlocked_at 
                  ? new Date(backendMatch.unlocked_at).toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' }) 
                  : ib.unlockedAt,
              };
            }
            return ib;
          });

          // Include any backend badges not yet in local initial bank
          liveStats.badges.forEach(bb => {
            const alreadyPresent = mappedBadges.some(
              mb => mb.id === bb.slug || mb.name.toLowerCase() === bb.name.toLowerCase()
            );
            if (!alreadyPresent) {
              mappedBadges.push({
                id: bb.slug || String(bb.id),
                name: bb.name,
                description: bb.description,
                category: (bb.category as 'streak' | 'skills' | 'speed' | 'milestone') || 'milestone',
                tier: (bb.tier as 'bronze' | 'silver' | 'gold' | 'diamond') || 'bronze',
                icon: bb.icon || '🏆',
                unlocked: bb.unlocked,
                unlockedAt: bb.unlocked_at 
                  ? new Date(bb.unlocked_at).toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' }) 
                  : undefined,
                progress: { current: bb.unlocked ? 1 : 0, max: 1 },
              });
            }
          });

          // Map certificates
          let mappedCerts = initial.certificates;
          if (liveCertificates && liveCertificates.length > 0) {
            mappedCerts = liveCertificates.map(c => ({
              id: c.id,
              title: c.title,
              issuer: c.issuer,
              issueDate: c.issue_date,
              verificationCode: c.verification_code,
              credentialUrl: c.credential_url,
              skills: c.skills,
            }));
          }

          setProgress(prev => ({
            ...prev,
            totalXp: liveStats.total_xp,
            level: liveStats.level || levelInfo.level,
            levelTitle: levelInfo.title,
            currentStreak: liveStats.current_streak,
            longestStreak: liveStats.longest_streak,
            totalSolved: liveStats.total_solved,
            totalEasySolved: liveStats.easy_solved,
            totalMediumSolved: liveStats.medium_solved,
            totalHardSolved: liveStats.hard_solved,
            badges: mappedBadges,
            certificates: mappedCerts,
          }));
        }
      } catch (err) {
        console.warn('Failed hydrating live gamification data from backend:', err);
      }
    };

    loadGamificationData();
  }, []);

  const levelInfo = calculateLevel(progress.totalXp);
  const currentFloor = levelInfo.currentLevelFloor;
  const nextTarget = levelInfo.nextLevelXp;
  const xpInLevel = progress.totalXp - currentFloor;
  const xpNeeded = nextTarget - currentFloor;
  const xpPercent = Math.min(100, Math.round((xpInLevel / xpNeeded) * 100));

  const filteredBadges = progress.badges.filter((b) => {
    if (badgeFilter === 'unlocked') return b.unlocked;
    if (badgeFilter === 'locked') return !b.unlocked;
    return true;
  });

  const handleCopyCredential = (cert: Certificate) => {
    navigator.clipboard.writeText(cert.credentialUrl);
    setCopiedCertId(cert.id);
    setTimeout(() => setCopiedCertId(null), 2500);
  };

  return (
    <div className="max-w-7xl mx-auto space-y-8 animate-in fade-in duration-500">
      {/* Header: LAG Grow Professionally */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-white/5 pb-6">
        <div>
          <div className="flex items-center gap-2 text-emerald-400 text-xs font-semibold uppercase tracking-wider mb-1">
            <Trophy className="w-4 h-4" />
            <span>LAG Stage 03 • Grow Professionally</span>
          </div>
          <h1 className="text-3xl font-bold tracking-tight text-white">Progress & Achievements</h1>
          <p className="text-zinc-400 text-sm mt-1">
            Track your algorithmic mastery, claim verifiable certificates, and inspect earned badges.
          </p>
        </div>

        {/* Current Level Pill */}
        <div className="flex items-center gap-3">
          <div className="px-4 py-2 rounded-2xl bg-zinc-900 border border-white/10 flex items-center gap-3 shadow-lg">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-500 to-emerald-500 p-[2px]">
              <div className="w-full h-full rounded-xl bg-zinc-950 flex items-center justify-center font-bold text-sm text-cyan-400">
                L{progress.level}
              </div>
            </div>
            <div>
              <span className="text-[10px] uppercase font-semibold text-zinc-400 block tracking-wider">Rank Tier</span>
              <span className="text-sm font-bold text-white block -mt-0.5">{progress.levelTitle}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Top Banner: XP Progress & Global Stats */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* XP Level Card (7 cols) */}
        <div className="lg:col-span-7 p-6 rounded-3xl bg-gradient-to-br from-zinc-900/90 to-zinc-950 border border-white/10 shadow-2xl relative overflow-hidden flex flex-col justify-between">
          <div className="absolute top-0 right-0 w-64 h-64 bg-cyan-500/10 rounded-full blur-[80px] pointer-events-none" />
          
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <span className="text-xs font-semibold uppercase text-cyan-400 tracking-wider">Level Progression</span>
                <h3 className="text-2xl font-bold text-white mt-0.5">
                  Level {progress.level}: {progress.levelTitle}
                </h3>
              </div>
              <div className="text-right">
                <span className="text-xs text-zinc-400">Total XP Earned</span>
                <div className="text-2xl font-black text-cyan-400 font-mono">
                  {progress.totalXp.toLocaleString()} <span className="text-xs text-zinc-500">XP</span>
                </div>
              </div>
            </div>

            {/* Progress Bar */}
            <div className="space-y-1.5 pt-2">
              <div className="flex items-center justify-between text-xs font-medium">
                <span className="text-zinc-300">Level {progress.level} ({currentFloor} XP)</span>
                <span className="text-cyan-400 font-mono font-bold">{xpPercent}% ({xpInLevel}/{xpNeeded} XP)</span>
                <span className="text-zinc-500">Level {progress.level + 1} ({nextTarget} XP)</span>
              </div>
              <div className="w-full h-3 rounded-full bg-zinc-800/80 p-[2px] overflow-hidden border border-white/5">
                <div 
                  className="h-full rounded-full bg-gradient-to-r from-cyan-500 via-emerald-400 to-purple-500 transition-all duration-700 shadow-[0_0_12px_rgba(6,182,212,0.6)]"
                  style={{ width: `${xpPercent}%` }}
                />
              </div>
            </div>
          </div>

          <div className="grid grid-cols-3 gap-3 pt-6 mt-6 border-t border-white/5 text-center">
            <div className="p-3 rounded-xl bg-zinc-900/50 border border-white/5">
              <span className="text-[11px] text-zinc-400 block font-medium">Problems Solved</span>
              <span className="text-xl font-bold text-white mt-1 block">{progress.totalSolved}</span>
            </div>
            <div className="p-3 rounded-xl bg-zinc-900/50 border border-white/5">
              <span className="text-[11px] text-zinc-400 block font-medium">Global Percentile</span>
              <span className="text-xl font-bold text-emerald-400 mt-1 block">Top {100 - progress.rankPercentile}%</span>
            </div>
            <div className="p-3 rounded-xl bg-zinc-900/50 border border-white/5">
              <span className="text-[11px] text-zinc-400 block font-medium">Badges Unlocked</span>
              <span className="text-xl font-bold text-purple-400 mt-1 block">
                {progress.badges.filter(b => b.unlocked).length} / {progress.badges.length}
              </span>
            </div>
          </div>
        </div>

        {/* Streak & Difficulty Breakdown (5 cols) */}
        <div className="lg:col-span-5 grid grid-cols-2 gap-4">
          {/* Current Streak */}
          <div className="p-5 rounded-3xl bg-zinc-900/60 border border-white/10 shadow-xl relative overflow-hidden flex flex-col justify-between">
            <div className="w-10 h-10 rounded-2xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400">
              <Flame className="w-6 h-6 fill-amber-500/20" />
            </div>
            <div className="mt-4">
              <span className="text-xs text-zinc-400 font-medium">Current Streak</span>
              <h4 className="text-3xl font-extrabold text-white mt-1 font-mono">{progress.currentStreak} Days</h4>
              <span className="text-[11px] text-amber-400 font-medium flex items-center gap-1 mt-1">
                🔥 Longest: {progress.longestStreak} Days
              </span>
            </div>
          </div>

          {/* Difficulty Solved Distribution */}
          <div className="p-5 rounded-3xl bg-zinc-900/60 border border-white/10 shadow-xl flex flex-col justify-between">
            <div className="flex items-center justify-between">
              <span className="text-xs text-zinc-400 font-medium">By Difficulty</span>
              <TrendingUp className="w-4 h-4 text-cyan-400" />
            </div>
            <div className="space-y-2 mt-3 text-xs">
              <div className="flex items-center justify-between">
                <span className="text-emerald-400 font-medium">Easy</span>
                <span className="font-bold text-white font-mono">{progress.totalEasySolved}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-amber-400 font-medium">Medium</span>
                <span className="font-bold text-white font-mono">{progress.totalMediumSolved}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-rose-400 font-medium">Hard</span>
                <span className="font-bold text-white font-mono">{progress.totalHardSolved}</span>
              </div>
            </div>
            <div className="w-full h-1.5 rounded-full bg-zinc-800 flex overflow-hidden mt-3">
              <div style={{ width: '35%' }} className="bg-emerald-400" />
              <div style={{ width: '50%' }} className="bg-amber-400" />
              <div style={{ width: '15%' }} className="bg-rose-400" />
            </div>
          </div>
        </div>
      </div>

      {/* Skill Mastery Section */}
      <div className="p-6 md:p-8 rounded-3xl bg-zinc-900/40 border border-white/5 shadow-xl space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-xl font-bold text-white tracking-tight">Algorithmic Skill Domains</h3>
            <p className="text-xs text-zinc-400 mt-0.5">Competency measured through passing all 10 testcases on problem topics.</p>
          </div>
          <span className="text-xs font-mono text-cyan-400 bg-cyan-950/40 px-3 py-1 rounded-full border border-cyan-500/20">
            5 Domains Assessed
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {progress.skills.map((skill) => (
            <div 
              key={skill.name}
              className="p-5 rounded-2xl bg-zinc-950/80 border border-white/5 hover:border-cyan-500/30 transition-all space-y-3 group"
            >
              <div className="flex items-center justify-between">
                <h4 className="font-semibold text-white text-sm group-hover:text-cyan-400 transition-colors">
                  {skill.name}
                </h4>
                <span className="text-xs font-bold font-mono px-2 py-0.5 rounded bg-zinc-800 text-zinc-300">
                  Tier {skill.level}
                </span>
              </div>

              <div className="space-y-1.5">
                <div className="flex items-center justify-between text-xs text-zinc-400">
                  <span>{skill.solvedCount} of {skill.totalCount} problems</span>
                  <span className="font-bold text-white font-mono">{skill.progressPercent}%</span>
                </div>
                <div className="w-full h-2 rounded-full bg-zinc-800 overflow-hidden">
                  <div 
                    className={`h-full rounded-full bg-gradient-to-r ${skill.color} transition-all duration-500`}
                    style={{ width: `${skill.progressPercent}%` }}
                  />
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Badges Showcase Section */}
      <div className="p-6 md:p-8 rounded-3xl bg-zinc-900/40 border border-white/5 shadow-xl space-y-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h3 className="text-xl font-bold text-white tracking-tight">Achievements & Badges</h3>
            <p className="text-xs text-zinc-400 mt-0.5">Earn badges for daily streaks, speed benchmarks, and domain mastery.</p>
          </div>

          {/* Badge Filter Tabs */}
          <div className="flex items-center gap-1.5 p-1 rounded-xl bg-zinc-950 border border-white/10 text-xs font-semibold">
            <button
              onClick={() => setBadgeFilter('all')}
              className={`px-3 py-1.5 rounded-lg transition-colors cursor-pointer ${
                badgeFilter === 'all' ? 'bg-cyan-500 text-zinc-950' : 'text-zinc-400 hover:text-white'
              }`}
            >
              All ({progress.badges.length})
            </button>
            <button
              onClick={() => setBadgeFilter('unlocked')}
              className={`px-3 py-1.5 rounded-lg transition-colors cursor-pointer ${
                badgeFilter === 'unlocked' ? 'bg-cyan-500 text-zinc-950' : 'text-zinc-400 hover:text-white'
              }`}
            >
              Unlocked ({progress.badges.filter(b => b.unlocked).length})
            </button>
            <button
              onClick={() => setBadgeFilter('locked')}
              className={`px-3 py-1.5 rounded-lg transition-colors cursor-pointer ${
                badgeFilter === 'locked' ? 'bg-cyan-500 text-zinc-950' : 'text-zinc-400 hover:text-white'
              }`}
            >
              Locked ({progress.badges.filter(b => !b.unlocked).length})
            </button>
          </div>
        </div>

        {/* Badges Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {filteredBadges.map((badge) => (
            <button
              key={badge.id}
              onClick={() => setSelectedBadge(badge)}
              className={`p-5 rounded-2xl border text-left transition-all flex flex-col justify-between group cursor-pointer relative overflow-hidden ${
                badge.unlocked
                  ? 'bg-zinc-950/80 border-white/10 hover:border-cyan-500/40 hover:scale-[1.02] shadow-lg'
                  : 'bg-zinc-950/40 border-white/5 opacity-60 hover:opacity-80'
              }`}
            >
              <div>
                <div className="flex items-center justify-between mb-3">
                  <div className="text-3xl p-2 rounded-xl bg-zinc-900 border border-white/5 group-hover:scale-110 transition-transform">
                    {badge.icon}
                  </div>
                  <span className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full border ${
                    badge.tier === 'diamond'
                      ? 'bg-cyan-500/20 text-cyan-300 border-cyan-500/40'
                      : badge.tier === 'gold'
                      ? 'bg-amber-500/20 text-amber-300 border-amber-500/40'
                      : badge.tier === 'silver'
                      ? 'bg-zinc-400/20 text-zinc-200 border-zinc-400/30'
                      : 'bg-orange-800/20 text-orange-300 border-orange-700/30'
                  }`}>
                    {badge.tier}
                  </span>
                </div>

                <h4 className="font-bold text-white text-sm mb-1 group-hover:text-cyan-300 transition-colors">
                  {badge.name}
                </h4>
                <p className="text-xs text-zinc-400 leading-relaxed line-clamp-2">
                  {badge.description}
                </p>
              </div>

              <div className="pt-4 mt-3 border-t border-white/5 flex items-center justify-between text-[11px]">
                {badge.unlocked ? (
                  <span className="text-emerald-400 font-semibold flex items-center gap-1">
                    <CheckCircle2 className="w-3.5 h-3.5" /> Unlocked
                  </span>
                ) : (
                  <span className="text-zinc-500 font-medium flex items-center gap-1">
                    <Lock className="w-3.5 h-3.5" /> In Progress
                  </span>
                )}

                {badge.progress && !badge.unlocked && (
                  <span className="font-mono text-zinc-400">
                    {badge.progress.current}/{badge.progress.max}
                  </span>
                )}
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Verifiable Certificates Section */}
      <div className="p-6 md:p-8 rounded-3xl bg-zinc-900/40 border border-white/5 shadow-xl space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-xl font-bold text-white tracking-tight">Verifiable Certificates</h3>
            <p className="text-xs text-zinc-400 mt-0.5">Shareable digital credentials proving tested algorithm proficiency.</p>
          </div>
          <span className="text-xs font-semibold text-emerald-400 bg-emerald-950/40 px-3 py-1 rounded-full border border-emerald-500/20 flex items-center gap-1.5">
            <ShieldCheck className="w-3.5 h-3.5" />
            2 Active Credentials
          </span>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {progress.certificates.map((cert) => (
            <div 
              key={cert.id}
              className="p-6 rounded-3xl bg-gradient-to-br from-zinc-950 to-zinc-900 border border-white/10 shadow-2xl space-y-5 relative overflow-hidden flex flex-col justify-between"
            >
              <div className="space-y-3">
                <div className="flex items-start justify-between gap-4">
                  <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-amber-400/20 to-cyan-500/20 border border-amber-500/30 flex items-center justify-center text-amber-400">
                    <Award className="w-6 h-6" />
                  </div>
                  <span className="text-xs font-mono font-bold text-cyan-400 bg-cyan-950/60 px-2.5 py-1 rounded border border-cyan-500/20">
                    {cert.verificationCode}
                  </span>
                </div>

                <div>
                  <h4 className="text-lg font-bold text-white tracking-tight">
                    {cert.title}
                  </h4>
                  <p className="text-xs text-zinc-400 mt-0.5">
                    Issued by <span className="text-zinc-200 font-medium">{cert.issuer}</span> to <span className="text-white font-semibold">{userName}</span> on {cert.issueDate}.
                  </p>
                </div>

                <div className="flex flex-wrap gap-1.5 pt-1">
                  {cert.skills.map((skill) => (
                    <span key={skill} className="px-2 py-0.5 rounded text-[11px] bg-zinc-800 text-zinc-300 border border-white/5">
                      {skill}
                    </span>
                  ))}
                </div>
              </div>

              {/* Action Buttons */}
              <div className="pt-4 border-t border-white/5 flex items-center justify-between gap-3">
                <button
                  onClick={() => setSelectedCertificate(cert)}
                  className="px-4 py-2 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-zinc-950 text-xs font-bold transition-all flex items-center gap-1.5 cursor-pointer shadow-sm"
                >
                  <Eye className="w-3.5 h-3.5" />
                  <span>Preview Credential</span>
                </button>

                <button
                  onClick={() => handleCopyCredential(cert)}
                  className="px-3.5 py-2 rounded-xl bg-zinc-800 hover:bg-zinc-700 text-zinc-200 text-xs font-medium border border-white/10 transition-colors flex items-center gap-1.5 cursor-pointer"
                >
                  {copiedCertId === cert.id ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                  <span>{copiedCertId === cert.id ? 'Copied Link' : 'Copy Verification Link'}</span>
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Certificate Modal Preview */}
      {selectedCertificate && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-in fade-in duration-200">
          <div className="max-w-2xl w-full bg-zinc-950 rounded-3xl border border-white/20 p-8 shadow-2xl relative space-y-6 text-center">
            <button
              onClick={() => setSelectedCertificate(null)}
              className="absolute top-5 right-5 text-zinc-400 hover:text-white p-2 rounded-xl bg-zinc-900 border border-white/5 cursor-pointer"
            >
              ✕
            </button>

            <div className="w-16 h-16 rounded-full bg-amber-500/10 border border-amber-500/30 mx-auto flex items-center justify-center text-amber-400">
              <Award className="w-8 h-8" />
            </div>

            <div className="space-y-2">
              <span className="text-xs font-bold uppercase tracking-widest text-cyan-400">
                Official CipherPage Credential
              </span>
              <h2 className="text-2xl font-black text-white">{selectedCertificate.title}</h2>
              <p className="text-sm text-zinc-400">
                This certifies that <strong className="text-white">{userName}</strong> has completed the required video curriculum and passed all 10 testcases on our integrated platform.
              </p>
            </div>

            <div className="p-4 rounded-2xl bg-zinc-900/60 border border-white/5 flex items-center justify-between text-xs font-mono">
              <span className="text-zinc-400">Credential ID:</span>
              <span className="text-cyan-400 font-bold">{selectedCertificate.verificationCode}</span>
            </div>

            <div className="flex justify-center gap-3 pt-2">
              <button
                onClick={() => setSelectedCertificate(null)}
                className="px-5 py-2.5 rounded-xl bg-zinc-800 hover:bg-zinc-700 text-zinc-200 text-xs font-semibold cursor-pointer"
              >
                Close Preview
              </button>
              <button
                onClick={() => handleCopyCredential(selectedCertificate)}
                className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-cyan-400 text-zinc-950 text-xs font-bold hover:brightness-110 flex items-center gap-1.5 cursor-pointer"
              >
                <Share2 className="w-3.5 h-3.5" />
                <span>Share Verification</span>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Badge Modal Preview */}
      {selectedBadge && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-in fade-in duration-200">
          <div className="max-w-md w-full bg-zinc-950 rounded-3xl border border-white/20 p-6 shadow-2xl relative space-y-5 text-center">
            <button
              onClick={() => setSelectedBadge(null)}
              className="absolute top-4 right-4 text-zinc-400 hover:text-white p-2 rounded-xl bg-zinc-900 border border-white/5 cursor-pointer"
            >
              ✕
            </button>

            <div className="text-6xl mx-auto p-4 rounded-3xl bg-zinc-900 border border-white/10 w-fit">
              {selectedBadge.icon}
            </div>

            <div className="space-y-1.5">
              <span className={`text-[10px] font-bold uppercase tracking-wider px-2.5 py-0.5 rounded-full border ${
                selectedBadge.tier === 'diamond'
                  ? 'bg-cyan-500/20 text-cyan-300 border-cyan-500/40'
                  : 'bg-amber-500/20 text-amber-300 border-amber-500/40'
              }`}>
                {selectedBadge.tier} Tier Badge
              </span>
              <h3 className="text-xl font-bold text-white">{selectedBadge.name}</h3>
              <p className="text-xs text-zinc-400 leading-relaxed">{selectedBadge.description}</p>
            </div>

            <div className="p-3 rounded-xl bg-zinc-900/60 border border-white/5 text-xs text-zinc-400">
              {selectedBadge.unlocked ? (
                <span className="text-emerald-400 font-semibold flex items-center justify-center gap-1">
                  <CheckCircle2 className="w-4 h-4" /> Unlocked on {selectedBadge.unlockedAt || 'August 2026'}
                </span>
              ) : (
                <span>Requirement: Complete criteria on the Monaco code editor.</span>
              )}
            </div>

            <button
              onClick={() => setSelectedBadge(null)}
              className="w-full py-2.5 rounded-xl bg-zinc-800 hover:bg-zinc-700 text-zinc-200 text-xs font-semibold cursor-pointer"
            >
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
