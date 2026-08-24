import React, { useState } from 'react';
import { PlayCircle, Download, Send, Award, BookOpen, Terminal, Rocket, CheckCircle2 } from 'lucide-react';
import { apiClient } from '../../core/api';

interface SubmissionResponse {
  score: number;
  passed_tests: number;
  total_tests: number;
  status: string;
}

export const LearningPortal: React.FC = () => {
  const [code, setCode] = useState<string>('def solve():\n    # Write your solution here\n    pass');
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [submissionResult, setSubmissionResult] = useState<SubmissionResponse | null>(null);

  const handleCodeSubmit = async () => {
    setIsSubmitting(true);
    try {
      // Send payload data to FastAPI backend to evaluate on Celery worker
      const response = await apiClient.post<SubmissionResponse>('/api/v1/challenges/1/submit', {
        submitted_code: code
      });
      setSubmissionResult(response.data);
    } catch (error) {
      console.error('Submission failed', error);
      alert('Failed to submit code. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="flex h-screen w-full bg-brand-dark text-slate-200 overflow-hidden font-sans">
      
      {/* =======================
          LEFT PANE: LEARN
          ======================= */}
      <section className="w-1/3 flex flex-col border-r border-slate-700 bg-slate-800/50">
        <div className="p-4 border-b border-slate-700 bg-slate-800 flex items-center gap-2">
          <BookOpen className="text-brand-primary" size={24} />
          <h2 className="text-lg font-bold tracking-wide">LEARN</h2>
        </div>
        
        <div className="flex-1 p-4 overflow-y-auto">
          <h3 className="text-xl font-semibold mb-4">Module 1: Advanced Data Structures</h3>
          
          {/* Mock Video Player */}
          <div className="relative w-full aspect-video bg-black rounded-lg overflow-hidden flex items-center justify-center group mb-6 shadow-lg border border-slate-600">
            <video 
              controls 
              className="w-full h-full object-cover"
              poster="https://images.unsplash.com/photo-1555066931-4365d14bab8c?auto=format&fit=crop&w=800&q=80"
            >
              <source src="https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8" type="application/x-mpegURL" />
              Your browser does not support the video tag.
            </video>
            <div className="absolute inset-0 bg-black/40 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none">
              <PlayCircle className="text-white w-16 h-16 opacity-80" />
            </div>
          </div>

          <div className="space-y-4">
            <h4 className="font-semibold text-slate-300">Resources</h4>
            <button className="w-full flex items-center justify-between p-3 bg-slate-700 hover:bg-slate-600 rounded-lg transition-colors border border-slate-600">
              <span className="flex items-center gap-2">
                <Download size={18} className="text-slate-400" />
                Lecture Slides (PDF)
              </span>
            </button>
            <button className="w-full flex items-center justify-between p-3 bg-slate-700 hover:bg-slate-600 rounded-lg transition-colors border border-slate-600">
              <span className="flex items-center gap-2">
                <Download size={18} className="text-slate-400" />
                Starter Code Repository
              </span>
            </button>
          </div>
        </div>
      </section>


      {/* =======================
          MIDDLE PANE: APPLY
          ======================= */}
      <section className="w-1/3 flex flex-col border-r border-slate-700 bg-slate-900">
        <div className="p-4 border-b border-slate-700 bg-slate-800 flex items-center gap-2">
          <Terminal className="text-brand-warning" size={24} />
          <h2 className="text-lg font-bold tracking-wide">APPLY</h2>
        </div>
        
        <div className="flex-1 flex flex-col p-4">
          <div className="mb-4">
            <h3 className="font-semibold text-lg mb-2">Challenge: Reverse a Linked List</h3>
            <p className="text-sm text-slate-400 mb-2">Write a function to reverse a singly linked list in-place and return the new head.</p>
          </div>
          
          <div className="flex-1 rounded-lg overflow-hidden border border-slate-700 flex flex-col bg-slate-950">
            <div className="bg-slate-800 px-4 py-2 text-xs font-mono text-slate-400 flex justify-between">
              <span>main.py</span>
              <span>Python 3.11</span>
            </div>
            <textarea 
              value={code}
              onChange={(e) => setCode(e.target.value)}
              className="flex-1 w-full bg-transparent p-4 font-mono text-sm text-slate-300 focus:outline-none resize-none leading-relaxed"
              spellCheck={false}
            />
          </div>

          <div className="mt-4 flex justify-between items-center">
            {submissionResult ? (
              <div className="flex items-center gap-2 text-brand-accent text-sm font-medium">
                <CheckCircle2 size={18} />
                Score: {submissionResult.score}% ({submissionResult.passed_tests}/{submissionResult.total_tests} tests)
              </div>
            ) : (
              <div className="text-sm text-slate-500">Awaiting submission...</div>
            )}
            
            <button 
              onClick={handleCodeSubmit}
              disabled={isSubmitting}
              className="flex items-center gap-2 bg-brand-warning hover:bg-amber-600 text-white px-6 py-2 rounded-lg font-medium transition-colors disabled:opacity-50"
            >
              {isSubmitting ? 'Evaluating...' : 'Submit Code'}
              <Send size={16} />
            </button>
          </div>
        </div>
      </section>


      {/* =======================
          RIGHT PANE: GROW
          ======================= */}
      <section className="w-1/3 flex flex-col bg-slate-800/30">
        <div className="p-4 border-b border-slate-700 bg-slate-800 flex items-center gap-2">
          <Rocket className="text-brand-accent" size={24} />
          <h2 className="text-lg font-bold tracking-wide">GROW</h2>
        </div>
        
        <div className="flex-1 p-4 overflow-y-auto space-y-6">
          <div className="bg-slate-800/80 p-5 rounded-xl border border-brand-accent/30 shadow-[0_0_15px_rgba(16,185,129,0.1)]">
            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <Award className="text-brand-accent" />
              Milestone Tracking
            </h3>
            
            <div className="space-y-4">
              <div className="relative">
                <div className="flex items-center justify-between mb-1 text-sm">
                  <span className="font-medium text-slate-300">Course Progress</span>
                  <span className="text-brand-accent font-bold">65%</span>
                </div>
                <div className="w-full bg-slate-700 rounded-full h-2.5">
                  <div className="bg-brand-accent h-2.5 rounded-full" style={{ width: '65%' }}></div>
                </div>
              </div>
              
              <div className="relative">
                <div className="flex items-center justify-between mb-1 text-sm">
                  <span className="font-medium text-slate-300">Apply Score Average</span>
                  <span className="text-brand-warning font-bold">92%</span>
                </div>
                <div className="w-full bg-slate-700 rounded-full h-2.5">
                  <div className="bg-brand-warning h-2.5 rounded-full" style={{ width: '92%' }}></div>
                </div>
              </div>
            </div>
          </div>

          <div>
            <h3 className="font-semibold text-slate-300 mb-3">Unlocked Portfolios</h3>
            <div className="grid gap-3">
              <div className="p-4 rounded-lg bg-slate-800 border border-slate-600 hover:border-brand-primary transition-colors cursor-pointer group">
                <h4 className="font-medium text-white group-hover:text-brand-primary transition-colors">Build a Redis Clone</h4>
                <p className="text-sm text-slate-400 mt-1">Unlocked at 80% Apply Score</p>
              </div>
              <div className="p-4 rounded-lg bg-slate-800 border border-slate-600 opacity-50 cursor-not-allowed">
                <h4 className="font-medium text-white flex justify-between">
                  Distributed Rate Limiter
                  <span className="text-xs bg-slate-700 px-2 py-1 rounded">Locked</span>
                </h4>
                <p className="text-sm text-slate-400 mt-1">Requires 95% Apply Score</p>
              </div>
            </div>
          </div>
          
          <div>
            <h3 className="font-semibold text-slate-300 mb-3">Badges & Certificates</h3>
            <div className="flex flex-wrap gap-3">
              <span className="px-3 py-1.5 bg-blue-500/20 text-blue-400 border border-blue-500/30 rounded-full text-xs font-medium flex items-center gap-1">
                <CheckCircle2 size={14} /> Data Structures Pro
              </span>
              <span className="px-3 py-1.5 bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 rounded-full text-xs font-medium flex items-center gap-1">
                <CheckCircle2 size={14} /> Python Master
              </span>
            </div>
          </div>
        </div>
      </section>

    </div>
  );
};
