import React, { useState, useEffect, useRef } from 'react';
import { ReelScene, SupportedLang } from '../types';
import { MandalaWatermark } from './MandalaWatermark';
import { QuoteCard } from './QuoteCard';
import { getQuoteById } from '../lib/recommend';
import { SUPPORTED_LANGS } from '../lib/i18n';

interface ReelPlayerProps {
  scenes: ReelScene[];
  lang: SupportedLang;
  videoUrl?: string;
  disclaimer?: string;
  isRendering?: boolean;
  renderProgress?: number;
}

export const ReelPlayer: React.FC<ReelPlayerProps> = ({
  scenes,
  lang,
  videoUrl,
  disclaimer,
  isRendering,
  renderProgress
}) => {
  const [currentIdx, setCurrentIdx] = useState(0);
  const [isPaused, setIsPaused] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [progressRatio, setProgressRatio] = useState(0); // 0 to 1 for current scene
  const [speed, setSpeed] = useState<number>(1.0);

  const videoRef = useRef<HTMLVideoElement | null>(null);
  const timerRef = useRef<number | null>(null);
  const progressIntervalRef = useRef<number | null>(null);
  const startTimeRef = useRef<number>(Date.now());
  const elapsedRef = useRef<number>(0);

  const currentScene = scenes[currentIdx] || scenes[0];
  const duration = currentScene?.durationMs || 6000;

  useEffect(() => {
    if (videoRef.current) {
      videoRef.current.playbackRate = speed;
    }
  }, [speed, videoUrl]);

  // TTS narration
  const speakCurrentScene = (text: string) => {
    if (!('speechSynthesis' in window)) return;
    try {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(text);
      const conf = SUPPORTED_LANGS.find((l) => l.code === lang);
      utterance.lang = conf?.ttsLang || 'en-IN';
      utterance.rate = 0.95 * speed;
      utterance.onend = () => setIsSpeaking(false);
      utterance.onerror = () => setIsSpeaking(false);
      setIsSpeaking(true);
      window.speechSynthesis.speak(utterance);
    } catch (e) {
      setIsSpeaking(false);
    }
  };

  const stopSpeaking = () => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
    }
    setIsSpeaking(false);
  };

  // Timer & progress update
  useEffect(() => {
    if (scenes.length === 0) return;

    if (isPaused) {
      if (progressIntervalRef.current) clearInterval(progressIntervalRef.current);
      return;
    }

    startTimeRef.current = Date.now() - (elapsedRef.current / speed);

    progressIntervalRef.current = window.setInterval(() => {
      const now = Date.now();
      const elapsed = (now - startTimeRef.current) * speed;
      elapsedRef.current = elapsed;
      const ratio = Math.min(1, elapsed / duration);
      setProgressRatio(ratio);

      if (elapsed >= duration) {
        // Advance scene
        clearInterval(progressIntervalRef.current!);
        elapsedRef.current = 0;
        setProgressRatio(0);
        if (currentIdx < scenes.length - 1) {
          setCurrentIdx((prev) => prev + 1);
        } else {
          // Loop back to start or stay on outro
          setCurrentIdx(0);
        }
      }
    }, 50);

    return () => {
      if (progressIntervalRef.current) clearInterval(progressIntervalRef.current);
    };
  }, [currentIdx, duration, isPaused, scenes.length, speed]);

  // Read current scene aloud if user toggled speaking
  useEffect(() => {
    if (isSpeaking && currentScene) {
      speakCurrentScene(currentScene.text);
    }
    return () => {
      stopSpeaking();
    };
  }, [currentIdx]);

  const handleNext = () => {
    elapsedRef.current = 0;
    setProgressRatio(0);
    if (currentIdx < scenes.length - 1) {
      setCurrentIdx((prev) => prev + 1);
    } else {
      setCurrentIdx(0);
    }
  };

  const handlePrev = () => {
    elapsedRef.current = 0;
    setProgressRatio(0);
    if (currentIdx > 0) {
      setCurrentIdx((prev) => prev - 1);
    }
  };

  const toggleNarration = () => {
    if (isSpeaking) {
      stopSpeaking();
    } else {
      speakCurrentScene(currentScene.text);
    }
  };

  const quote = currentScene.quoteId ? getQuoteById(currentScene.quoteId) : null;

  return (
    <div className="reel-wrapper">
      <div
        className="reel-container"
        onMouseDown={() => setIsPaused(true)}
        onMouseUp={() => setIsPaused(false)}
        onTouchStart={() => setIsPaused(true)}
        onTouchEnd={() => setIsPaused(false)}
      >
        {/* If videoUrl is provided, display video player */}
        {videoUrl ? (
          <video
            ref={videoRef}
            src={videoUrl}
            controls
            autoPlay
            playsInline
            style={{ width: '100%', height: '100%', objectFit: 'cover' }}
          />
        ) : (
          <>
            {/* Background mandala & gradient */}
            <div style={{ position: 'absolute', inset: 0, overflow: 'hidden', zIndex: 1 }}>
              <div
                style={{
                  position: 'absolute',
                  inset: 0,
                  background: 'radial-gradient(circle at 50% 35%, var(--accent-soft) 0%, var(--surface) 80%)',
                  opacity: 0.8
                }}
              />
              <div style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)' }}>
                <MandalaWatermark size={320} animate={!isPaused} />
              </div>
            </div>

            {/* Segmented Stories Progress Bar */}
            <div className="reel-progress-bars">
              {scenes.map((_, idx) => {
                let fill = '0%';
                if (idx < currentIdx) fill = '100%';
                else if (idx === currentIdx) fill = `${progressRatio * 100}%`;

                return (
                  <div key={idx} className="reel-bar-slot">
                    <div className="reel-bar-fill" style={{ width: fill }} />
                  </div>
                );
              })}
            </div>

            {/* Header overlay */}
            <div className="reel-header-overlay" style={{ justifyContent: 'flex-end' }}>
              <div style={{ display: 'flex', gap: '8px' }}>
                {/* TTS narration toggle */}
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    toggleNarration();
                  }}
                  className="btn btn-secondary btn-sm"
                  style={{
                    height: '32px',
                    minHeight: '32px',
                    padding: '0 10px',
                    fontSize: '0.75rem',
                    backgroundColor: isSpeaking ? 'var(--accent)' : 'var(--surface)',
                    color: isSpeaking ? 'var(--on-accent)' : 'var(--ink)'
                  }}
                  aria-label={isSpeaking ? 'Mute voice narration' : 'Enable voice narration'}
                >
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                    <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5" />
                    <path d="M15.54 8.46a5 5 0 0 1 0 7.07" />
                  </svg>
                  <span>{isSpeaking ? 'Speaking' : 'Narrate'}</span>
                </button>

                {/* Pause/Play indicator */}
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    setIsPaused(!isPaused);
                  }}
                  className="btn btn-secondary btn-sm"
                  style={{ height: '32px', minHeight: '32px', padding: '0 8px' }}
                  aria-label={isPaused ? 'Resume reel' : 'Pause reel'}
                >
                  {isPaused ? '▶' : '❚❚'}
                </button>
              </div>
            </div>

            {/* Tap left/right touch zones */}
            <div className="reel-touch-areas">
              <div
                className="reel-touch-left"
                onClick={handlePrev}
                title="Tap to view previous scene"
              />
              <div
                className="reel-touch-center"
                onClick={() => setIsPaused(!isPaused)}
                title="Tap to toggle pause"
              />
              <div
                className="reel-touch-right"
                onClick={handleNext}
                title="Tap to view next scene"
              />
            </div>

            {/* Scene Body Content (Cleanly centered) */}
            <div className="reel-content-scene">
              {currentScene.type === 'quote' && quote ? (
                <div style={{ width: '100%', maxWidth: '340px', textAlign: 'left' }}>
                  <QuoteCard quote={quote} />
                </div>
              ) : (
                <div style={{ maxWidth: '320px', textAlign: 'center' }}>
                  <p
                    style={{
                      fontFamily: currentScene.type === 'hook' || currentScene.type === 'outro' ? 'var(--font-head)' : 'var(--font-body)',
                      fontSize: currentScene.type === 'hook' ? '1.5rem' : '1.18rem',
                      fontWeight: currentScene.type === 'hook' ? 700 : 500,
                      lineHeight: 1.4,
                      color: 'var(--ink)',
                      margin: 0
                    }}
                  >
                    {currentScene.text}
                  </p>
                </div>
              )}
            </div>

            {/* In-player Reel Generation Progress Bar */}
            {isRendering && (
              <div
                style={{
                  position: 'absolute',
                  bottom: '24px',
                  left: '18px',
                  right: '18px',
                  backgroundColor: 'rgba(15, 23, 42, 0.88)',
                  backdropFilter: 'blur(10px)',
                  border: '1px solid var(--accent)',
                  borderRadius: '12px',
                  padding: '10px 14px',
                  zIndex: 25,
                  boxShadow: '0 8px 24px rgba(0,0,0,0.45)',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '6px'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span
                    style={{
                      fontSize: '0.8rem',
                      fontWeight: 600,
                      color: 'var(--accent)',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '8px'
                    }}
                  >
                    <span
                      style={{
                        display: 'inline-block',
                        width: '8px',
                        height: '8px',
                        borderRadius: '50%',
                        backgroundColor: 'var(--accent)',
                        boxShadow: '0 0 8px var(--accent)'
                      }}
                    />
                    Generating Reel...
                  </span>
                  <span style={{ fontSize: '0.82rem', fontWeight: 700, color: '#f8fafc' }}>
                    {renderProgress !== undefined ? `${renderProgress}%` : 'In progress'}
                  </span>
                </div>
                <div
                  style={{
                    width: '100%',
                    height: '6px',
                    backgroundColor: 'rgba(255, 255, 255, 0.15)',
                    borderRadius: '999px',
                    overflow: 'hidden'
                  }}
                >
                  <div
                    style={{
                      height: '100%',
                      width: `${Math.max(6, renderProgress ?? 0)}%`,
                      background: 'linear-gradient(90deg, var(--accent), #f59e0b)',
                      borderRadius: '999px',
                      transition: 'width 0.4s ease'
                    }}
                  />
                </div>
              </div>
            )}
          </>
        )}
      </div>

      {/* Playback Speed Controls: 1x, 1.5x, 2x */}
      <div
        className="reel-speed-selector"
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: '8px',
          marginTop: '12px',
          marginBottom: '6px'
        }}
      >
        <span style={{ fontSize: '0.8125rem', color: 'var(--muted)', fontWeight: 600 }}>
          Speed:
        </span>
        {[1, 1.5, 2].map((s) => (
          <button
            key={s}
            type="button"
            onClick={() => setSpeed(s)}
            style={{
              padding: '4px 12px',
              borderRadius: '9999px',
              border: '1.5px solid',
              borderColor: speed === s ? 'var(--accent)' : 'var(--line)',
              backgroundColor: speed === s ? 'var(--accent)' : 'var(--surface)',
              color: speed === s ? 'var(--on-accent)' : 'var(--ink)',
              fontSize: '0.8125rem',
              fontWeight: speed === s ? 700 : 500,
              cursor: 'pointer',
              transition: 'all 0.15s ease'
            }}
          >
            {s}x
          </button>
        ))}
      </div>

      {disclaimer && (
        <p className="caption" style={{ marginTop: '10px', textAlign: 'center', maxWidth: '380px' }}>
          {disclaimer}
        </p>
      )}
    </div>
  );
};
