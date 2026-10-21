'use client';

import { useState, useEffect } from 'react';
import VideoPlayer from '@/components/VideoPlayer';
import { useAuth } from '@/features/auth/hooks/useAuth';
import { recordUserActivity } from '@/services/gamificationService';
import { 
  Play, 
  CheckCircle2, 
  ExternalLink, 
  Sparkles, 
  ListVideo, 
  Clock, 
  Share2, 
  BookMarked, 
  Search, 
  Plus, 
  Tv, 
  Bookmark, 
  BookOpen 
} from 'lucide-react';
import CourseRAGAssistant from '@/components/CourseRAGAssistant';

interface VideoLesson {
  id: string;
  title: string;
  duration: string;
  url: string;
  category: string;
  description: string;
}

const DEFAULT_PLAYLIST: VideoLesson[] = [
  {
    id: 'AdG8y5RwzpU',
    title: 'Leetcode 486 | Predict the Winner | Medium | POTD August 1, 2026',
    duration: 'POTD Aug 1',
    url: 'https://www.youtube.com/watch?v=AdG8y5RwzpU',
    category: 'Leetcode August 2026',
    description: 'Detailed walkthrough and optimal dynamic programming / game theory solution for LeetCode 486 Predict the Winner.',
  },
  {
    id: 'hRNW-YOEmlA',
    title: 'Leetcode 877 | Stone Game | Medium | POTD August 2, 2026',
    duration: 'POTD Aug 2',
    url: 'https://www.youtube.com/watch?v=hRNW-YOEmlA',
    category: 'Leetcode August 2026',
    description: 'Mathematical intuition and optimal minimax/DP approach for Stone Game on LeetCode.',
  },
  {
    id: 'wENy24037dc',
    title: 'Leetcode 1406 | Stone Game III | Hard | POTD August 3, 2026',
    duration: 'POTD Aug 3',
    url: 'https://www.youtube.com/watch?v=wENy24037dc',
    category: 'Leetcode August 2026',
    description: 'Comprehensive analysis of LeetCode 1406 Stone Game III using bottom-up DP and game state evaluation.',
  },
  {
    id: 'urHnY9shvXk',
    title: 'Leetcode 3731 | Find Missing Elements | Easy | POTD August 4, 2026',
    duration: 'POTD Aug 4',
    url: 'https://www.youtube.com/watch?v=urHnY9shvXk',
    category: 'Leetcode August 2026',
    description: 'Clean array traversal and hash set approach for LeetCode 3731.',
  },
  {
    id: 'w9JtDI-M0kk',
    title: 'Leetcode 3310 | Remove Methods From Project | Medium | POTD August 5, 2026',
    duration: 'POTD Aug 5',
    url: 'https://www.youtube.com/watch?v=w9JtDI-M0kk',
    category: 'Leetcode August 2026',
    description: 'Graph component isolation, DFS reachability and BFS algorithms explained step by step.',
  },
  {
    id: 'ymwTZ4XxxgY',
    title: 'Leetcode 3345 | Smallest Divisible Digit Product I | Easy | POTD August 6, 2026',
    duration: 'POTD Aug 6',
    url: 'https://www.youtube.com/watch?v=ymwTZ4XxxgY',
    category: 'Leetcode August 2026',
    description: 'Digit product arithmetic and modulo constraints for LeetCode 3345.',
  },
  {
    id: 'JSSoUPwsHro',
    title: 'Leetcode 2958 | Length of Longest Subarray With at Most K Frequency | Medium | POTD August 12, 2026',
    duration: 'POTD Aug 12',
    url: 'https://www.youtube.com/watch?v=JSSoUPwsHro',
    category: 'Leetcode August 2026',
    description: 'Two-pointer sliding window technique with frequency map optimization.',
  },
  {
    id: '97z3WHbfcSM',
    title: 'Leetcode 3090 | Maximum Length Substring With Two Occurrences | Easy | POTD August 14, 2026',
    duration: 'POTD Aug 14',
    url: 'https://www.youtube.com/watch?v=97z3WHbfcSM',
    category: 'Leetcode August 2026',
    description: 'Sliding window technique maintaining maximum allowed character frequencies.',
  },
  {
    id: '9Bs9UZFdG3U',
    title: 'Leetcode 3702 | Longest Subsequence With Non-Zero Bitwise XOR | Medium | POTD August 15, 2026',
    duration: 'POTD Aug 15',
    url: 'https://www.youtube.com/watch?v=9Bs9UZFdG3U',
    category: 'Leetcode August 2026',
    description: 'Bit manipulation properties and subsequence selection for non-zero bitwise XOR.',
  },
  {
    id: 'UoxKmaWJNBU',
    title: 'Leetcode 2812 | Find the Safest Path in a Grid | Medium | POTD July 1, 2026',
    duration: 'POTD Jul 1',
    url: 'https://www.youtube.com/watch?v=UoxKmaWJNBU',
    category: 'Leetcode July 2026',
    description: 'Multi-source BFS + Dijkstra / Binary Search for optimal grid safety factor.',
  },
  {
    id: '5hv1sJjHDIo',
    title: 'Leetcode 3286 | Find a Safe Walk Through a Grid | Medium | POTD July 2, 2026',
    duration: 'POTD Jul 2',
    url: 'https://www.youtube.com/watch?v=5hv1sJjHDIo',
    category: 'Leetcode July 2026',
    description: '0-1 BFS / Dijkstra shortest path through grid with health constraint.',
  },
];

export default function CoursesPage() {
  const { profile, user } = useAuth();
  const userId = user?.uid || (profile?.id ? String(profile.id) : '');

  const [playlist, setPlaylist] = useState<VideoLesson[]>(DEFAULT_PLAYLIST);
  const [activeVideo, setActiveVideo] = useState<VideoLesson>(DEFAULT_PLAYLIST[0]);
  const [customUrl, setCustomUrl] = useState('');
  const [customTitle, setCustomTitle] = useState('');
  const [showAddForm, setShowAddForm] = useState(false);
  const [completedIds, setCompletedIds] = useState<string[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [activeTab, setActiveTab] = useState<'overview' | 'notes'>('overview');
  const [userNotes, setUserNotes] = useState('');
  const [showRAGAssistant, setShowRAGAssistant] = useState(false);

  // Load completed video progress and custom playlist from user-scoped storage
  useEffect(() => {
    if (!userId) {
      setCompletedIds([]);
      setPlaylist(DEFAULT_PLAYLIST);
      setActiveVideo(DEFAULT_PLAYLIST[0]);
      setUserNotes('');
      return;
    }

    const storagePrefix = `cipherpage_${userId}`;
    try {
      const savedCompleted = localStorage.getItem(`${storagePrefix}_completed_videos`);
      if (savedCompleted) {
        setCompletedIds(JSON.parse(savedCompleted));
      } else {
        setCompletedIds([]);
      }

      const savedPlaylist = localStorage.getItem(`${storagePrefix}_custom_playlist`);
      if (savedPlaylist) {
        const parsed = JSON.parse(savedPlaylist);
        if (Array.isArray(parsed) && parsed.length > 0) {
          setPlaylist(parsed);
          setActiveVideo(parsed[0]);
        } else {
          setPlaylist(DEFAULT_PLAYLIST);
          setActiveVideo(DEFAULT_PLAYLIST[0]);
        }
      } else {
        setPlaylist(DEFAULT_PLAYLIST);
        setActiveVideo(DEFAULT_PLAYLIST[0]);
      }

      const savedNotes = localStorage.getItem(`${storagePrefix}_video_notes`);
      if (savedNotes) {
        setUserNotes(savedNotes);
      } else {
        setUserNotes('');
      }
    } catch (e) {
      console.error(e);
    }
  }, [userId]);

  const handleToggleComplete = (id: string) => {
    if (!userId) return;
    const isNowCompleted = !completedIds.includes(id);
    const updated = isNowCompleted
      ? [...completedIds, id]
      : completedIds.filter(item => item !== id);
    setCompletedIds(updated);

    const storagePrefix = `cipherpage_${userId}`;
    try {
      localStorage.setItem(`${storagePrefix}_completed_videos`, JSON.stringify(updated));
    } catch {}

    if (isNowCompleted) {
      const matched = playlist.find(p => p.id === id);
      if (matched) {
        void recordUserActivity({
          activity_type: 'VIDEO_WATCHED',
          title: matched.title,
          description: matched.category,
          action_label: 'Completed',
        });
      }
    }
  };

  const handleAddCustomVideo = (e: React.FormEvent) => {
    e.preventDefault();
    if (!customUrl.trim() || !userId) return;

    const newLesson: VideoLesson = {
      id: Date.now().toString(),
      title: customTitle.trim() || 'Custom YouTube Video',
      duration: 'Custom',
      url: customUrl.trim(),
      category: 'My Channel',
      description: 'Custom video added from YouTube channel.',
    };

    const updatedPlaylist = [newLesson, ...playlist];
    setPlaylist(updatedPlaylist);
    setActiveVideo(newLesson);
    setCustomUrl('');
    setCustomTitle('');
    setShowAddForm(false);

    const storagePrefix = `cipherpage_${userId}`;
    try {
      localStorage.setItem(`${storagePrefix}_custom_playlist`, JSON.stringify(updatedPlaylist));
    } catch {}
  };

  const handleSaveNotes = (val: string) => {
    setUserNotes(val);
    if (!userId) return;
    const storagePrefix = `cipherpage_${userId}`;
    try {
      localStorage.setItem(`${storagePrefix}_video_notes`, val);
    } catch {}
  };


  const filteredPlaylist = playlist.filter(v =>
    v.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    v.category.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const progressPercent = Math.round((completedIds.length / playlist.length) * 100) || 0;

  return (
    <div className="max-w-7xl mx-auto space-y-8 animate-in fade-in duration-500">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-white/5 pb-6">
        <div>
          <div className="flex items-center gap-2 text-cyan-400 text-xs font-semibold uppercase tracking-wider mb-1">
            <Tv className="w-4 h-4" />
            <span>Interactive Video Lectures</span>
          </div>
          <h1 className="text-3xl font-bold tracking-tight text-white">Course Video Library</h1>
          <p className="text-zinc-400 text-sm mt-1">
            Stream high-definition lessons powered by <span className="text-cyan-400 font-medium">react-player</span> with progress tracking and custom YouTube support.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setShowRAGAssistant(true)}
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-indigo-500 to-cyan-500 hover:from-indigo-400 hover:to-cyan-400 text-white font-semibold text-sm transition-all shadow-[0_0_20px_-3px_rgba(99,102,241,0.4)] cursor-pointer"
          >
            <BookOpen className="w-4 h-4" />
            <span>Ask Course AI</span>
          </button>

          <button
            onClick={() => setShowAddForm(!showAddForm)}
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-zinc-800 hover:bg-zinc-700 text-zinc-200 font-semibold text-sm transition-all border border-white/10 cursor-pointer"
          >
            <Plus className="w-4 h-4" />
            {showAddForm ? 'Close Add Video' : 'Add Video'}
          </button>
        </div>
      </div>

      {/* Add Custom Video Drawer / Form */}
      {showAddForm && (
        <form
          onSubmit={handleAddCustomVideo}
          className="p-6 rounded-2xl bg-zinc-900/80 border border-cyan-500/30 backdrop-blur-md shadow-2xl space-y-4 animate-in slide-in-from-top-4 duration-300"
        >
          <div className="flex items-center gap-2 text-cyan-400 font-medium text-sm">
            <Sparkles className="w-4 h-4" />
            <span>Add Any Video From Your YouTube Channel</span>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-zinc-400 mb-1.5">YouTube Video URL</label>
              <input
                type="url"
                required
                placeholder="https://www.youtube.com/watch?v=..."
                value={customUrl}
                onChange={(e) => setCustomUrl(e.target.value)}
                className="w-full px-4 py-2.5 rounded-xl bg-zinc-950 border border-white/10 text-white placeholder-zinc-500 text-sm focus:outline-hidden focus:border-cyan-500 transition-colors"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-zinc-400 mb-1.5">Video Title (Optional)</label>
              <input
                type="text"
                placeholder="e.g. Masterclass Episode 1"
                value={customTitle}
                onChange={(e) => setCustomTitle(e.target.value)}
                className="w-full px-4 py-2.5 rounded-xl bg-zinc-950 border border-white/10 text-white placeholder-zinc-500 text-sm focus:outline-hidden focus:border-cyan-500 transition-colors"
              />
            </div>
          </div>
          <div className="flex justify-end gap-3 pt-2">
            <button
              type="button"
              onClick={() => setShowAddForm(false)}
              className="px-4 py-2 rounded-xl text-zinc-400 hover:text-white text-sm hover:bg-white/5 transition-colors cursor-pointer"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-5 py-2 rounded-xl bg-gradient-to-r from-cyan-500 to-cyan-400 text-zinc-950 font-semibold text-sm hover:brightness-110 transition-all cursor-pointer shadow-lg shadow-cyan-500/20"
            >
              Load into Player
            </button>
          </div>
        </form>
      )}

      {/* Main Grid: Player on Left, Playlist on Right */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Column: Player & Video Info */}
        <div className="lg:col-span-2 space-y-6">
          {/* React Player Container */}
          <div className="rounded-2xl p-2 bg-zinc-900/40 border border-white/5 shadow-2xl">
            <VideoPlayer
              key={activeVideo.id + activeVideo.url}
              src={activeVideo.url}
              controls={true}
              playing={false}
              onEnded={() => handleToggleComplete(activeVideo.id)}
            />
          </div>

          {/* Video Metadata & Actions */}
          <div className="p-6 rounded-2xl bg-zinc-900/40 border border-white/5 shadow-xl space-y-5">
            <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className="px-2.5 py-0.5 rounded-full text-xs font-medium bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                    {activeVideo.category}
                  </span>
                  <span className="flex items-center gap-1 text-xs text-zinc-400">
                    <Clock className="w-3.5 h-3.5" />
                    {activeVideo.duration}
                  </span>
                </div>
                <h2 className="text-2xl font-bold text-white tracking-tight pt-1">
                  {activeVideo.title}
                </h2>
              </div>

              {/* Action Buttons */}
              <div className="flex items-center gap-3">
                <button
                  onClick={() => handleToggleComplete(activeVideo.id)}
                  className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-medium transition-all cursor-pointer border ${
                    completedIds.includes(activeVideo.id)
                      ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30'
                      : 'bg-zinc-800/80 hover:bg-zinc-800 text-zinc-300 border-white/10'
                  }`}
                >
                  <CheckCircle2 className={`w-4 h-4 ${completedIds.includes(activeVideo.id) ? 'text-emerald-400' : 'text-zinc-400'}`} />
                  {completedIds.includes(activeVideo.id) ? 'Completed' : 'Mark as Done'}
                </button>

                <a
                  href={activeVideo.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="p-2.5 rounded-xl bg-zinc-800/80 hover:bg-zinc-800 text-zinc-400 hover:text-white border border-white/10 transition-colors"
                  title="Open on YouTube"
                >
                  <ExternalLink className="w-4 h-4" />
                </a>
              </div>
            </div>

            {/* Tabs: Overview & Notes */}
            <div className="border-t border-white/5 pt-4">
              <div className="flex gap-4 border-b border-white/5 pb-2 text-sm font-medium">
                <button
                  onClick={() => setActiveTab('overview')}
                  className={`pb-2 border-b-2 transition-colors cursor-pointer ${
                    activeTab === 'overview'
                      ? 'border-cyan-400 text-cyan-400'
                      : 'border-transparent text-zinc-400 hover:text-white'
                  }`}
                >
                  Overview & Details
                </button>
                <button
                  onClick={() => setActiveTab('notes')}
                  className={`pb-2 border-b-2 transition-colors cursor-pointer flex items-center gap-1.5 ${
                    activeTab === 'notes'
                      ? 'border-cyan-400 text-cyan-400'
                      : 'border-transparent text-zinc-400 hover:text-white'
                  }`}
                >
                  <Bookmark className="w-3.5 h-3.5" />
                  Lecture Notes
                </button>
              </div>

              {activeTab === 'overview' ? (
                <div className="pt-4 text-zinc-300 text-sm leading-relaxed space-y-3">
                  <p>{activeVideo.description}</p>
                  
                  {/* RAG Learning Assistant Quick Banner */}
                  <div 
                    onClick={() => setShowRAGAssistant(true)}
                    className="p-4 rounded-xl bg-gradient-to-r from-indigo-950/40 to-cyan-950/40 border border-cyan-500/20 hover:border-cyan-500/40 flex items-center justify-between gap-3 cursor-pointer transition-all group"
                  >
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-lg bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400 group-hover:scale-105 transition-transform">
                        <Sparkles className="w-4 h-4" />
                      </div>
                      <div>
                        <p className="text-xs font-semibold text-white group-hover:text-cyan-300 transition-colors">
                          Have questions about this topic? Ask the Course AI
                        </p>
                        <p className="text-[11px] text-zinc-400">
                          Instant grounded answers with citations from verified course notes &amp; syllabus.
                        </p>
                      </div>
                    </div>
                    <span className="text-xs font-medium text-cyan-400 group-hover:translate-x-0.5 transition-transform flex items-center gap-1">
                      Open RAG Q&amp;A &rarr;
                    </span>
                  </div>

                  <div className="p-4 rounded-xl bg-zinc-950/50 border border-white/5 flex items-center gap-3">
                    <div className="w-2.5 h-2.5 rounded-full bg-cyan-400 animate-pulse" />
                    <span className="text-xs text-zinc-400">
                      Direct YouTube streaming via <code className="text-cyan-400 font-mono">react-player</code> with adaptive bitrate and cross-device syncing.
                    </span>
                  </div>
                </div>
              ) : (
                <div className="pt-4 space-y-3">
                  <textarea
                    rows={4}
                    placeholder="Take notes while watching this lecture... (Saved automatically)"
                    value={userNotes}
                    onChange={(e) => handleSaveNotes(e.target.value)}
                    className="w-full p-4 rounded-xl bg-zinc-950/80 border border-white/10 text-white placeholder-zinc-500 text-sm focus:outline-hidden focus:border-cyan-500 transition-colors"
                  />
                  <div className="flex items-center justify-between text-xs text-zinc-500">
                    <span>Notes are saved locally in your browser.</span>
                    <span>{userNotes.length} characters</span>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Right Column: Playlist & Progress Tracker */}
        <div className="space-y-6">
          {/* Progress Card */}
          <div className="p-6 rounded-2xl bg-zinc-900/40 border border-white/5 shadow-xl relative overflow-hidden">
            <div className="flex items-center justify-between mb-3">
              <span className="text-sm font-semibold text-white">Course Progress</span>
              <span className="text-sm font-bold text-cyan-400">{progressPercent}%</span>
            </div>
            <div className="w-full h-2 rounded-full bg-zinc-800 overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-cyan-500 to-purple-500 rounded-full transition-all duration-500"
                style={{ width: `${progressPercent}%` }}
              />
            </div>
            <p className="text-xs text-zinc-400 mt-2.5">
              {completedIds.length} of {playlist.length} lessons completed
            </p>
          </div>

          {/* Playlist Card */}
          <div className="rounded-2xl bg-zinc-900/40 border border-white/5 shadow-xl overflow-hidden flex flex-col">
            <div className="p-4 border-b border-white/5 flex items-center justify-between gap-3 bg-zinc-900/70">
              <div className="flex items-center gap-2">
                <ListVideo className="w-4 h-4 text-cyan-400" />
                <h3 className="font-semibold text-white text-sm">Course Playlist</h3>
              </div>
              <span className="text-xs text-zinc-400 font-medium">
                {playlist.length} lessons
              </span>
            </div>

            {/* Search within playlist */}
            <div className="p-3 border-b border-white/5">
              <div className="relative">
                <Search className="w-4 h-4 text-zinc-500 absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  placeholder="Filter lessons..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-9 pr-3 py-1.5 rounded-lg bg-zinc-950 border border-white/5 text-white placeholder-zinc-500 text-xs focus:outline-hidden focus:border-cyan-500 transition-colors"
                />
              </div>
            </div>

            {/* Video List Items */}
            <div className="divide-y divide-white/5 max-h-[500px] overflow-y-auto">
              {filteredPlaylist.map((video, idx) => {
                const isActive = activeVideo.id === video.id;
                const isCompleted = completedIds.includes(video.id);

                return (
                  <button
                    key={video.id}
                    onClick={() => setActiveVideo(video)}
                    className={`w-full text-left p-4 transition-colors flex items-start gap-3 cursor-pointer group ${
                      isActive
                        ? 'bg-cyan-500/10 border-l-2 border-cyan-400'
                        : 'hover:bg-white/5'
                    }`}
                  >
                    <div className="flex-shrink-0 mt-0.5">
                      <div className={`w-7 h-7 rounded-lg flex items-center justify-center text-xs font-semibold ${
                        isActive
                          ? 'bg-cyan-500 text-zinc-950 font-bold'
                          : isCompleted
                          ? 'bg-emerald-500/20 text-emerald-400'
                          : 'bg-zinc-800 text-zinc-400 group-hover:text-white'
                      }`}>
                        {isCompleted ? (
                          <CheckCircle2 className="w-4 h-4" />
                        ) : (
                          idx + 1
                        )}
                      </div>
                    </div>

                    <div className="flex-1 min-w-0">
                      <p className={`text-sm font-medium line-clamp-2 leading-snug ${
                        isActive ? 'text-cyan-400 font-semibold' : 'text-zinc-200 group-hover:text-white'
                      }`}>
                        {video.title}
                      </p>
                      <div className="flex items-center gap-2 mt-1.5 text-xs text-zinc-500">
                        <span>{video.category}</span>
                        <span>•</span>
                        <span>{video.duration}</span>
                        {isActive && (
                          <>
                            <span>•</span>
                            <span className="text-cyan-400 font-medium flex items-center gap-1">
                              <Play className="w-3 h-3 fill-cyan-400" /> Playing
                            </span>
                          </>
                        )}
                      </div>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>
        </div>
      </div>

      {/* Course RAG Assistant Modal / Drawer (Phase 4: RAG-04) */}
      <CourseRAGAssistant
        isOpen={showRAGAssistant}
        onClose={() => setShowRAGAssistant(false)}
        courseId={1}
        courseTitle={activeVideo.category}
      />
    </div>
  );
}
