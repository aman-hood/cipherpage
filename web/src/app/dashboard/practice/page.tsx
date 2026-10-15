'use client';

import { useState } from 'react';
import PracticeWorkspace from '@/components/PracticeWorkspace';
import VideoPlayer from '@/components/VideoPlayer';
import { 
  Code2, 
  BookOpen, 
  Play, 
  Sparkles, 
  ChevronDown, 
  ExternalLink,
  Layers,
  CheckCircle2,
  Tv
} from 'lucide-react';
import { CHANNEL_DATA } from '@/lib/youtubeData';

const ALL_PRACTICE_PROBLEMS = [
  {
    id: '486',
    problemNumber: '486',
    title: 'Predict the Winner',
    difficulty: 'Medium',
    category: 'Leetcode August 2026',
    url: 'https://www.youtube.com/watch?v=AdG8y5RwzpU',
  },
  {
    id: '877',
    problemNumber: '877',
    title: 'Stone Game',
    difficulty: 'Medium',
    category: 'Leetcode August 2026',
    url: 'https://www.youtube.com/watch?v=hRNW-YOEmlA',
  },
  {
    id: '1406',
    problemNumber: '1406',
    title: 'Stone Game III',
    difficulty: 'Hard',
    category: 'Leetcode August 2026',
    url: 'https://www.youtube.com/watch?v=wENy24037dc',
  },
  {
    id: '3731',
    problemNumber: '3731',
    title: 'Find Missing Elements',
    difficulty: 'Easy',
    category: 'Leetcode August 2026',
    url: 'https://www.youtube.com/watch?v=urHnY9shvXk',
  },
  {
    id: '2812',
    problemNumber: '2812',
    title: 'Find the Safest Path in a Grid',
    difficulty: 'Medium',
    category: 'Leetcode July 2026',
    url: 'https://www.youtube.com/watch?v=UoxKmaWJNBU',
  },
  {
    id: '3286',
    problemNumber: '3286',
    title: 'Find a Safe Walk Through a Grid',
    difficulty: 'Medium',
    category: 'Leetcode July 2026',
    url: 'https://www.youtube.com/watch?v=5hv1sJjHDIo',
  },
];

export default function PracticePage() {
  const [selectedProblem, setSelectedProblem] = useState(ALL_PRACTICE_PROBLEMS[0]);
  const [showVideo, setShowVideo] = useState(false);

  return (
    <div className="max-w-7xl mx-auto space-y-6 animate-in fade-in duration-500">
      {/* Top Banner: LAG Apply Knowledge */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-white/5 pb-6">
        <div>
          <div className="flex items-center gap-2 text-cyan-400 text-xs font-semibold uppercase tracking-wider mb-1">
            <Code2 className="w-4 h-4" />
            <span>Apply Knowledge • Monaco IDE Workspace</span>
          </div>
          <h1 className="text-3xl font-bold tracking-tight text-white">Algorithm Practice Lab</h1>
          <p className="text-zinc-400 text-sm mt-1">
            Solve channel POTD problems with multi-language support and <span className="text-cyan-400 font-medium">10 automated test cases (5 basic, 3 medium, 2 hard)</span>.
          </p>
        </div>

        {/* Problem Selector & Video Toggle */}
        <div className="flex items-center gap-3">
          <div className="relative">
            <select
              value={selectedProblem.problemNumber}
              onChange={(e) => {
                const found = ALL_PRACTICE_PROBLEMS.find(p => p.problemNumber === e.target.value);
                if (found) setSelectedProblem(found);
              }}
              className="px-4 py-2.5 rounded-xl bg-zinc-900 border border-white/10 text-white text-xs font-semibold hover:border-cyan-500/40 focus:outline-hidden focus:border-cyan-500 cursor-pointer transition-colors"
            >
              {ALL_PRACTICE_PROBLEMS.map((p) => (
                <option key={p.id} value={p.problemNumber} className="bg-zinc-900 text-white">
                  #{p.problemNumber} {p.title} ({p.difficulty})
                </option>
              ))}
            </select>
          </div>

          <button
            onClick={() => setShowVideo(!showVideo)}
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-zinc-800 hover:bg-zinc-700 text-zinc-200 text-xs font-semibold border border-white/10 transition-colors cursor-pointer"
          >
            <Play className="w-3.5 h-3.5 text-cyan-400 fill-cyan-400" />
            <span>{showVideo ? 'Hide Lecture' : 'Watch Lecture'}</span>
          </button>
        </div>
      </div>

      {/* Optional Lecture Video Collapse */}
      {showVideo && (
        <div className="p-4 rounded-2xl bg-zinc-900/60 border border-cyan-500/20 shadow-2xl space-y-3 animate-in slide-in-from-top-4 duration-300">
          <div className="flex items-center justify-between text-xs">
            <span className="font-semibold text-cyan-400 flex items-center gap-1.5">
              <Tv className="w-4 h-4" /> YouTube Video Lecture for Problem #{selectedProblem.problemNumber}
            </span>
            <a
              href={selectedProblem.url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-zinc-400 hover:text-white flex items-center gap-1"
            >
              Open on YouTube <ExternalLink className="w-3 h-3" />
            </a>
          </div>
          <div className="max-w-3xl mx-auto rounded-xl overflow-hidden border border-white/10">
            <VideoPlayer
              key={selectedProblem.url}
              src={selectedProblem.url}
              controls={true}
              playing={false}
            />
          </div>
        </div>
      )}

      {/* Main Practice Workspace: Monaco Editor & 10 Test Cases */}
      <PracticeWorkspace
        key={selectedProblem.id}
        problemNumber={selectedProblem.problemNumber}
        problemTitle={selectedProblem.title}
      />
    </div>
  );
}
