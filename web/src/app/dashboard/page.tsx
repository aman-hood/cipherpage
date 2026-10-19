'use client';

import { 
  ChevronLeft, 
  ChevronRight, 
  Activity, 
  BookOpen, 
  Clock, 
  Terminal, 
  Play, 
  Calendar as CalendarIcon, 
  CheckCircle2, 
  ExternalLink, 
  Sparkles,
  AlertCircle,
  Code2,
  Trophy,
  Award
} from 'lucide-react';
import { useState, useEffect, useMemo } from 'react';
import { useAuth } from '@/features/auth/hooks/useAuth';
import Link from 'next/link';
import VideoPlayer from '@/components/VideoPlayer';
import PracticeWorkspace from '@/components/PracticeWorkspace';
import { 
  MONTH_NAMES, 
  CHANNEL_DATA, 
  getPlaylistForMonth, 
  getPOTDVideosForMonth, 
  getVideoForDate, 
  getPOTDDaysSet,
  POTDVideo 
} from '@/lib/youtubeData';

function YouTubeIcon({ className = "w-4 h-4" }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="currentColor">
      <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>
    </svg>
  );
}

interface CalendarProps {
  currentDate: Date;
  selectedDay: number;
  onPrevMonth: () => void;
  onNextMonth: () => void;
  onSelectDay: (day: number) => void;
  onJumpToDate: (year: number, monthIndex: number, day: number) => void;
}

function Calendar({
  currentDate,
  selectedDay,
  onPrevMonth,
  onNextMonth,
  onSelectDay,
  onJumpToDate,
}: CalendarProps) {
  const currentYear = currentDate.getFullYear();
  const currentMonth = currentDate.getMonth();

  const daysInMonth = new Date(currentYear, currentMonth + 1, 0).getDate();
  const firstDayOfMonth = new Date(currentYear, currentMonth, 1).getDay();

  const dayNames = ["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"];

  // Fetch playlist info & available POTD days for current month view
  const currentPlaylist = useMemo(() => {
    return getPlaylistForMonth(currentMonth, currentYear);
  }, [currentMonth, currentYear]);

  const potdDaysSet = useMemo(() => {
    return getPOTDDaysSet(currentYear, currentMonth);
  }, [currentYear, currentMonth]);

  const days = [];
  for (let i = 0; i < firstDayOfMonth; i++) {
    days.push(<div key={`empty-${i}`} className="w-8 h-8"></div>);
  }

  for (let i = 1; i <= daysInMonth; i++) {
    const isSelected = selectedDay === i;
    const hasPOTD = potdDaysSet.has(i);

    days.push(
      <button
        key={`day-${i}`}
        onClick={() => onSelectDay(i)}
        className={`w-8 h-8 flex flex-col items-center justify-center rounded-xl text-xs font-medium transition-all relative cursor-pointer ${
          isSelected
            ? 'bg-cyan-500 text-zinc-950 font-bold shadow-[0_0_15px_-3px_rgba(6,182,212,0.6)] scale-105'
            : hasPOTD
            ? 'text-cyan-300 bg-cyan-950/40 border border-cyan-500/30 hover:bg-cyan-500/20'
            : 'text-zinc-400 hover:bg-white/10 hover:text-white'
        }`}
        title={hasPOTD ? `POTD Available for ${MONTH_NAMES[currentMonth]} ${i}` : `${MONTH_NAMES[currentMonth]} ${i}`}
      >
        <span>{i}</span>
        {hasPOTD && !isSelected && (
          <span className="w-1 h-1 rounded-full bg-cyan-400 absolute bottom-1 shadow-[0_0_4px_rgba(34,211,238,0.9)]" />
        )}
      </button>
    );
  }

  return (
    <div className="bg-zinc-900/50 border border-white/5 rounded-2xl p-6 shadow-xl space-y-4">
      {/* Month & Year Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="font-semibold text-lg text-white">
            {MONTH_NAMES[currentMonth]} {currentYear}
          </h3>
          <div className="flex items-center gap-1.5 mt-0.5">
            {currentPlaylist ? (
              <span className="inline-flex items-center gap-1 text-[11px] font-medium text-emerald-400">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                {currentPlaylist.playlistTitle} ({potdDaysSet.size} POTDs)
              </span>
            ) : (
              <span className="text-[11px] text-zinc-500">
                No &ldquo;Leetcode {MONTH_NAMES[currentMonth]} {currentYear}&rdquo; playlist
              </span>
            )}
          </div>
        </div>

        <div className="flex gap-2">
          <button 
            onClick={onPrevMonth} 
            className="p-1.5 rounded-lg bg-zinc-800 hover:bg-zinc-700 text-zinc-400 hover:text-white transition-colors border border-white/5 cursor-pointer"
            title="Previous Month"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>
          <button 
            onClick={onNextMonth} 
            className="p-1.5 rounded-lg bg-zinc-800 hover:bg-zinc-700 text-zinc-400 hover:text-white transition-colors border border-white/5 cursor-pointer"
            title="Next Month"
          >
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      </div>
      
      {/* Day Names */}
      <div className="grid grid-cols-7 gap-y-3 gap-x-2 text-center text-xs font-medium text-zinc-500">
        {dayNames.map(day => (
          <div key={day}>{day}</div>
        ))}
      </div>

      {/* Days Grid */}
      <div className="grid grid-cols-7 gap-y-2 gap-x-2 justify-items-center">
        {days}
      </div>

      {/* Legend & Quick Jump */}
      <div className="pt-3 border-t border-white/5 space-y-2.5">
        <div className="flex items-center justify-between text-xs text-zinc-400">
          <span className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-cyan-400" />
            POTD Video Available
          </span>
          <span className="text-[11px] text-zinc-500">Click date to view</span>
        </div>

        {/* Quick jump shortcuts to months with channel playlists */}
        <div className="flex flex-wrap gap-2 pt-1">
          <button
            onClick={() => onJumpToDate(2026, 7, 1)} // August 2026 (monthIndex 7)
            className={`px-2.5 py-1 rounded-lg text-xs font-medium transition-colors cursor-pointer border ${
              currentMonth === 7 && currentYear === 2026
                ? 'bg-cyan-500/20 text-cyan-300 border-cyan-500/30'
                : 'bg-zinc-800/60 text-zinc-400 hover:text-white border-white/5 hover:bg-zinc-800'
            }`}
          >
            August 2026 (9)
          </button>
          <button
            onClick={() => onJumpToDate(2026, 6, 1)} // July 2026 (monthIndex 6)
            className={`px-2.5 py-1 rounded-lg text-xs font-medium transition-colors cursor-pointer border ${
              currentMonth === 6 && currentYear === 2026
                ? 'bg-cyan-500/20 text-cyan-300 border-cyan-500/30'
                : 'bg-zinc-800/60 text-zinc-400 hover:text-white border-white/5 hover:bg-zinc-800'
            }`}
          >
            July 2026 (21)
          </button>
        </div>
      </div>
    </div>
  );
}

export default function Dashboard() {
  const { profile, user } = useAuth();
  const userName = (profile?.name || user?.displayName || user?.email?.split('@')[0] || '').split(' ')[0];
  // Default to August 1, 2026 so user immediately sees their playlist's POTD video on load
  const [calendarDate, setCalendarDate] = useState(new Date(2026, 7, 1));
  const [selectedDay, setSelectedDay] = useState(1);
  const [solvedPotds, setSolvedPotds] = useState<string[]>([]);
  const [showPracticeWorkspace, setShowPracticeWorkspace] = useState(false);
  // New state for dynamic metrics
  const [streakDays, setStreakDays] = useState<number>(0);
  const [hoursLearned, setHoursLearned] = useState<number>(0);
  // Store dates of days with at least one solved problem
  const [solvedDates, setSolvedDates] = useState<string[]>([]);

  // Load persisted metrics
  useEffect(() => {
    try {
      const savedSolved = localStorage.getItem('cipherpage_solved_potds');
      if (savedSolved) setSolvedPotds(JSON.parse(savedSolved));
      const savedStreak = localStorage.getItem('cipherpage_current_streak');
      if (savedStreak) setStreakDays(parseInt(savedStreak, 10));
      const savedHours = localStorage.getItem('cipherpage_hours_learned');
      if (savedHours) setHoursLearned(parseFloat(savedHours));
    } catch (e) {}
  }, []);

  useEffect(() => {
    try {
      const savedSolved = localStorage.getItem('cipherpage_solved_potds');
      if (savedSolved) {
        setSolvedPotds(JSON.parse(savedSolved));
      }
    } catch (e) {}
  }, []);

  const currentYear = calendarDate.getFullYear();
  const currentMonth = calendarDate.getMonth();

  // Find playlist for currently selected month in calendar
  const activePlaylist = useMemo(() => {
    return getPlaylistForMonth(currentMonth, currentYear);
  }, [currentMonth, currentYear]);

  // Find video for the clicked date
  const selectedPOTDVideo = useMemo(() => {
    return getVideoForDate(currentYear, currentMonth, selectedDay);
  }, [currentYear, currentMonth, selectedDay]);

  // List of all POTD videos in this month
  const monthPOTDVideos = useMemo(() => {
    return getPOTDVideosForMonth(currentMonth, currentYear);
  }, [currentMonth, currentYear]);

  const handlePrevMonth = () => {
    const prev = new Date(currentYear, currentMonth - 1, 1);
    setCalendarDate(prev);
    setSelectedDay(1);
  };

  const handleNextMonth = () => {
    const next = new Date(currentYear, currentMonth + 1, 1);
    setCalendarDate(next);
    setSelectedDay(1);
  };

  const handleSelectDay = (day: number) => {
    setSelectedDay(day);
  };

  const handleJumpToDate = (year: number, monthIndex: number, day: number) => {
    setCalendarDate(new Date(year, monthIndex, 1));
    setSelectedDay(day);
  };

  const handleToggleSolved = (videoId: string) => {
    const updated = solvedPotds.includes(videoId)
      ? solvedPotds.filter(id => id !== videoId)
      : [...solvedPotds, videoId];
    setSolvedPotds(updated);
    localStorage.setItem('cipherpage_solved_potds', JSON.stringify(updated));

    // Record today's date as solved if not already present
    const todayStr = new Date().toISOString().split('T')[0];
    let newSolvedDates = solvedDates;
    if (!solvedDates.includes(todayStr)) {
      newSolvedDates = [...solvedDates, todayStr];
      setSolvedDates(newSolvedDates);
      localStorage.setItem('cipherpage_solved_dates', JSON.stringify(newSolvedDates));
    }

    // Recompute streak based on consecutive solved dates up to today
    const datesSet = new Set(newSolvedDates);
    let streak = 0;
    const today = new Date();
    for (let i = 0; i < 365; i++) {
      const dateKey = today.toISOString().split('T')[0];
      if (datesSet.has(dateKey)) {
        streak++;
        today.setDate(today.getDate() - 1);
      } else {
        break;
      }
    }
    setStreakDays(streak);
    localStorage.setItem('cipherpage_current_streak', streak.toString());

    // Increment hours learned by a fixed amount per solved POTD (e.g., 0.5h)
    const addedHours = 0.5;
    const totalHours = parseFloat(localStorage.getItem('cipherpage_hours_learned') || '0') + addedHours;
    setHoursLearned(totalHours);
    localStorage.setItem('cipherpage_hours_learned', totalHours.toString());
  };

  const handleVideoWatched = (videoId: string) => {
    // Add hours for video watch (e.g., 0.5h per watch)
    const addedHours = 0.5;
    const total = parseFloat(localStorage.getItem('cipherpage_hours_learned') || '0') + addedHours;
    setHoursLearned(total);
    localStorage.setItem('cipherpage_hours_learned', total.toString());
  };

  const isCurrentSolved = selectedPOTDVideo && solvedPotds.includes(selectedPOTDVideo.videoId);

  return (
    <div className="max-w-6xl mx-auto space-y-8 animate-in fade-in duration-500">
      {/* Top Welcome Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight mb-2 text-white">
          Welcome back{userName ? `, ${userName}` : ''}!
        </h1>
        <p className="text-zinc-400">
          Track your daily LeetCode Problem of the Day solutions from <span className="text-cyan-400 font-medium">{CHANNEL_DATA.handle}</span>.
        </p>
      </div>
      
      {/* Overview Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="p-6 rounded-2xl bg-zinc-900/50 border border-white/5 shadow-xl relative overflow-hidden group hover:border-cyan-500/30 transition-colors">
          <div className="absolute top-0 right-0 w-32 h-32 bg-cyan-500/10 rounded-full blur-[50px] -mr-10 -mt-10 pointer-events-none" />
          <div className="w-12 h-12 bg-cyan-500/10 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
            <Activity className="w-6 h-6 text-cyan-400" />
          </div>
          <p className="text-zinc-400 text-sm font-medium mb-1">Current Streak</p>
          <h4 className="text-3xl font-bold text-white">{streakDays} Days</h4>
        </div>
        
        <div className="p-6 rounded-2xl bg-zinc-900/50 border border-white/5 shadow-xl relative overflow-hidden group hover:border-purple-500/30 transition-colors">
          <div className="absolute top-0 right-0 w-32 h-32 bg-purple-500/10 rounded-full blur-[50px] -mr-10 -mt-10 pointer-events-none" />
          <div className="w-12 h-12 bg-purple-500/10 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
            <BookOpen className="w-6 h-6 text-purple-400" />
          </div>
          <p className="text-zinc-400 text-sm font-medium mb-1">Questions Solved</p>
          <h4 className="text-3xl font-bold text-white">{solvedPotds.length}</h4>
        </div>
        
        <div className="p-6 rounded-2xl bg-zinc-900/50 border border-white/5 shadow-xl relative overflow-hidden group hover:border-emerald-500/30 transition-colors">
          <div className="absolute top-0 right-0 w-32 h-32 bg-emerald-500/10 rounded-full blur-[50px] -mr-10 -mt-10 pointer-events-none" />
          <div className="w-12 h-12 bg-emerald-500/10 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
            <Clock className="w-6 h-6 text-emerald-400" />
          </div>
          <p className="text-zinc-400 text-sm font-medium mb-1">Hours Learned</p>
          <h4 className="text-3xl font-bold text-white">{hoursLearned}h</h4>
        </div>
      </div>

      {/* Main Dynamic Video Player: Powered by react-player & Calendar Date selection */}
      <div className="bg-zinc-900/50 border border-white/5 rounded-2xl p-6 shadow-xl relative overflow-hidden">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
          <div>
            <div className="flex items-center gap-2 text-cyan-400 text-xs font-semibold uppercase tracking-wider mb-1">
              <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
              <span>YouTube POTD Video Player</span>
            </div>
            <h2 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2.5">
              <span>POTD: {MONTH_NAMES[currentMonth]} {selectedDay}, {currentYear}</span>
            </h2>
            <p className="text-zinc-400 text-sm mt-0.5">
              Target Playlist: <span className="text-zinc-200 font-medium">Leetcode {MONTH_NAMES[currentMonth]} {currentYear}</span>
            </p>
          </div>

          <div className="flex items-center gap-3">
            <a
              href={`https://youtube.com/@cipherpage`}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-zinc-800/80 hover:bg-zinc-800 text-zinc-300 hover:text-white text-xs font-medium border border-white/10 transition-colors"
            >
              <YouTubeIcon className="w-4 h-4 text-red-500" />
              <span>@cipherpage</span>
            </a>
            <Link
              href="/dashboard/courses"
              className="flex items-center gap-2 px-4 py-2 rounded-xl bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-400 font-semibold text-xs border border-cyan-500/20 transition-all cursor-pointer shadow-sm"
            >
              <BookOpen className="w-4 h-4" />
              <span>All Courses</span>
            </Link>
          </div>
        </div>

        {/* Video Player Display or Empty State */}
        {selectedPOTDVideo ? (
          <div className="space-y-5">
            <div className="max-w-4xl mx-auto rounded-2xl overflow-hidden border border-white/10 shadow-2xl bg-black">
              <VideoPlayer
                key={selectedPOTDVideo.videoId}
                src={selectedPOTDVideo.url}
                title={selectedPOTDVideo.title}
                controls={true}
                playing={false}
              />
            </div>

            {/* Video Metadata Bar */}
            <div className="p-4 rounded-xl bg-zinc-950/60 border border-white/5 flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div className="space-y-1">
                <div className="flex items-center gap-2.5">
                  {selectedPOTDVideo.difficulty && (
                    <span className={`px-2.5 py-0.5 rounded-full text-xs font-semibold uppercase tracking-wide border ${
                      selectedPOTDVideo.difficulty === 'Easy'
                        ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                        : selectedPOTDVideo.difficulty === 'Medium'
                        ? 'bg-amber-500/10 text-amber-400 border-amber-500/20'
                        : 'bg-rose-500/10 text-rose-400 border-rose-500/20'
                    }`}>
                      {selectedPOTDVideo.difficulty}
                    </span>
                  )}
                  {selectedPOTDVideo.problemNumber && (
                    <span className="text-xs font-mono font-medium text-cyan-400 bg-cyan-950/40 px-2 py-0.5 rounded border border-cyan-500/20">
                      Problem #{selectedPOTDVideo.problemNumber}
                    </span>
                  )}
                  <span className="text-xs text-zinc-400">
                    {selectedPOTDVideo.playlistTitle}
                  </span>
                </div>
                <h3 className="text-lg font-bold text-white tracking-tight pt-0.5">
                  {selectedPOTDVideo.problemTitle || selectedPOTDVideo.title}
                </h3>
              </div>

              <div className="flex items-center gap-3">
                <button
                  onClick={() => setShowPracticeWorkspace(!showPracticeWorkspace)}
                  className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition-all cursor-pointer shadow-md ${
                    showPracticeWorkspace
                      ? 'bg-cyan-500 text-zinc-950 shadow-cyan-500/20'
                      : 'bg-gradient-to-r from-cyan-500/20 to-purple-500/20 text-cyan-300 border border-cyan-500/30 hover:bg-cyan-500/30'
                  }`}
                >
                  <Code2 className="w-4 h-4" />
                  <span>{showPracticeWorkspace ? 'Hide Code Editor' : 'Apply: Practice Code (10 Tests)'}</span>
                </button>

                <button
                  onClick={() => handleToggleSolved(selectedPOTDVideo.videoId)}
                  className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold transition-all cursor-pointer border ${
                    isCurrentSolved
                      ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30'
                      : 'bg-zinc-800 hover:bg-zinc-700 text-zinc-300 border-white/10'
                  }`}
                >
                  <CheckCircle2 className={`w-4 h-4 ${isCurrentSolved ? 'text-emerald-400' : 'text-zinc-400'}`} />
                  <span>{isCurrentSolved ? 'Marked Solved' : 'Mark as Solved'}</span>
                </button>

                <a
                  href={selectedPOTDVideo.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="p-2 rounded-xl bg-zinc-800 hover:bg-zinc-700 text-zinc-400 hover:text-white border border-white/10 transition-colors"
                  title="Open on YouTube"
                >
                  <ExternalLink className="w-4 h-4" />
                </a>
              </div>
            </div>

            {/* Integrated Practice Workspace (Monaco + 10 Test Cases) */}
            {showPracticeWorkspace && (
              <div className="pt-2 animate-in slide-in-from-top-4 duration-300">
                <PracticeWorkspace
                  key={selectedPOTDVideo.videoId + selectedPOTDVideo.problemNumber}
                  problemNumber={selectedPOTDVideo.problemNumber || '486'}
                  problemTitle={selectedPOTDVideo.problemTitle || selectedPOTDVideo.title}
                  onSolveSuccess={() => {
                    if (!solvedPotds.includes(selectedPOTDVideo.videoId)) {
                      handleToggleSolved(selectedPOTDVideo.videoId);
                    }
                  }}
                />
              </div>
            )}
          </div>
        ) : (
          <div className="p-8 rounded-2xl bg-zinc-950/60 border border-white/5 flex flex-col items-center justify-center text-center space-y-4">
            <div className="w-14 h-14 rounded-2xl bg-zinc-900 border border-white/10 flex items-center justify-center text-zinc-500">
              <CalendarIcon className="w-7 h-7" />
            </div>
            <div className="space-y-1 max-w-md">
              <h4 className="text-lg font-semibold text-white">
                No Video on {MONTH_NAMES[currentMonth]} {selectedDay}, {currentYear}
              </h4>
              <p className="text-xs text-zinc-400 leading-relaxed">
                {activePlaylist ? (
                  <>
                    No POTD video was published on day {selectedDay} in playlist{' '}
                    <span className="text-cyan-400 font-medium">&ldquo;{activePlaylist.playlistTitle}&rdquo;</span>.
                  </>
                ) : (
                  <>
                    The channel does not have a playlist named{' '}
                    <span className="text-zinc-300 font-medium">&ldquo;Leetcode {MONTH_NAMES[currentMonth]} {currentYear}&rdquo;</span>.
                  </>
                )}
              </p>
            </div>

            {monthPOTDVideos.length > 0 ? (
              <div className="pt-2 w-full max-w-lg">
                <p className="text-xs font-medium text-zinc-400 mb-2">
                  Select an available POTD date for {MONTH_NAMES[currentMonth]} {currentYear}:
                </p>
                <div className="flex flex-wrap gap-2 justify-center">
                  {monthPOTDVideos.map((v) => (
                    <button
                      key={v.videoId}
                      onClick={() => handleSelectDay(v.day)}
                      className="px-3 py-1.5 rounded-lg bg-zinc-900 hover:bg-cyan-500/20 text-xs text-zinc-300 hover:text-cyan-300 border border-white/10 hover:border-cyan-500/30 transition-all cursor-pointer flex items-center gap-1.5"
                    >
                      <Play className="w-3 h-3 text-cyan-400 fill-cyan-400" />
                      <span>Day {v.day}</span>
                      {v.difficulty && (
                        <span className={`text-[10px] px-1.5 py-0.2 rounded font-semibold ${
                          v.difficulty === 'Easy' ? 'text-emerald-400' : v.difficulty === 'Medium' ? 'text-amber-400' : 'text-rose-400'
                        }`}>
                          {v.difficulty}
                        </span>
                      )}
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              <div className="pt-2 flex gap-3">
                <button
                  onClick={() => handleJumpToDate(2026, 7, 1)}
                  className="px-4 py-2 rounded-xl bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-400 border border-cyan-500/20 text-xs font-medium transition-colors cursor-pointer"
                >
                  View August 2026 Playlist
                </button>
                <button
                  onClick={() => handleJumpToDate(2026, 6, 1)}
                  className="px-4 py-2 rounded-xl bg-purple-500/10 hover:bg-purple-500/20 text-purple-400 border border-purple-500/20 text-xs font-medium transition-colors cursor-pointer"
                >
                  View July 2026 Playlist
                </button>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Grid: Recent Activity on Left, Interactive Calendar on Right */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-zinc-900/50 border border-white/5 rounded-2xl p-6 shadow-xl">
            <h3 className="font-semibold text-lg mb-6 text-white">Recent Activity</h3>
            <div className="space-y-4">
              {[
                { title: 'Leetcode 486 | Predict the Winner', desc: 'POTD August 1, 2026 • Game Theory & Dynamic Programming', time: 'Watched' },
                { title: 'Leetcode 877 | Stone Game', desc: 'POTD August 2, 2026 • Math & Greedy Strategy', time: 'Solved' },
                { title: 'Leetcode 1406 | Stone Game III', desc: 'POTD August 3, 2026 • Hard DP Solution', time: 'Completed' }
              ].map((item, i) => (
                <div key={i} className="flex items-center gap-4 p-4 rounded-xl bg-zinc-950/50 border border-white/5 hover:bg-white/5 transition-colors cursor-pointer group">
                  <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-cyan-500/20 to-purple-500/20 flex items-center justify-center group-hover:scale-105 transition-transform border border-white/5">
                    <Terminal className="w-5 h-5 text-cyan-400" />
                  </div>
                  <div className="flex-1">
                    <h5 className="font-medium text-white">{item.title}</h5>
                    <p className="text-sm text-zinc-400">{item.desc}</p>
                  </div>
                  <span className="text-xs font-medium text-cyan-400 bg-cyan-950/50 px-2.5 py-1 rounded-full border border-cyan-500/20">{item.time}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
        
        {/* Right Column: Calendar Connected to POTD Video Fetching */}
        <div className="space-y-6">
          <Calendar 
            currentDate={calendarDate}
            selectedDay={selectedDay}
            onPrevMonth={handlePrevMonth}
            onNextMonth={handleNextMonth}
            onSelectDay={handleSelectDay}
            onJumpToDate={handleJumpToDate}
          />
          
          <div className="bg-zinc-900/50 border border-white/5 rounded-2xl p-6 shadow-xl space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-emerald-400 text-xs font-semibold uppercase tracking-wider">
                <Trophy className="w-4 h-4" />
                <span>Grow: Achievements</span>
              </div>
              <Link 
                href="/dashboard/achievements" 
                className="text-xs text-cyan-400 hover:text-cyan-300 font-medium flex items-center gap-0.5"
              >
                View All →
              </Link>
            </div>

            {/* Level & XP Mini Bar */}
            <div className="p-3.5 rounded-xl bg-zinc-950/70 border border-white/5 space-y-2">
              <div className="flex items-center justify-between text-xs">
                <span className="font-bold text-white">Level 4 • Algorithm Specialist</span>
                <span className="text-cyan-400 font-mono font-semibold">1,150 XP</span>
              </div>
              <div className="w-full h-1.5 rounded-full bg-zinc-800 overflow-hidden">
                <div className="h-full rounded-full bg-gradient-to-r from-cyan-500 to-emerald-400 w-[65%]" />
              </div>
            </div>

            {/* Unlocked Badges Row */}
            <div>
              <span className="text-[11px] font-semibold text-zinc-400 uppercase tracking-wider block mb-2">
                Recent Badges Unlocked:
              </span>
              <div className="grid grid-cols-4 gap-2">
                {[
                  { icon: '⚔️', title: 'First Blood' },
                  { icon: '🔥', title: 'Streak 7' },
                  { icon: '👑', title: 'Minimax' },
                  { icon: '⚡', title: 'Flawless' }
                ].map((b, i) => (
                  <Link
                    key={i}
                    href="/dashboard/achievements"
                    className="p-2 rounded-xl bg-zinc-950/60 border border-white/5 hover:border-cyan-500/30 flex flex-col items-center justify-center text-center transition-all group"
                    title={b.title}
                  >
                    <span className="text-xl group-hover:scale-110 transition-transform">{b.icon}</span>
                    <span className="text-[9px] text-zinc-400 font-medium mt-1 truncate max-w-[50px]">{b.title}</span>
                  </Link>
                ))}
              </div>
            </div>

            <Link
              href="/dashboard/achievements"
              className="w-full py-2.5 rounded-xl bg-zinc-800 hover:bg-zinc-700 text-zinc-200 text-xs font-semibold flex items-center justify-center gap-2 border border-white/5 transition-colors cursor-pointer"
            >
              <Award className="w-3.5 h-3.5 text-emerald-400" />
              <span>Inspect Badges & Certificates</span>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
