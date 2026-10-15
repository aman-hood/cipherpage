'use client';

import Image from "next/image";
import { 
  Terminal, 
  BookOpen, 
  Trophy, 
  ArrowRight, 
  Play, 
  Code2, 
  ShieldCheck, 
  Sparkles, 
  Layers, 
  Award, 
  CheckCircle2,
  ExternalLink,
  Cpu
} from "lucide-react";
import Link from "next/link";
import { useState } from "react";

export default function Home() {
  const [demoTab, setDemoTab] = useState<'learn' | 'apply' | 'grow'>('apply');
  const [selectedLanguage, setSelectedLanguage] = useState('Python');

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-50 font-sans selection:bg-cyan-500/30">
      {/* Navigation */}
      <nav className="fixed w-full z-50 border-b border-white/5 bg-zinc-950/80 backdrop-blur-md">
        <div className="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Image src="/logo.png" alt="CipherPage Logo" width={40} height={40} className="w-10 h-10 object-contain" priority />
            <div>
              <span className="text-xl font-bold tracking-tight text-white block">CipherPage</span>
              <span className="text-[10px] font-semibold tracking-wider text-cyan-400 uppercase block -mt-1">
                LAG — Learn • Apply • Grow
              </span>
            </div>
          </div>
          
          <div className="hidden md:flex items-center gap-8 text-sm font-medium text-zinc-400">
            <Link href="#lag-framework" className="hover:text-white transition-colors">LAG Ecosystem</Link>
            <Link href="#learn" className="hover:text-white transition-colors">Learn</Link>
            <Link href="#apply" className="hover:text-white transition-colors">Apply</Link>
            <Link href="#grow" className="hover:text-white transition-colors">Grow</Link>
          </div>

          <div className="flex items-center gap-4">
            <Link href="/login" className="text-sm font-medium text-zinc-300 hover:text-white transition-colors">
              Sign In
            </Link>
            <Link 
              href="/register" 
              className="text-sm font-semibold bg-gradient-to-r from-cyan-500 to-cyan-400 text-zinc-950 px-5 py-2.5 rounded-full hover:brightness-110 transition-all shadow-[0_0_20px_-3px_rgba(6,182,212,0.4)]"
            >
              Get Started Free
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative pt-44 pb-24 overflow-hidden">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-cyan-500/15 rounded-full blur-[140px] pointer-events-none" />
        <div className="absolute top-1/3 left-1/3 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-purple-500/15 rounded-full blur-[120px] pointer-events-none" />
        
        <div className="max-w-7xl mx-auto px-6 relative z-10 flex flex-col items-center text-center">
          {/* LAG Badge */}
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full border border-cyan-500/30 bg-cyan-500/10 text-cyan-400 text-xs font-semibold tracking-wide uppercase mb-8 shadow-sm">
            <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
            LAG Methodology: Learn • Apply • Grow
          </div>
          
          <h1 className="text-5xl md:text-7xl lg:text-8xl font-black tracking-tight mb-8 max-w-5xl leading-[1.05]">
            Learn. Apply. <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-purple-400 to-purple-500">Grow.</span>
          </h1>
          
          <p className="text-lg md:text-xl text-zinc-300 max-w-3xl mb-12 leading-relaxed">
            A coding-first platform where theoretical concepts meet immediate practical execution. Watch high-definition YouTube video lectures, apply your knowledge directly in our integrated <span className="text-cyan-400 font-medium">Monaco Editor with 10 automated testcases</span>, and grow into a career-ready software engineer.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 items-center w-full justify-center">
            <Link 
              href="/register" 
              className="w-full sm:w-auto px-8 py-4 bg-gradient-to-r from-cyan-500 to-cyan-400 hover:brightness-110 text-zinc-950 rounded-full font-bold transition-all transform hover:scale-105 flex items-center justify-center gap-2 shadow-[0_0_40px_-5px_rgba(6,182,212,0.5)]"
            >
              Start Learning & Practicing Free <ArrowRight className="w-5 h-5" />
            </Link>
            <Link 
              href="/dashboard" 
              className="w-full sm:w-auto px-8 py-4 bg-zinc-900/80 hover:bg-zinc-800 text-white rounded-full font-semibold border border-white/10 transition-all flex items-center justify-center gap-2"
            >
              <Terminal className="w-5 h-5 text-cyan-400" /> Open Web Workspace
            </Link>
          </div>
        </div>
      </section>

      {/* The 3 Pillars of LAG Section */}
      <section id="lag-framework" className="py-24 bg-zinc-900/40 border-y border-white/5 relative">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-xs font-bold uppercase tracking-widest text-cyan-400 mb-3">
              The CipherPage Educational Architecture
            </h2>
            <h3 className="text-3xl md:text-5xl font-bold tracking-tight text-white">
              The LAG Framework
            </h3>
            <p className="text-zinc-400 mt-4 text-base leading-relaxed">
              Designed around active recall and real-time execution. Every single topic follows a structured 3-stage feedback loop.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {/* Pillar 1: Learn Concepts */}
            <div id="learn" className="p-8 rounded-3xl bg-zinc-950/80 border border-white/5 hover:border-cyan-500/40 transition-all group flex flex-col relative overflow-hidden shadow-xl">
              <div className="absolute top-0 right-0 w-32 h-32 bg-cyan-500/10 rounded-full blur-[40px] pointer-events-none" />
              <div className="w-14 h-14 bg-cyan-500/10 rounded-2xl flex items-center justify-center mb-6 border border-cyan-500/20 group-hover:scale-110 transition-transform">
                <BookOpen className="w-7 h-7 text-cyan-400" />
              </div>
              <div className="text-xs font-mono font-semibold text-cyan-400 uppercase tracking-wider mb-2">Stage 01 • L</div>
              <h4 className="text-2xl font-bold mb-4 text-white">Learn Concepts</h4>
              <p className="text-zinc-400 leading-relaxed text-sm mb-6 flex-1">
                Structured programming courses delivered through high-quality video lectures and concise documentation.
              </p>
              
              <ul className="space-y-2.5 text-xs text-zinc-300 border-t border-white/5 pt-5">
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-cyan-400 flex-shrink-0" />
                  <span>Curated YouTube Channel (@cipherpage) series</span>
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-cyan-400 flex-shrink-0" />
                  <span>Daily LeetCode Problem of the Day breakdowns</span>
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-cyan-400 flex-shrink-0" />
                  <span>Monthly organized algorithm playlists</span>
                </li>
              </ul>
            </div>
            
            {/* Pillar 2: Apply Knowledge */}
            <div id="apply" className="p-8 rounded-3xl bg-zinc-950/80 border border-white/5 hover:border-purple-500/40 transition-all group flex flex-col relative overflow-hidden shadow-xl">
              <div className="absolute top-0 right-0 w-32 h-32 bg-purple-500/10 rounded-full blur-[40px] pointer-events-none" />
              <div className="w-14 h-14 bg-purple-500/10 rounded-2xl flex items-center justify-center mb-6 border border-purple-500/20 group-hover:scale-110 transition-transform">
                <Terminal className="w-7 h-7 text-purple-400" />
              </div>
              <div className="text-xs font-mono font-semibold text-purple-400 uppercase tracking-wider mb-2">Stage 02 • A</div>
              <h4 className="text-2xl font-bold mb-4 text-white">Apply Knowledge</h4>
              <p className="text-zinc-400 leading-relaxed text-sm mb-6 flex-1">
                Practice directly within our integrated Monaco editor. Automated testing and isolated execution.
              </p>

              <ul className="space-y-2.5 text-xs text-zinc-300 border-t border-white/5 pt-5">
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-purple-400 flex-shrink-0" />
                  <span>10 Test Cases per problem: 5 Basic, 3 Medium, 2 Hard</span>
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-purple-400 flex-shrink-0" />
                  <span>Full Monaco IDE: Python, C++, Java, JS, TS, Go</span>
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-purple-400 flex-shrink-0" />
                  <span>Instant sandboxed execution with millisecond timing</span>
                </li>
              </ul>
            </div>
            
            {/* Pillar 3: Grow Professionally */}
            <div id="grow" className="p-8 rounded-3xl bg-zinc-950/80 border border-white/5 hover:border-emerald-500/40 transition-all group flex flex-col relative overflow-hidden shadow-xl">
              <div className="absolute top-0 right-0 w-32 h-32 bg-emerald-500/10 rounded-full blur-[40px] pointer-events-none" />
              <div className="w-14 h-14 bg-emerald-500/10 rounded-2xl flex items-center justify-center mb-6 border border-emerald-500/20 group-hover:scale-110 transition-transform">
                <Trophy className="w-7 h-7 text-emerald-400" />
              </div>
              <div className="text-xs font-mono font-semibold text-emerald-400 uppercase tracking-wider mb-2">Stage 03 • G</div>
              <h4 className="text-2xl font-bold mb-4 text-white">Grow Professionally</h4>
              <p className="text-zinc-400 leading-relaxed text-sm mb-6 flex-1">
                Earn badges, verifiable certificates, and build a portfolio of real-world projects as you progress.
              </p>

              <ul className="space-y-2.5 text-xs text-zinc-300 border-t border-white/5 pt-5">
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
                  <span>Daily calendar streak tracking & milestones</span>
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
                  <span>Difficulty badges & problem mastery analytics</span>
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
                  <span>Verifiable portfolio ready for technical interviews</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Interactive Live Preview: Learn and Apply in Action */}
      <section className="py-24 max-w-7xl mx-auto px-6">
        <div className="text-center max-w-3xl mx-auto mb-14">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-500/10 text-cyan-400 text-xs font-bold uppercase mb-4 border border-cyan-500/20">
            <Sparkles className="w-3.5 h-3.5" />
            Live Practice Preview
          </div>
          <h3 className="text-3xl md:text-4xl font-bold text-white tracking-tight">
            From Video Lecture to 10 Passing Testcases
          </h3>
          <p className="text-zinc-400 mt-3 text-sm">
            Experience how seamlessly theoretical understanding transforms into verified code implementation.
          </p>
        </div>

        {/* Mock IDE & Video Container */}
        <div className="rounded-3xl bg-zinc-900/60 border border-white/10 p-6 md:p-8 shadow-2xl space-y-6">
          <div className="flex flex-wrap items-center justify-between gap-4 border-b border-white/5 pb-4">
            <div className="flex items-center gap-3">
              <span className="text-xs font-mono font-bold text-cyan-400 bg-cyan-950/60 px-2.5 py-1 rounded border border-cyan-500/30">
                Leetcode #486
              </span>
              <h4 className="text-lg font-bold text-white">Predict the Winner</h4>
              <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/20">
                Medium
              </span>
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={() => setDemoTab('learn')}
                className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition-all cursor-pointer ${
                  demoTab === 'learn'
                    ? 'bg-cyan-500 text-zinc-950 shadow-md'
                    : 'bg-zinc-800 text-zinc-400 hover:text-white'
                }`}
              >
                1. Learn (Video)
              </button>
              <button
                onClick={() => setDemoTab('apply')}
                className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition-all cursor-pointer ${
                  demoTab === 'apply'
                    ? 'bg-cyan-500 text-zinc-950 shadow-md'
                    : 'bg-zinc-800 text-zinc-400 hover:text-white'
                }`}
              >
                2. Apply (Monaco & 10 Tests)
              </button>
              <button
                onClick={() => setDemoTab('grow')}
                className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition-all cursor-pointer ${
                  demoTab === 'grow'
                    ? 'bg-cyan-500 text-zinc-950 shadow-md'
                    : 'bg-zinc-800 text-zinc-400 hover:text-white'
                }`}
              >
                3. Grow (Badges)
              </button>
            </div>
          </div>

          {/* Tab 1: Learn View */}
          {demoTab === 'learn' && (
            <div className="grid md:grid-cols-2 gap-6 items-center">
              <div className="space-y-4">
                <span className="text-xs font-bold uppercase text-cyan-400 tracking-wider">Concept Lecture</span>
                <h4 className="text-2xl font-bold text-white">Optimal Game Theory & Dynamic Programming</h4>
                <p className="text-zinc-400 text-sm leading-relaxed">
                  Understand minimax turn evaluation, score differentials, and how state transitions shrink the array boundary from O(2^n) brute force to O(n^2) space-optimized dynamic programming.
                </p>
                <div className="flex items-center gap-3 pt-2">
                  <Link 
                    href="/dashboard" 
                    className="px-4 py-2.5 rounded-xl bg-cyan-500 text-zinc-950 font-bold text-xs flex items-center gap-2 hover:brightness-110"
                  >
                    <Play className="w-3.5 h-3.5 fill-current" /> Watch Full Lecture on Dashboard
                  </Link>
                </div>
              </div>
              <div className="aspect-video rounded-2xl bg-black border border-white/10 flex flex-col items-center justify-center p-6 text-center relative overflow-hidden group">
                <div className="w-16 h-16 rounded-full bg-cyan-500/20 border border-cyan-500/40 flex items-center justify-center text-cyan-400 mb-3 group-hover:scale-110 transition-transform">
                  <Play className="w-8 h-8 fill-current ml-1" />
                </div>
                <span className="text-sm font-semibold text-white">Stream POTD from @cipherpage</span>
                <span className="text-xs text-zinc-500 mt-1">Playlist: Leetcode August 2026</span>
              </div>
            </div>
          )}

          {/* Tab 2: Apply View (Monaco + 10 Test Cases) */}
          {demoTab === 'apply' && (
            <div className="grid md:grid-cols-12 gap-6">
              {/* Code Editor preview */}
              <div className="md:col-span-7 bg-zinc-950 rounded-2xl p-4 border border-white/10 font-mono text-xs space-y-3">
                <div className="flex items-center justify-between text-zinc-400 border-b border-white/5 pb-2">
                  <span className="flex items-center gap-2 text-cyan-400">
                    <Code2 className="w-4 h-4" /> solution.py
                  </span>
                  <span>Python 3.11</span>
                </div>
                <pre className="text-zinc-300 leading-relaxed overflow-x-auto text-[13px]">
{`class Solution:
    def predictTheWinner(self, nums: list[int]) -> bool:
        n = len(nums)
        dp = list(nums)
        for diff in range(1, n):
            for i in range(n - diff):
                j = i + diff
                dp[i] = max(nums[i] - dp[i + 1], nums[j] - dp[i])
        return dp[0] >= 0`}
                </pre>
                <div className="pt-2 flex justify-end">
                  <Link 
                    href="/dashboard"
                    className="px-4 py-2 rounded-xl bg-gradient-to-r from-cyan-500 to-cyan-400 text-zinc-950 font-bold text-xs flex items-center gap-1.5 shadow-md hover:brightness-110"
                  >
                    <Sparkles className="w-3.5 h-3.5" /> Open in Monaco IDE
                  </Link>
                </div>
              </div>

              {/* 10 Testcases preview */}
              <div className="md:col-span-5 bg-zinc-950 rounded-2xl p-4 border border-white/10 space-y-3 font-mono text-xs">
                <div className="flex items-center justify-between border-b border-white/5 pb-2">
                  <span className="font-semibold text-white font-sans text-sm">Test Suite</span>
                  <span className="text-[11px] font-bold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
                    10/10 PASSED (100%)
                  </span>
                </div>

                <div className="space-y-1.5 font-sans">
                  <div className="text-[10px] text-zinc-500 uppercase font-semibold">5 Basic Test Cases</div>
                  <div className="grid grid-cols-5 gap-1 font-mono text-xs">
                    {[1, 2, 3, 4, 5].map((i) => (
                      <div key={i} className="p-1 rounded bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-center font-bold">
                        ✓ #{i}
                      </div>
                    ))}
                  </div>

                  <div className="text-[10px] text-zinc-500 uppercase font-semibold pt-1">3 Medium Test Cases</div>
                  <div className="grid grid-cols-3 gap-1 font-mono text-xs">
                    {[6, 7, 8].map((i) => (
                      <div key={i} className="p-1 rounded bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-center font-bold">
                        ✓ #{i}
                      </div>
                    ))}
                  </div>

                  <div className="text-[10px] text-zinc-500 uppercase font-semibold pt-1">2 Hard Test Cases</div>
                  <div className="grid grid-cols-2 gap-1 font-mono text-xs">
                    {[9, 10].map((i) => (
                      <div key={i} className="p-1 rounded bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-center font-bold">
                        ✓ #{i}
                      </div>
                    ))}
                  </div>
                </div>

                <div className="p-2.5 rounded-lg bg-zinc-900 border border-white/5 text-[11px] text-zinc-300 font-sans">
                  <span className="text-emerald-400 font-bold">Execution Speed:</span> 12ms average across all 10 edge tests.
                </div>
              </div>
            </div>
          )}

          {/* Tab 3: Grow View */}
          {demoTab === 'grow' && (
            <div className="grid md:grid-cols-3 gap-6 text-center">
              <div className="p-6 rounded-2xl bg-zinc-950 border border-white/5 space-y-2">
                <div className="w-12 h-12 rounded-xl bg-cyan-500/10 mx-auto flex items-center justify-center text-cyan-400">
                  <Sparkles className="w-6 h-6" />
                </div>
                <h5 className="font-bold text-white text-base">Daily Calendar Streak</h5>
                <p className="text-xs text-zinc-400">Keep up with monthly LeetCode playlists and daily POTDs.</p>
              </div>

              <div className="p-6 rounded-2xl bg-zinc-950 border border-white/5 space-y-2">
                <div className="w-12 h-12 rounded-xl bg-purple-500/10 mx-auto flex items-center justify-center text-purple-400">
                  <Award className="w-6 h-6" />
                </div>
                <h5 className="font-bold text-white text-base">Algorithmic Mastery</h5>
                <p className="text-xs text-zinc-400">Earn verifiable skill credentials in Dynamic Programming, Graphs, and Trees.</p>
              </div>

              <div className="p-6 rounded-2xl bg-zinc-950 border border-white/5 space-y-2">
                <div className="w-12 h-12 rounded-xl bg-emerald-500/10 mx-auto flex items-center justify-center text-emerald-400">
                  <Trophy className="w-6 h-6" />
                </div>
                <h5 className="font-bold text-white text-base">Interview Ready</h5>
                <p className="text-xs text-zinc-400">Build a track record of tested solutions ready for FAANG/top tech interviews.</p>
              </div>
            </div>
          )}
        </div>
      </section>

      {/* CTA Footer Banner */}
      <section className="py-20 border-t border-white/5 bg-zinc-950 text-center relative overflow-hidden">
        <div className="max-w-4xl mx-auto px-6 space-y-6">
          <h3 className="text-3xl md:text-5xl font-black text-white tracking-tight">
            Ready to Learn, Apply, and Grow?
          </h3>
          <p className="text-zinc-400 text-base max-w-xl mx-auto">
            Join thousands of developers mastering algorithms with daily YouTube breakdown lectures and 10-testcase Monaco coding practice.
          </p>
          <div className="pt-2 flex justify-center">
            <Link 
              href="/register" 
              className="px-8 py-4 rounded-full bg-gradient-to-r from-cyan-500 to-cyan-400 text-zinc-950 font-bold hover:brightness-110 shadow-[0_0_30px_-5px_rgba(6,182,212,0.5)] transition-all transform hover:scale-105"
            >
              Get Started Now
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-10 border-t border-white/10 text-center text-zinc-500 text-sm">
        <div className="max-w-7xl mx-auto px-6 flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-3">
             <Image src="/logo.png" alt="CipherPage Logo" width={28} height={28} className="w-7 h-7 object-contain" />
             <span className="font-bold text-zinc-300">CipherPage</span>
             <span className="text-xs text-zinc-500">• LAG — Learn • Apply • Grow</span>
          </div>
          <p>© {new Date().getFullYear()} CipherPage. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}
