'use client';

import { useState, useEffect } from 'react';
import MonacoCodeEditor from '@/components/MonacoCodeEditor';
import { 
  Play, 
  CheckCircle2, 
  XCircle, 
  RotateCcw, 
  Copy, 
  Check, 
  Sparkles, 
  Terminal, 
  Code2, 
  ShieldCheck,
  Cpu,
  Layers,
  Flame,
  Award,
  History,
  Clock,
  Loader2,
  AlertCircle,
  Bot
} from 'lucide-react';
import AIMentorDrawer from '@/components/AIMentorDrawer';
import { createClient } from '@/lib/supabase/client';
import { 
  ProblemInfo, 
  TestCase, 
  getProblemDetails, 
  getKnownBackendChallengeId, 
  resolveBackendChallengeId 
} from '@/lib/problemsData';
import { 
  submitCode, 
  pollSubmissionResult, 
  getSubmissionHistory, 
  EvaluationResult 
} from '@/services/submissionService';

interface PracticeWorkspaceProps {
  problemNumber?: string;
  problemTitle?: string;
  onSolveSuccess?: () => void;
  className?: string;
}

type SupportedLanguage = 'python' | 'javascript' | 'typescript' | 'cpp' | 'java' | 'go';

const LANGUAGES: { id: SupportedLanguage; label: string; version: string }[] = [
  { id: 'python', label: 'Python', version: '3.11' },
  { id: 'javascript', label: 'JavaScript', version: 'ES2023' },
  { id: 'typescript', label: 'TypeScript', version: '5.4' },
  { id: 'cpp', label: 'C++', version: 'GCC 17' },
  { id: 'java', label: 'Java', version: 'OpenJDK 21' },
  { id: 'go', label: 'Go', version: '1.22' },
];

export default function PracticeWorkspace({
  problemNumber = '486',
  problemTitle,
  onSolveSuccess,
  className = '',
}: PracticeWorkspaceProps) {
  const [problem, setProblem] = useState<ProblemInfo>(() => 
    getProblemDetails(problemNumber, problemTitle)
  );

  const [language, setLanguage] = useState<SupportedLanguage>('python');
  const [code, setCode] = useState<string>('');
  const [copied, setCopied] = useState(false);
  const [selectedTestCaseIndex, setSelectedTestCaseIndex] = useState(0);
  const [isRunning, setIsRunning] = useState(false);
  const [submissionStatusText, setSubmissionStatusText] = useState<string>('');
  const [testResults, setTestResults] = useState<TestCase[]>([]);
  const [runSuccess, setRunSuccess] = useState<boolean | null>(null);
  const [rightPanelTab, setRightPanelTab] = useState<'testcases' | 'history'>('testcases');
  const [historyList, setHistoryList] = useState<EvaluationResult[]>([]);
  const [lastExecutionTime, setLastExecutionTime] = useState<string | null>(null);
  const [lastMemoryUsage, setLastMemoryUsage] = useState<string | null>(null);
  const [isMentorOpen, setIsMentorOpen] = useState(false);

  // Dynamic backend challenge ID state with synchronous fallback
  const [challengeId, setChallengeId] = useState<number>(() =>
    getKnownBackendChallengeId(problemNumber, problemTitle)
  );

  const getActiveAuthToken = async (): Promise<string | undefined> => {
    try {
      const supabase = createClient();
      const { data: { session } } = await supabase.auth.getSession();
      if (session?.access_token) return session.access_token;
    } catch (e) {}
    if (typeof window !== 'undefined') {
      const local = localStorage.getItem('cipherpage_auth_token');
      if (local) return local;
    }
    return undefined;
  };

  // Resolve backend challenge ID whenever problem changes
  useEffect(() => {
    let isMounted = true;
    resolveBackendChallengeId(problemNumber, problemTitle).then((id) => {
      if (isMounted) setChallengeId(id);
    });
    return () => {
      isMounted = false;
    };
  }, [problemNumber, problemTitle]);

  // Update problem when problemNumber changes
  useEffect(() => {
    const details = getProblemDetails(problemNumber, problemTitle);
    setProblem(details);
    setCode(details.starterCode[language] || details.starterCode.python);
    setTestResults(details.testCases.map(tc => ({ ...tc })));
    setRunSuccess(null);
    setLastExecutionTime(null);
    setLastMemoryUsage(null);

    // Fetch submission history with active token
    getActiveAuthToken().then((token) => {
      getSubmissionHistory(challengeId, token).then(data => {
        if (data && data.length > 0) setHistoryList(data);
      }).catch(() => {});
    });
  }, [problemNumber, problemTitle, language, challengeId]);

  const handleLanguageChange = (newLang: SupportedLanguage) => {
    setLanguage(newLang);
    setCode(problem.starterCode[newLang] || problem.starterCode.python);
  };

  const handleResetCode = () => {
    setCode(problem.starterCode[language] || problem.starterCode.python);
    setRunSuccess(null);
  };

  const handleCopyCode = () => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // Run/Submit code against isolated backend runner
  const handleRunTests = async (runAll: boolean = true) => {
    setIsRunning(true);
    setRightPanelTab('testcases');
    setSubmissionStatusText('QUEUED...');

    try {
      const token = await getActiveAuthToken();

      // 1. Submit code to FastAPI backend with authenticated session token
      const submission = await submitCode({
        challenge_id: challengeId,
        code: code,
        language: language,
      }, token);

      setSubmissionStatusText('DISPATCHED TO ISOLATED RUNNER...');

      // 2. Poll Celery background worker until complete (API-04, CODE-04)
      const finalResult = await pollSubmissionResult(
        submission.submission_id,
        (status) => {
          setSubmissionStatusText(`${status.status}...`);
        },
        token
      );

      // Record execution metrics (CODE-05)
      const execMs = Math.round(finalResult.execution_time * 1000);
      setLastExecutionTime(`${execMs}ms`);
      setLastMemoryUsage(`${finalResult.memory_usage.toFixed(1)}MB`);

      const totalToRun = runAll ? 10 : 5;
      const allPassed = finalResult.status === 'PASSED';

      // 3. Map backend results or apply evaluation to test cases (zero false positive fallback)
      const evaluated = problem.testCases.map((tc, index) => {
        if (index >= totalToRun) {
          return { ...tc, actualOutput: undefined, isPassed: undefined };
        }

        const backendResult = finalResult.results?.find(r => r.test_case_id === tc.id);
        const passed = backendResult !== undefined ? backendResult.passed : allPassed;
        const actualOut = backendResult?.stdout || (allPassed ? tc.expectedOutput : (finalResult.error_message || 'Wrong Answer / Runtime Error'));

        return {
          ...tc,
          actualOutput: actualOut,
          isPassed: passed,
          executionTime: `${Math.round((backendResult?.execution_time || finalResult.execution_time / 10) * 1000)}ms`,
        };
      });

      setTestResults(evaluated);
      setRunSuccess(allPassed);

      // 4. Update history
      setHistoryList(prev => [finalResult, ...prev.filter(h => h.submission_id !== finalResult.submission_id)]);

      if (allPassed && runAll) {
        try {
          const saved = localStorage.getItem('cipherpage_solved_potds');
          const list: string[] = saved ? JSON.parse(saved) : [];
          if (!list.includes(problem.id)) {
            list.push(problem.id);
            localStorage.setItem('cipherpage_solved_potds', JSON.stringify(list));
          }
        } catch (e) {}

        onSolveSuccess?.();
      }

    } catch (err: unknown) {
      console.warn('Backend submission failed:', err);
      const errorMessage = err instanceof Error ? err.message : 'Evaluation service unavailable. Please check connection and try again.';
      setRunSuccess(false);
      setSubmissionStatusText(`Submission Failed: ${errorMessage}`);

      const evaluated = problem.testCases.map((tc) => ({
        ...tc,
        actualOutput: `Evaluation failed: ${errorMessage}`,
        isPassed: false,
        executionTime: '0ms',
      }));

      setTestResults(evaluated);
    } finally {
      setIsRunning(false);
    }
  };

  const passedCount = testResults.filter((tc) => tc.isPassed === true).length;
  const currentTestCase = testResults[selectedTestCaseIndex] || problem.testCases[0];

  return (
    <div className={`rounded-2xl bg-zinc-900/60 border border-white/10 shadow-2xl overflow-hidden flex flex-col ${className}`}>
      {/* Top Bar: Problem Title & Language Selector */}
      <div className="p-4 border-b border-white/5 bg-zinc-950/70 flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center">
            <Code2 className="w-5 h-5 text-cyan-400" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-mono font-medium text-cyan-400 bg-cyan-950/60 px-2 py-0.5 rounded border border-cyan-500/20">
                #{problem.problemNumber}
              </span>
              <h3 className="font-bold text-white text-base tracking-tight">
                {problem.title}
              </h3>
              <span className={`text-[10px] font-semibold uppercase px-2 py-0.5 rounded-full border ${
                problem.difficulty === 'Easy'
                  ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                  : problem.difficulty === 'Medium'
                  ? 'bg-amber-500/10 text-amber-400 border-amber-500/20'
                  : 'bg-rose-500/10 text-rose-400 border-rose-500/20'
              }`}>
                {problem.difficulty}
              </span>
            </div>
            <p className="text-xs text-zinc-400 mt-0.5">{problem.category}</p>
          </div>
        </div>

        {/* Language Selection & Utility Buttons */}
        <div className="flex items-center gap-2">
          <div className="flex bg-zinc-900 rounded-xl p-1 border border-white/5">
            {LANGUAGES.map((lang) => (
              <button
                key={lang.id}
                onClick={() => handleLanguageChange(lang.id)}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all cursor-pointer ${
                  language === lang.id
                    ? 'bg-cyan-500 text-zinc-950 font-bold shadow-md'
                    : 'text-zinc-400 hover:text-white'
                }`}
              >
                {lang.label}
              </button>
            ))}
          </div>

          <button
            onClick={handleCopyCode}
            className="p-2 rounded-xl bg-zinc-900 hover:bg-zinc-800 text-zinc-400 hover:text-white border border-white/5 transition-colors cursor-pointer"
            title="Copy Code"
          >
            {copied ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
          </button>

          <button
            onClick={handleResetCode}
            className="p-2 rounded-xl bg-zinc-900 hover:bg-zinc-800 text-zinc-400 hover:text-white border border-white/5 transition-colors cursor-pointer"
            title="Reset Starter Code"
          >
            <RotateCcw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Editor & Test Cases Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 min-h-[520px]">
        {/* Left Column: Monaco Code Editor (7 cols) */}
        <div className="lg:col-span-7 border-r border-white/5 flex flex-col p-4 bg-zinc-950/40">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2 text-xs text-zinc-400 font-mono">
              <Terminal className="w-4 h-4 text-cyan-400" />
              <span>solution.{language === 'cpp' ? 'cpp' : language === 'python' ? 'py' : language === 'javascript' ? 'js' : language === 'typescript' ? 'ts' : language === 'java' ? 'java' : 'go'}</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              <span className="text-[11px] text-zinc-400 font-mono">Isolated Runner Ready (Celery/Judge0)</span>
            </div>
          </div>

          <div className="flex-1">
            <MonacoCodeEditor
              value={code}
              onChange={setCode}
              language={language}
              height="400px"
            />
          </div>

          {/* Action Bar */}
          <div className="flex items-center justify-between mt-4 pt-3 border-t border-white/5">
            <div className="flex items-center gap-2 text-xs text-zinc-400">
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              <span>10 Automated Sandbox Test Cases</span>
            </div>

            <div className="flex items-center gap-2.5">
              <button
                onClick={() => setIsMentorOpen(true)}
                className="px-3.5 py-2 rounded-xl bg-purple-500/15 hover:bg-purple-500/25 text-purple-300 hover:text-purple-200 text-xs font-semibold border border-purple-500/30 transition-all flex items-center gap-1.5 cursor-pointer shadow-[0_0_15px_-3px_rgba(168,85,247,0.25)]"
                title="Consult GenAI Coding Mentor (Hint, Debug, Explain, Big-O)"
              >
                <Bot className="w-3.5 h-3.5 text-purple-400" />
                <span>AI Mentor</span>
              </button>

              <button
                disabled={isRunning}
                onClick={() => handleRunTests(false)}
                className="px-4 py-2 rounded-xl bg-zinc-800 hover:bg-zinc-700 text-zinc-200 text-xs font-semibold border border-white/10 transition-colors flex items-center gap-1.5 cursor-pointer disabled:opacity-50"
              >
                <Play className="w-3.5 h-3.5 fill-current" />
                <span>Run (5 Basic)</span>
              </button>

              <button
                disabled={isRunning}
                onClick={() => handleRunTests(true)}
                className="px-5 py-2 rounded-xl bg-gradient-to-r from-cyan-500 to-cyan-400 hover:from-cyan-400 hover:to-cyan-300 text-zinc-950 text-xs font-bold transition-all shadow-[0_0_20px_-3px_rgba(6,182,212,0.4)] flex items-center gap-1.5 cursor-pointer disabled:opacity-50"
              >
                {isRunning ? (
                  <>
                    <Loader2 className="w-3.5 h-3.5 animate-spin" />
                    <span>{submissionStatusText || 'Evaluating...'}</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-3.5 h-3.5" />
                    <span>Submit Solution (All 10)</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>

        {/* Right Column: Test Cases & Submission History (5 cols) */}
        <div className="lg:col-span-5 flex flex-col p-4 bg-zinc-900/40">
          {/* Sub-Tabs: Test Cases vs Submission History */}
          <div className="flex items-center justify-between mb-3 border-b border-white/5 pb-2.5">
            <div className="flex items-center gap-2">
              <button
                onClick={() => setRightPanelTab('testcases')}
                className={`px-3 py-1 rounded-lg text-xs font-semibold transition-colors flex items-center gap-1.5 cursor-pointer ${
                  rightPanelTab === 'testcases'
                    ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20'
                    : 'text-zinc-400 hover:text-white'
                }`}
              >
                <Layers className="w-3.5 h-3.5" />
                <span>Test Suite (10 Cases)</span>
              </button>

              <button
                onClick={() => setRightPanelTab('history')}
                className={`px-3 py-1 rounded-lg text-xs font-semibold transition-colors flex items-center gap-1.5 cursor-pointer ${
                  rightPanelTab === 'history'
                    ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20'
                    : 'text-zinc-400 hover:text-white'
                }`}
              >
                <History className="w-3.5 h-3.5" />
                <span>History ({historyList.length})</span>
              </button>
            </div>

            {runSuccess !== null && rightPanelTab === 'testcases' && (
              <span className={`text-xs font-bold px-2.5 py-0.5 rounded-full flex items-center gap-1 ${
                runSuccess
                  ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                  : 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
              }`}>
                {runSuccess ? <CheckCircle2 className="w-3 h-3" /> : <XCircle className="w-3 h-3" />}
                {passedCount}/10 Passed
              </span>
            )}
          </div>

          {rightPanelTab === 'testcases' ? (
            <>
              {/* Test Category Chips */}
              <div className="space-y-2 mb-4">
                <div className="text-[11px] font-semibold uppercase tracking-wider text-zinc-500 flex items-center justify-between">
                  <span>Select Testcase:</span>
                  <span>5 Basic • 3 Medium • 2 Hard</span>
                </div>

                {/* Test Case Selection Grid */}
                <div className="grid grid-cols-5 gap-1.5">
                  {testResults.map((tc, idx) => {
                    const isSelected = selectedTestCaseIndex === idx;
                    const status = tc.isPassed;

                    return (
                      <button
                        key={tc.id}
                        onClick={() => setSelectedTestCaseIndex(idx)}
                        className={`py-1.5 px-2 rounded-lg text-xs font-medium transition-all text-center flex flex-col items-center justify-center cursor-pointer border ${
                          isSelected
                            ? 'bg-cyan-500 text-zinc-950 font-bold border-cyan-400 shadow-md scale-105'
                            : status === true
                            ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                            : status === false
                            ? 'bg-rose-500/10 text-rose-400 border-rose-500/30'
                            : tc.category === 'basic'
                            ? 'bg-zinc-800/80 text-zinc-300 border-white/5 hover:border-cyan-500/30'
                            : tc.category === 'medium'
                            ? 'bg-amber-950/20 text-amber-300 border-amber-500/20 hover:border-amber-500/40'
                            : 'bg-purple-950/20 text-purple-300 border-purple-500/20 hover:border-purple-500/40'
                        }`}
                      >
                        <span className="text-[10px] uppercase opacity-75 font-mono">
                          {tc.category === 'basic' ? 'Bas' : tc.category === 'medium' ? 'Med' : 'Hrd'}
                        </span>
                        <span className="text-xs font-bold">#{tc.id}</span>
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Active Test Case Detail Viewer */}
              <div className="flex-1 bg-zinc-950/80 rounded-xl p-4 border border-white/5 flex flex-col space-y-3 font-mono text-xs">
                <div className="flex items-center justify-between border-b border-white/5 pb-2">
                  <div className="flex items-center gap-2">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider ${
                      currentTestCase.category === 'basic'
                        ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20'
                        : currentTestCase.category === 'medium'
                        ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                        : 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                    }`}>
                      {currentTestCase.category} Case #{currentTestCase.id}
                    </span>
                    {currentTestCase.executionTime && (
                      <span className="text-[11px] text-zinc-400 flex items-center gap-1 font-sans">
                        <Cpu className="w-3 h-3 text-cyan-400" />
                        {currentTestCase.executionTime}
                      </span>
                    )}
                  </div>

                  {currentTestCase.isPassed !== undefined && (
                    <span className={`text-[11px] font-bold flex items-center gap-1 ${
                      currentTestCase.isPassed ? 'text-emerald-400' : 'text-rose-400'
                    }`}>
                      {currentTestCase.isPassed ? <CheckCircle2 className="w-3.5 h-3.5" /> : <XCircle className="w-3.5 h-3.5" />}
                      {currentTestCase.isPassed ? 'Passed' : 'Failed'}
                    </span>
                  )}
                </div>

                {/* Input */}
                <div>
                  <span className="text-[11px] font-sans font-semibold text-zinc-400 uppercase">Input:</span>
                  <div className="mt-1 p-2.5 rounded-lg bg-zinc-900 border border-white/5 text-zinc-200 overflow-x-auto">
                    {currentTestCase.input}
                  </div>
                </div>

                {/* Expected Output */}
                <div>
                  <span className="text-[11px] font-sans font-semibold text-zinc-400 uppercase">Expected Output:</span>
                  <div className="mt-1 p-2.5 rounded-lg bg-zinc-900 border border-white/5 text-emerald-400 font-bold overflow-x-auto">
                    {currentTestCase.expectedOutput}
                  </div>
                </div>

                {/* Actual Output (if evaluated) */}
                {currentTestCase.actualOutput && (
                  <div>
                    <span className="text-[11px] font-sans font-semibold text-zinc-400 uppercase">Actual Output:</span>
                    <div className={`mt-1 p-2.5 rounded-lg border overflow-x-auto font-bold ${
                      currentTestCase.isPassed
                        ? 'bg-emerald-950/20 text-emerald-400 border-emerald-500/20'
                        : 'bg-rose-950/20 text-rose-400 border-rose-500/20'
                    }`}>
                      {currentTestCase.actualOutput}
                    </div>
                  </div>
                )}

                {currentTestCase.explanation && (
                  <div className="pt-2 text-[11px] text-zinc-400 font-sans border-t border-white/5">
                    <span className="font-semibold text-zinc-300">Explanation: </span>
                    {currentTestCase.explanation}
                  </div>
                )}
              </div>

              {/* Execution Metrics Summary */}
              {lastExecutionTime && (
                <div className="mt-2.5 p-2 rounded-lg bg-zinc-950/50 border border-white/5 flex items-center justify-between text-[11px] text-zinc-400">
                  <span className="flex items-center gap-1.5 font-mono">
                    <Clock className="w-3 h-3 text-cyan-400" /> Total Time: {lastExecutionTime}
                  </span>
                  <span className="flex items-center gap-1.5 font-mono">
                    <Cpu className="w-3 h-3 text-purple-400" /> Peak Memory: {lastMemoryUsage}
                  </span>
                </div>
              )}

              {/* Success Celebration Banner */}
              {runSuccess === true && (
                <div className="mt-3 p-3 rounded-xl bg-gradient-to-r from-emerald-500/20 to-cyan-500/20 border border-emerald-500/30 flex items-center gap-3 animate-in fade-in duration-300">
                  <div className="w-8 h-8 rounded-lg bg-emerald-500/20 flex items-center justify-center text-emerald-400">
                    <Award className="w-5 h-5" />
                  </div>
                  <div className="flex-1">
                    <p className="text-xs font-bold text-white">All 10 Test Cases Passed!</p>
                    <p className="text-[11px] text-emerald-300">Applied knowledge verified • Solution saved to your streak.</p>
                  </div>
                </div>
              )}
            </>
          ) : (
            /* Submission History Tab (CODE-05) */
            <div className="flex-1 flex flex-col space-y-2 overflow-y-auto max-h-[460px] pr-1">
              <div className="text-[11px] font-semibold uppercase tracking-wider text-zinc-500 mb-1">
                Past Submissions ({historyList.length})
              </div>

              {historyList.length === 0 ? (
                <div className="flex-1 flex flex-col items-center justify-center p-8 text-center text-zinc-500">
                  <History className="w-8 h-8 mb-2 opacity-40 text-cyan-400" />
                  <p className="text-xs">No submissions recorded yet.</p>
                  <p className="text-[11px] text-zinc-600 mt-0.5">Submit your solution to inspect isolated execution logs.</p>
                </div>
              ) : (
                historyList.map((hist) => (
                  <div
                    key={hist.submission_id}
                    className="p-3 rounded-xl bg-zinc-950/70 border border-white/5 flex items-center justify-between text-xs hover:border-white/10 transition-colors"
                  >
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                          hist.status === 'PASSED'
                            ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                            : 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                        }`}>
                          {hist.status}
                        </span>
                        <span className="font-mono text-zinc-300 font-semibold">
                          Score: {hist.score.toFixed(0)}%
                        </span>
                      </div>
                      <p className="text-[10px] text-zinc-500 font-mono">
                        ID: {hist.submission_id} • {new Date(hist.created_at).toLocaleTimeString()}
                      </p>
                    </div>

                    <div className="text-right font-mono text-[11px] text-zinc-400 space-y-0.5">
                      <p className="text-cyan-400 font-semibold">{hist.tests_passed}/{hist.total_tests} Tests</p>
                      <p className="text-zinc-500 text-[10px]">{(hist.execution_time * 1000).toFixed(0)}ms</p>
                    </div>
                  </div>
                ))
              )}
            </div>
          )}
        </div>
      </div>

      {/* GenAI Coding Mentor Drawer (AI-01..AI-07) */}
      <AIMentorDrawer
        isOpen={isMentorOpen}
        onClose={() => setIsMentorOpen(false)}
        challengeId={challengeId}
        code={code}
        language={language}
        lastErrorOutput={testResults.find(t => t.isPassed === false)?.actualOutput || ''}
      />
    </div>
  );
}
