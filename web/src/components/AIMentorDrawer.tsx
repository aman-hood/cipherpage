'use client';

import { useState, useEffect } from 'react';
import { 
  Sparkles, 
  X, 
  Lightbulb, 
  Bug, 
  BookOpen, 
  Zap, 
  Copy, 
  Check, 
  Loader2, 
  AlertTriangle,
  Bot,
  ChevronRight,
  ShieldCheck
} from 'lucide-react';
import { 
  AIMentorMode, 
  fetchAIMentorGuidance, 
  fetchAIQuota, 
  AIMentorResponseData 
} from '@/services/aiMentorService';

interface AIMentorDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  challengeId?: number;
  code: string;
  language: string;
  lastErrorOutput?: string;
}

export default function AIMentorDrawer({
  isOpen,
  onClose,
  challengeId = 1,
  code,
  language,
  lastErrorOutput = '',
}: AIMentorDrawerProps) {
  const [activeMode, setActiveMode] = useState<AIMentorMode>('HINT');
  const [requestFullSolution, setRequestFullSolution] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [copied, setCopied] = useState(false);
  const [response, setResponse] = useState<AIMentorResponseData | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [remainingQuota, setRemainingQuota] = useState<number>(50);

  useEffect(() => {
    if (isOpen) {
      fetchAIQuota().then((q) => setRemainingQuota(q.remaining_quota)).catch(() => {});
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const handleAskMentor = async () => {
    setIsLoading(true);
    setErrorMsg(null);
    setResponse(null);

    try {
      const res = await fetchAIMentorGuidance({
        challenge_id: challengeId,
        mode: activeMode,
        code,
        language,
        error_output: lastErrorOutput || undefined,
        request_full_solution: activeMode === 'HINT' ? requestFullSolution : false,
      });
      setResponse(res);
      setRemainingQuota(res.remaining_quota);
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to contact AI Mentor.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCopy = () => {
    if (response?.content) {
      navigator.clipboard.writeText(response.content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex justify-end animate-in fade-in duration-200">
      <div 
        className="w-full max-w-xl bg-zinc-950 border-l border-white/10 h-full flex flex-col shadow-2xl overflow-hidden animate-in slide-in-from-right duration-300"
      >
        {/* Top Header */}
        <div className="p-4 border-b border-white/10 bg-zinc-900/60 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500/20 to-purple-500/20 border border-cyan-500/30 flex items-center justify-center">
              <Bot className="w-5 h-5 text-cyan-400" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="font-bold text-white text-base tracking-tight">GenAI Coding Mentor</h3>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/30">
                  LAG • AI-01
                </span>
              </div>
              <p className="text-xs text-zinc-400 mt-0.5">
                Targeted pedagogical guidance • {remainingQuota}/50 daily requests left
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-2 rounded-xl bg-zinc-900 hover:bg-zinc-800 text-zinc-400 hover:text-white border border-white/5 transition-colors cursor-pointer"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Mode Selector Tabs (AI-01) */}
        <div className="p-4 border-b border-white/5 bg-zinc-900/30 grid grid-cols-4 gap-1.5">
          <button
            onClick={() => { setActiveMode('HINT'); setResponse(null); }}
            className={`py-2 px-2.5 rounded-xl text-xs font-semibold flex flex-col items-center gap-1 transition-all cursor-pointer border ${
              activeMode === 'HINT'
                ? 'bg-cyan-500 text-zinc-950 border-cyan-400 shadow-md font-bold'
                : 'bg-zinc-900/70 text-zinc-400 border-white/5 hover:text-white'
            }`}
          >
            <Lightbulb className="w-4 h-4" />
            <span>Hint</span>
          </button>

          <button
            onClick={() => { setActiveMode('DEBUG'); setResponse(null); }}
            className={`py-2 px-2.5 rounded-xl text-xs font-semibold flex flex-col items-center gap-1 transition-all cursor-pointer border ${
              activeMode === 'DEBUG'
                ? 'bg-rose-500 text-white border-rose-400 shadow-md font-bold'
                : 'bg-zinc-900/70 text-zinc-400 border-white/5 hover:text-white'
            }`}
          >
            <Bug className="w-4 h-4" />
            <span>Debug</span>
          </button>

          <button
            onClick={() => { setActiveMode('EXPLAIN'); setResponse(null); }}
            className={`py-2 px-2.5 rounded-xl text-xs font-semibold flex flex-col items-center gap-1 transition-all cursor-pointer border ${
              activeMode === 'EXPLAIN'
                ? 'bg-purple-500 text-white border-purple-400 shadow-md font-bold'
                : 'bg-zinc-900/70 text-zinc-400 border-white/5 hover:text-white'
            }`}
          >
            <BookOpen className="w-4 h-4" />
            <span>Explain</span>
          </button>

          <button
            onClick={() => { setActiveMode('COMPLEXITY'); setResponse(null); }}
            className={`py-2 px-2.5 rounded-xl text-xs font-semibold flex flex-col items-center gap-1 transition-all cursor-pointer border ${
              activeMode === 'COMPLEXITY'
                ? 'bg-amber-500 text-zinc-950 border-amber-400 shadow-md font-bold'
                : 'bg-zinc-900/70 text-zinc-400 border-white/5 hover:text-white'
            }`}
          >
            <Zap className="w-4 h-4" />
            <span>Big-O</span>
          </button>
        </div>

        {/* Mode Details & Options */}
        <div className="p-4 border-b border-white/5 bg-zinc-950/60 flex items-center justify-between gap-4">
          <div className="text-xs text-zinc-400 flex items-center gap-2">
            {activeMode === 'HINT' && <span>Socratic hints without spoiling solution (AI-02)</span>}
            {activeMode === 'DEBUG' && <span>Analyze bugs, logic errors & test failures (AI-03)</span>}
            {activeMode === 'EXPLAIN' && <span>Stepwise logic & intuition breakdown (AI-04)</span>}
            {activeMode === 'COMPLEXITY' && <span>Time & Space Complexity analysis (AI-04)</span>}
          </div>

          {activeMode === 'HINT' && (
            <label className="flex items-center gap-2 text-xs text-zinc-300 font-medium cursor-pointer">
              <input
                type="checkbox"
                checked={requestFullSolution}
                onChange={(e) => setRequestFullSolution(e.target.checked)}
                className="rounded border-zinc-700 text-cyan-500 focus:ring-cyan-500 cursor-pointer"
              />
              <span>Reveal Full Code</span>
            </label>
          )}

          <button
            disabled={isLoading}
            onClick={handleAskMentor}
            className="px-4 py-2 rounded-xl bg-gradient-to-r from-cyan-500 to-cyan-400 hover:from-cyan-400 hover:to-cyan-300 text-zinc-950 text-xs font-bold transition-all shadow-[0_0_15px_-3px_rgba(6,182,212,0.4)] flex items-center gap-1.5 cursor-pointer disabled:opacity-50"
          >
            {isLoading ? (
              <>
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
                <span>Thinking...</span>
              </>
            ) : (
              <>
                <Sparkles className="w-3.5 h-3.5" />
                <span>Consult Mentor</span>
              </>
            )}
          </button>
        </div>

        {/* Content Area */}
        <div className="flex-1 p-5 overflow-y-auto space-y-4">
          {errorMsg && (
            <div className="p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-300 text-xs flex items-center gap-2.5">
              <AlertTriangle className="w-4 h-4 flex-shrink-0" />
              <span>{errorMsg}</span>
            </div>
          )}

          {!response && !isLoading && !errorMsg && (
            <div className="h-full flex flex-col items-center justify-center p-8 text-center text-zinc-500 space-y-3">
              <div className="w-14 h-14 rounded-2xl bg-zinc-900 border border-white/5 flex items-center justify-center text-cyan-400">
                <Sparkles className="w-7 h-7 opacity-50" />
              </div>
              <div>
                <p className="text-sm font-semibold text-zinc-300">Ready to Assist</p>
                <p className="text-xs text-zinc-500 mt-1 max-w-sm">
                  Click &apos;Consult Mentor&apos; to receive progressive Socratic guidance, bug diagnosis, or complexity breakdown tailored to your current code.
                </p>
              </div>
            </div>
          )}

          {isLoading && (
            <div className="h-full flex flex-col items-center justify-center p-8 text-center text-zinc-400 space-y-3">
              <Loader2 className="w-8 h-8 text-cyan-400 animate-spin" />
              <p className="text-xs font-mono">Analyzing AST & applying pedagogical rules...</p>
            </div>
          )}

          {response && (
            <div className="space-y-4 animate-in fade-in duration-300">
              {/* Guidance Box */}
              <div className="p-4 rounded-2xl bg-zinc-900/80 border border-white/10 space-y-3">
                <div className="flex items-center justify-between border-b border-white/5 pb-2">
                  <span className="text-xs font-bold text-cyan-400 uppercase tracking-wider font-mono">
                    {response.mode} Guidance
                  </span>
                  <button
                    onClick={handleCopy}
                    className="flex items-center gap-1.5 text-xs text-zinc-400 hover:text-white transition-colors cursor-pointer"
                  >
                    {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                    <span>{copied ? 'Copied' : 'Copy'}</span>
                  </button>
                </div>

                <div className="text-xs text-zinc-200 leading-relaxed font-sans whitespace-pre-wrap">
                  {response.content}
                </div>
              </div>

              {/* Responsible AI Disclaimer (AI-06) */}
              <div className="p-3 rounded-xl bg-zinc-900/50 border border-white/5 flex items-start gap-2.5 text-[11px] text-zinc-400">
                <ShieldCheck className="w-4 h-4 text-cyan-400 flex-shrink-0 mt-0.5" />
                <p>
                  <strong className="text-zinc-300 font-semibold">Responsible AI: </strong>
                  {response.disclaimer}
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
