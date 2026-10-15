'use client';

import { useState, useEffect } from 'react';
import { 
  Sparkles, 
  X, 
  BookOpen, 
  FileText, 
  Search, 
  Loader2, 
  AlertTriangle, 
  Check, 
  Copy, 
  ExternalLink,
  ChevronRight,
  HelpCircle,
  Database,
  ShieldCheck,
  Quote
} from 'lucide-react';
import { 
  askLearningAssistant, 
  fetchCourseDocuments, 
  RAGQueryResponse, 
  DocumentSummary 
} from '@/services/ragService';

interface CourseRAGAssistantProps {
  isOpen: boolean;
  onClose: () => void;
  courseId?: number;
  courseTitle?: string;
}

const SAMPLE_QUESTIONS = [
  "What is FastAPI dependency injection and how does it work?",
  "How does Pydantic v2 validation improve API performance?",
  "Explain PostgreSQL connection pooling best practices.",
  "How is pgvector used for semantic similarity retrieval?"
];

export default function CourseRAGAssistant({
  isOpen,
  onClose,
  courseId,
  courseTitle = 'Course Materials',
}: CourseRAGAssistantProps) {
  const [question, setQuestion] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [copied, setCopied] = useState(false);
  const [result, setResult] = useState<RAGQueryResponse | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [documents, setDocuments] = useState<DocumentSummary[]>([]);
  const [showDocsList, setShowDocsList] = useState(false);
  const [scopeToCourse, setScopeToCourse] = useState(true);

  useEffect(() => {
    if (isOpen) {
      fetchCourseDocuments(scopeToCourse ? courseId : undefined)
        .then(setDocuments)
        .catch(() => {});
    }
  }, [isOpen, scopeToCourse, courseId]);

  if (!isOpen) return null;

  const handleAsk = async (queryToAsk?: string) => {
    const q = (queryToAsk || question).trim();
    if (!q) return;

    setIsLoading(true);
    setErrorMsg(null);
    setResult(null);

    try {
      const res = await askLearningAssistant({
        question: q,
        course_id: scopeToCourse ? courseId : undefined,
      });
      setResult(res);
      setQuestion(q);
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to query RAG Assistant.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCopy = () => {
    if (result?.answer) {
      navigator.clipboard.writeText(result.answer);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex justify-end animate-in fade-in duration-200">
      <div className="w-full max-w-2xl bg-zinc-950 border-l border-white/10 h-full flex flex-col shadow-2xl overflow-hidden animate-in slide-in-from-right duration-300">
        {/* Top Header */}
        <div className="p-4 border-b border-white/10 bg-zinc-900/60 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500/20 to-cyan-500/20 border border-cyan-500/30 flex items-center justify-center">
              <BookOpen className="w-5 h-5 text-cyan-400" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="font-bold text-white text-base tracking-tight">RAG Learning Assistant</h3>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/30">
                  pgvector • RAG-04
                </span>
              </div>
              <p className="text-xs text-zinc-400 mt-0.5">
                Grounded Q&amp;A citing course notes, guides &amp; transcripts
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowDocsList(!showDocsList)}
              className="px-2.5 py-1.5 rounded-lg bg-zinc-900 hover:bg-zinc-800 text-zinc-300 text-xs border border-white/10 transition-colors flex items-center gap-1.5 cursor-pointer"
              title="View Ingested Knowledge Sources"
            >
              <Database className="w-3.5 h-3.5 text-cyan-400" />
              <span>{documents.length} Docs</span>
            </button>
            <button
              onClick={onClose}
              className="p-2 rounded-xl bg-zinc-900 hover:bg-zinc-800 text-zinc-400 hover:text-white border border-white/5 transition-colors cursor-pointer"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Ingested Documents Drawer / Dropdown */}
        {showDocsList && (
          <div className="p-4 bg-zinc-900/90 border-b border-cyan-500/20 text-xs animate-in slide-in-from-top-2 duration-200">
            <div className="flex items-center justify-between mb-2">
              <span className="font-semibold text-zinc-200 flex items-center gap-1.5">
                <Database className="w-3.5 h-3.5 text-cyan-400" />
                Ingested Course Knowledge Base
              </span>
              <span className="text-[11px] text-zinc-500">
                Vector Index: pgvector cosine distance
              </span>
            </div>
            {documents.length === 0 ? (
              <p className="text-zinc-500 py-2">No documents currently ingested for this scope.</p>
            ) : (
              <div className="space-y-1.5 max-h-40 overflow-y-auto">
                {documents.map((doc) => (
                  <div key={doc.id} className="p-2 rounded-lg bg-zinc-950/60 border border-white/5 flex items-center justify-between">
                    <div className="flex items-center gap-2 truncate">
                      <FileText className="w-3.5 h-3.5 text-cyan-400 flex-shrink-0" />
                      <span className="text-zinc-200 truncate font-medium">{doc.title}</span>
                    </div>
                    <div className="flex items-center gap-2 text-[10px] text-zinc-400 flex-shrink-0">
                      <span className="px-1.5 py-0.5 rounded bg-zinc-800">{doc.chunks_count} chunks</span>
                      <span className="text-emerald-400 uppercase font-mono">{doc.status}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Search Query Input */}
        <div className="p-4 border-b border-white/5 bg-zinc-900/30 space-y-3">
          <form 
            onSubmit={(e) => { e.preventDefault(); handleAsk(); }}
            className="flex items-center gap-2"
          >
            <div className="relative flex-1">
              <Search className="w-4 h-4 text-zinc-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                placeholder="Ask anything about the lecture or course materials..."
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-zinc-950 border border-white/10 text-white placeholder-zinc-500 text-sm focus:outline-hidden focus:border-cyan-500 transition-colors"
              />
            </div>
            <button
              type="submit"
              disabled={isLoading || !question.trim()}
              className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-indigo-500 hover:from-cyan-400 hover:to-indigo-400 text-zinc-950 text-sm font-bold transition-all shadow-[0_0_15px_-3px_rgba(6,182,212,0.4)] flex items-center gap-2 cursor-pointer disabled:opacity-50 flex-shrink-0"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Searching...</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4" />
                  <span>Ask RAG</span>
                </>
              )}
            </button>
          </form>

          {/* Scope & Quick Suggestions */}
          <div className="flex flex-wrap items-center justify-between gap-2 pt-1 text-xs">
            <div className="flex items-center gap-2">
              <label className="flex items-center gap-1.5 text-zinc-400 cursor-pointer hover:text-zinc-200 transition-colors">
                <input
                  type="checkbox"
                  checked={scopeToCourse}
                  onChange={(e) => setScopeToCourse(e.target.checked)}
                  className="rounded border-zinc-700 text-cyan-500 focus:ring-cyan-500 cursor-pointer"
                />
                <span>Scope to current course only ({courseTitle})</span>
              </label>
            </div>
            <span className="text-[11px] text-zinc-500">
              Zero-hallucination grounded retrieval
            </span>
          </div>

          {/* Quick Questions Pills */}
          {!result && !isLoading && (
            <div className="space-y-1.5 pt-2">
              <span className="text-[11px] font-semibold text-zinc-400 uppercase tracking-wider">
                Suggested Questions
              </span>
              <div className="flex flex-wrap gap-1.5">
                {SAMPLE_QUESTIONS.map((q, idx) => (
                  <button
                    key={idx}
                    type="button"
                    onClick={() => handleAsk(q)}
                    className="text-left text-xs px-2.5 py-1.5 rounded-lg bg-zinc-900/80 hover:bg-zinc-800 text-zinc-300 hover:text-cyan-300 border border-white/5 transition-colors cursor-pointer"
                  >
                    {q}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Content Area */}
        <div className="flex-1 p-5 overflow-y-auto space-y-5">
          {errorMsg && (
            <div className="p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-300 text-xs flex items-center gap-2.5">
              <AlertTriangle className="w-4 h-4 flex-shrink-0" />
              <span>{errorMsg}</span>
            </div>
          )}

          {!result && !isLoading && !errorMsg && (
            <div className="h-full flex flex-col items-center justify-center p-8 text-center text-zinc-500 space-y-3">
              <div className="w-14 h-14 rounded-2xl bg-zinc-900 border border-white/5 flex items-center justify-center text-cyan-400">
                <BookOpen className="w-7 h-7 opacity-50" />
              </div>
              <div>
                <p className="text-sm font-semibold text-zinc-300">Ask Any Question From Course Notes</p>
                <p className="text-xs text-zinc-500 mt-1 max-w-md">
                  Queries are matched using pgvector 384-dimensional dense embeddings against syllabus notes and lecture documentation. Every claim includes exact source citations.
                </p>
              </div>
            </div>
          )}

          {isLoading && (
            <div className="h-full flex flex-col items-center justify-center p-8 text-center text-zinc-400 space-y-3">
              <Loader2 className="w-8 h-8 text-cyan-400 animate-spin" />
              <p className="text-xs font-mono">Retrieving relevant chunks from pgvector &amp; synthesizing grounded answer...</p>
            </div>
          )}

          {result && (
            <div className="space-y-5 animate-in fade-in duration-300">
              {/* Answer Box */}
              <div className="p-5 rounded-2xl bg-zinc-900/80 border border-white/10 space-y-3 shadow-xl">
                <div className="flex items-center justify-between border-b border-white/5 pb-2.5">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-bold text-cyan-400 uppercase tracking-wider font-mono flex items-center gap-1.5">
                      <Sparkles className="w-3.5 h-3.5" />
                      Grounded Answer
                    </span>
                    <span className={`text-[10px] font-mono px-2 py-0.5 rounded-full border ${
                      result.sources_found 
                        ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30' 
                        : 'bg-amber-500/10 text-amber-400 border-amber-500/30'
                    }`}>
                      Confidence: {Math.round(result.confidence * 100)}%
                    </span>
                  </div>
                  <button
                    onClick={handleCopy}
                    className="flex items-center gap-1.5 text-xs text-zinc-400 hover:text-white transition-colors cursor-pointer"
                  >
                    {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                    <span>{copied ? 'Copied' : 'Copy'}</span>
                  </button>
                </div>

                <div className="text-sm text-zinc-200 leading-relaxed font-sans whitespace-pre-wrap">
                  {result.answer}
                </div>
              </div>

              {/* Citations Section (RAG-04) */}
              {result.citations && result.citations.length > 0 && (
                <div className="space-y-2.5">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-zinc-300 uppercase tracking-wider flex items-center gap-1.5">
                      <Quote className="w-3.5 h-3.5 text-indigo-400" />
                      Evidence &amp; Citations ({result.citations.length})
                    </span>
                    <span className="text-[11px] text-zinc-500">
                      RAG-04 Verification
                    </span>
                  </div>

                  <div className="space-y-2">
                    {result.citations.map((cite, idx) => (
                      <div
                        key={idx}
                        className="p-3.5 rounded-xl bg-zinc-900/60 border border-white/5 space-y-2 hover:border-cyan-500/30 transition-all"
                      >
                        <div className="flex items-center justify-between text-xs">
                          <span className="font-semibold text-cyan-300 flex items-center gap-1.5">
                            <FileText className="w-3.5 h-3.5 text-cyan-400" />
                            {cite.document_title}
                          </span>
                          <span className="text-[11px] font-mono text-zinc-400 px-2 py-0.5 rounded bg-zinc-800">
                            {cite.section_title || `Section ${idx + 1}`}
                            {cite.page_number ? ` • p. ${cite.page_number}` : ''}
                          </span>
                        </div>
                        <div className="p-2.5 rounded-lg bg-zinc-950/70 border border-white/5 text-xs text-zinc-300 italic font-mono leading-relaxed">
                          &ldquo;{cite.excerpt}&rdquo;
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Refusal / Warning if sources not found (RAG-05) */}
              {!result.sources_found && (
                <div className="p-3.5 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-300 text-xs flex items-start gap-2.5">
                  <HelpCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
                  <div>
                    <strong className="font-semibold">Context Boundary (RAG-05): </strong>
                    The assistant refrains from hallucinating answers when no ingested document passes the semantic similarity threshold. Try asking questions covered by your course materials.
                  </div>
                </div>
              )}

              {/* Responsible AI Footer */}
              <div className="p-3 rounded-xl bg-zinc-900/50 border border-white/5 flex items-center gap-2.5 text-[11px] text-zinc-500">
                <ShieldCheck className="w-4 h-4 text-cyan-400 flex-shrink-0" />
                <span>
                  All responses are generated exclusively from verified course documentation using hybrid pgvector dense indexing.
                </span>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
