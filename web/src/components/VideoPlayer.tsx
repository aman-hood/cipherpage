'use client';

import { useState, useEffect } from 'react';
import dynamic from 'next/dynamic';
import { Play, AlertCircle, Loader2 } from 'lucide-react';

const ReactPlayer = dynamic(() => import('react-player'), {
  ssr: false,
  loading: () => (
    <div className="w-full h-full flex flex-col items-center justify-center bg-zinc-950 text-zinc-400 gap-3">
      <Loader2 className="w-8 h-8 animate-spin text-cyan-400" />
      <p className="text-sm">Loading player...</p>
    </div>
  ),
});

export interface VideoPlayerProps {
  url?: string;
  src?: string;
  title?: string;
  controls?: boolean;
  playing?: boolean;
  muted?: boolean;
  loop?: boolean;
  onEnded?: () => void;
  onReady?: () => void;
  className?: string;
}

export default function VideoPlayer({
  url,
  src,
  title,
  controls = true,
  playing = false,
  muted = false,
  loop = false,
  onEnded,
  onReady,
  className = '',
}: VideoPlayerProps) {
  const [hasMounted, setHasMounted] = useState(false);
  const [hasError, setHasError] = useState(false);
  const [isReady, setIsReady] = useState(false);

  const videoSource = src || url || '';

  useEffect(() => {
    setHasMounted(true);
  }, []);

  useEffect(() => {
    setHasError(false);
    setIsReady(false);
  }, [videoSource]);

  if (!hasMounted) {
    return (
      <div className={`relative aspect-video w-full rounded-2xl bg-zinc-900/80 border border-white/10 flex flex-col items-center justify-center overflow-hidden ${className}`}>
        <div className="w-14 h-14 rounded-full bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center animate-pulse">
          <Play className="w-6 h-6 text-cyan-400 fill-cyan-400/20 ml-1" />
        </div>
        <p className="mt-3 text-sm text-zinc-500 font-medium">Initializing video player...</p>
      </div>
    );
  }

  if (hasError) {
    return (
      <div className={`relative aspect-video w-full rounded-2xl bg-zinc-900/80 border border-red-500/20 flex flex-col items-center justify-center p-6 text-center ${className}`}>
        <AlertCircle className="w-10 h-10 text-red-400 mb-3" />
        <h4 className="text-base font-semibold text-white mb-1">Failed to load video</h4>
        <p className="text-xs text-zinc-400 max-w-sm mb-4">
          The video may be private, removed, or restricted from external playback.
        </p>
        <button
          onClick={() => setHasError(false)}
          className="px-4 py-2 text-xs font-medium rounded-lg bg-zinc-800 hover:bg-zinc-700 text-zinc-200 border border-white/10 transition-colors cursor-pointer"
        >
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div className={`relative aspect-video w-full rounded-2xl overflow-hidden bg-black border border-white/10 shadow-2xl group ${className}`}>
      {!isReady && (
        <div className="absolute inset-0 z-10 flex flex-col items-center justify-center bg-zinc-950/90 backdrop-blur-xs transition-opacity duration-300">
          <Loader2 className="w-8 h-8 animate-spin text-cyan-400 mb-2" />
          <span className="text-xs text-zinc-400">Loading video stream...</span>
        </div>
      )}

      <ReactPlayer
        src={videoSource}
        controls={controls}
        playing={playing}
        muted={muted}
        loop={loop}
        width="100%"
        height="100%"
        onReady={() => {
          setIsReady(true);
          onReady?.();
        }}
        onError={() => setHasError(true)}
        onEnded={onEnded}
        style={{ position: 'absolute', top: 0, left: 0 }}
      />
    </div>
  );
}
