'use client';

import { useState, useEffect } from 'react';
import dynamic from 'next/dynamic';
import { Loader2 } from 'lucide-react';

const MonacoEditor = dynamic(
  () => import('@monaco-editor/react').then((mod) => mod.Editor),
  {
    ssr: false,
    loading: () => (
      <div className="w-full h-full min-h-[350px] bg-zinc-950 flex flex-col items-center justify-center text-zinc-500 gap-3 border border-white/5 rounded-xl font-mono text-xs">
        <Loader2 className="w-6 h-6 animate-spin text-cyan-400" />
        <span>Loading Monaco Editor...</span>
      </div>
    ),
  }
);

interface MonacoCodeEditorProps {
  value: string;
  onChange: (value: string) => void;
  language: string; // 'python' | 'javascript' | 'typescript' | 'cpp' | 'java' | 'go'
  height?: string;
  readOnly?: boolean;
}

export default function MonacoCodeEditor({
  value,
  onChange,
  language,
  height = '420px',
  readOnly = false,
}: MonacoCodeEditorProps) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return (
      <div 
        style={{ height }} 
        className="w-full bg-zinc-950 flex flex-col items-center justify-center text-zinc-500 gap-2 border border-white/5 rounded-xl font-mono text-xs"
      >
        <Loader2 className="w-5 h-5 animate-spin text-cyan-400" />
        <span>Initializing Monaco runtime...</span>
      </div>
    );
  }

  // Map internal language ids to Monaco language ids
  const monacoLanguage =
    language === 'cpp'
      ? 'cpp'
      : language === 'python'
      ? 'python'
      : language === 'javascript'
      ? 'javascript'
      : language === 'typescript'
      ? 'typescript'
      : language === 'java'
      ? 'java'
      : language === 'go'
      ? 'go'
      : 'plaintext';

  return (
    <div className="w-full rounded-xl overflow-hidden border border-white/10 bg-zinc-950 shadow-inner">
      <MonacoEditor
        height={height}
        language={monacoLanguage}
        value={value}
        onChange={(val) => onChange(val || '')}
        theme="vs-dark"
        options={{
          minimap: { enabled: false },
          fontSize: 14,
          fontFamily: "'Fira Code', 'JetBrains Mono', Menlo, Monaco, Consolas, monospace",
          fontLigatures: true,
          lineNumbers: 'on',
          scrollBeyondLastLine: false,
          automaticLayout: true,
          readOnly,
          tabSize: 4,
          cursorBlinking: 'smooth',
          cursorSmoothCaretAnimation: 'on',
          smoothScrolling: true,
          wordWrap: 'on',
          renderLineHighlight: 'all',
          padding: { top: 14, bottom: 14 },
        }}
      />
    </div>
  );
}
