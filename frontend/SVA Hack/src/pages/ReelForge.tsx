import React, { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import {
  getForgeStatus,
  getForgeTemplates,
  getForgeShowcase,
  generateForgeVideo,
  getForgeJob
} from '../lib/api';
import { ForgeStatus, ForgeTemplate, ForgeJob } from '../types';
import { MandalaWatermark } from '../components/MandalaWatermark';
import { Toast, ToastMessage } from '../components/Toast';

export const ReelForge: React.FC = () => {
  const [status, setStatus] = useState<ForgeStatus | null>(null);
  const [templates, setTemplates] = useState<ForgeTemplate[]>([]);
  const [selectedTemplateId, setSelectedTemplateId] = useState<string>('vivekananda');
  const [prompt, setPrompt] = useState<string>('');
  const [aspectRatio, setAspectRatio] = useState<'9:16' | '16:9'>('9:16');
  const [voiceId, setVoiceId] = useState<string>('en-IN-PrabhatNeural');
  const [musicTrack, setMusicTrack] = useState<string>('motivational_ambient.mp3');
  const [subtitleColor, setSubtitleColor] = useState<string>('yellow');
  const [useStockClips, setUseStockClips] = useState<boolean>(true);
  const [style, setStyle] = useState<string>('cinematic');

  const [activeJobId, setActiveJobId] = useState<string | null>(null);
  const [jobState, setJobState] = useState<ForgeJob | null>(null);
  const [isGenerating, setIsGenerating] = useState<boolean>(false);
  const [renderedVideoUrl, setRenderedVideoUrl] = useState<string | null>(null);
  const [showcase, setShowcase] = useState<{ title: string; videoUrl: string | null; description: string } | null>(null);
  const [toasts, setToasts] = useState<ToastMessage[]>([]);
  const [showLogs, setShowLogs] = useState<boolean>(false);

  const logsEndRef = useRef<HTMLDivElement | null>(null);

  // Load initial ReelForge data
  useEffect(() => {
    getForgeStatus().then((s) => {
      if (s) setStatus(s);
    });

    getForgeTemplates().then((tpls) => {
      if (tpls && tpls.length > 0) {
        setTemplates(tpls);
        const viv = tpls.find((t) => t.id === 'vivekananda') || tpls[0];
        setSelectedTemplateId(viv.id);
        setPrompt(viv.prompt);
      }
    });

    getForgeShowcase().then((sc) => {
      if (sc) setShowcase(sc);
    });
  }, []);

  // Poll active generation job
  useEffect(() => {
    if (!activeJobId || !isGenerating) return;

    const interval = window.setInterval(async () => {
      const job = await getForgeJob(activeJobId);
      if (job) {
        setJobState(job);
        if (job.completed) {
          setIsGenerating(false);
          clearInterval(interval);
          if (job.video_url) {
            setRenderedVideoUrl(job.video_url);
            showToast('🎬 Reel generated successfully!');
          } else if (job.error) {
            showToast(`❌ Generation failed: ${job.error}`);
          }
        }
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [activeJobId, isGenerating]);

  // Scroll logs automatically
  useEffect(() => {
    if (showLogs && logsEndRef.current) {
      logsEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [jobState?.logs, showLogs]);

  const showToast = (text: string) => {
    const id = String(Date.now());
    setToasts((prev) => [...prev, { id, text }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 4000);
  };

  const handleSelectTemplate = (template: ForgeTemplate) => {
    setSelectedTemplateId(template.id);
    setPrompt(template.prompt);
  };

  const handleStartGeneration = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim()) return;

    setIsGenerating(true);
    setRenderedVideoUrl(null);
    setJobState(null);

    try {
      const res = await generateForgeVideo({
        prompt: prompt.trim(),
        aspect_ratio: aspectRatio,
        voice_id: voiceId,
        music_track: musicTrack,
        subtitle_color: subtitleColor,
        use_stock_clips: useStockClips,
        style
      });

      setActiveJobId(res.jobId);
      showToast('🚀 Video generation started in background!');
    } catch (err: any) {
      setIsGenerating(false);
      showToast(`Error starting generation: ${err.message}`);
    }
  };

  return (
    <main className="container" style={{ paddingTop: '32px', paddingBottom: '72px', position: 'relative' }}>
      <div style={{ position: 'absolute', top: 0, right: '5%', opacity: 0.05, pointerEvents: 'none' }}>
        <MandalaWatermark size={380} />
      </div>

      {/* Header */}
      <div style={{ textAlign: 'center', marginBottom: '32px' }}>
        <span
          className="caption"
          style={{
            textTransform: 'uppercase',
            letterSpacing: '0.12em',
            fontWeight: 700,
            color: 'var(--accent)',
            backgroundColor: 'var(--accent-soft)',
            padding: '4px 14px',
            borderRadius: '999px',
            border: '1px solid var(--line)'
          }}
        >
          🎬 ReelForge Studio
        </span>
        <h1 style={{ marginTop: '12px', marginBottom: '10px' }}>
          <span className="accent-underline">Prompt to Video Engine</span>
        </h1>
        <p style={{ color: 'var(--muted)', fontSize: '1.05rem', maxWidth: '640px', margin: '0 auto' }}>
          Create authentic vertical reels (9:16) and videos with AI narration, stock footage, historical Swami Vivekananda portraits, burned subtitles, and ducked ambient music.
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '36px', alignItems: 'start' }}>
        {/* Left Column: Studio Controls & Prompt */}
        <div className="card" style={{ padding: '28px', backgroundColor: 'var(--surface)', borderColor: 'var(--line)' }}>
          <h2 style={{ fontSize: '1.25rem', marginBottom: '18px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span>✨</span> Create New Reel
          </h2>

          {/* Preset Inspiration Templates */}
          <div style={{ marginBottom: '20px' }}>
            <label className="caption" style={{ fontWeight: 700, display: 'block', marginBottom: '8px' }}>
              Choose a Preset Template:
            </label>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
              {templates.map((tpl) => (
                <button
                  key={tpl.id}
                  type="button"
                  onClick={() => handleSelectTemplate(tpl)}
                  className={`chip ${selectedTemplateId === tpl.id ? 'active' : ''}`}
                  style={{ fontSize: '0.8125rem' }}
                >
                  {tpl.title}
                </button>
              ))}
            </div>
          </div>

          <form onSubmit={handleStartGeneration}>
            {/* Script Textarea */}
            <div style={{ marginBottom: '20px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                <label htmlFor="reelPrompt" className="caption" style={{ fontWeight: 700 }}>
                  Script / Prompt:
                </label>
                <span className="caption" style={{ color: 'var(--muted)', fontSize: '0.75rem' }}>
                  Supports SCENE:, CAPTION:, FOOTAGE:
                </span>
              </div>
              <textarea
                id="reelPrompt"
                rows={11}
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="SCENE: Your narration line...\nCAPTION: Short subtitle...\nFOOTAGE: nature_sunrise"
                style={{
                  width: '100%',
                  fontFamily: 'monospace',
                  fontSize: '0.875rem',
                  lineHeight: '1.5',
                  padding: '12px',
                  borderRadius: 'var(--radius)',
                  border: '1px solid var(--line)',
                  backgroundColor: 'var(--surface)',
                  color: 'var(--ink)',
                  resize: 'vertical'
                }}
                disabled={isGenerating}
                required
              />
            </div>

            {/* Studio Options Grid */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '20px' }}>
              {/* Aspect Ratio */}
              <div>
                <label className="caption" style={{ fontWeight: 700, display: 'block', marginBottom: '6px' }}>
                  Aspect Ratio
                </label>
                <div style={{ display: 'flex', gap: '6px' }}>
                  <button
                    type="button"
                    onClick={() => setAspectRatio('9:16')}
                    className={`btn ${aspectRatio === '9:16' ? 'btn-primary' : 'btn-secondary'} btn-sm`}
                    style={{ flex: 1, padding: '6px 8px', fontSize: '0.75rem' }}
                  >
                    9:16 Vertical
                  </button>
                  <button
                    type="button"
                    onClick={() => setAspectRatio('16:9')}
                    className={`btn ${aspectRatio === '16:9' ? 'btn-primary' : 'btn-secondary'} btn-sm`}
                    style={{ flex: 1, padding: '6px 8px', fontSize: '0.75rem' }}
                  >
                    16:9 Wide
                  </button>
                </div>
              </div>

              {/* Subtitle Style */}
              <div>
                <label className="caption" style={{ fontWeight: 700, display: 'block', marginBottom: '6px' }}>
                  Subtitle Color
                </label>
                <select
                  value={subtitleColor}
                  onChange={(e) => setSubtitleColor(e.target.value)}
                  disabled={isGenerating}
                  style={{
                    width: '100%',
                    padding: '8px 10px',
                    borderRadius: '8px',
                    border: '1px solid var(--line)',
                    backgroundColor: 'var(--surface)',
                    color: 'var(--ink)',
                    fontSize: '0.8125rem'
                  }}
                >
                  <option value="yellow">Yellow (Viral / TikTok)</option>
                  <option value="gold">Gold (Sacred / Classical)</option>
                  <option value="saffron">Saffron (Kesari)</option>
                  <option value="white">Clean White</option>
                  <option value="cyan">Cyber Cyan</option>
                </select>
              </div>

              {/* Narrator Voice */}
              <div>
                <label className="caption" style={{ fontWeight: 700, display: 'block', marginBottom: '6px' }}>
                  Narrator Voice
                </label>
                <select
                  value={voiceId}
                  onChange={(e) => setVoiceId(e.target.value)}
                  disabled={isGenerating}
                  style={{
                    width: '100%',
                    padding: '8px 10px',
                    borderRadius: '8px',
                    border: '1px solid var(--line)',
                    backgroundColor: 'var(--surface)',
                    color: 'var(--ink)',
                    fontSize: '0.8125rem'
                  }}
                >
                  <option value="en-IN-PrabhatNeural">Prabhat (Indian Male - Clear)</option>
                  <option value="hi-IN-MadhurNeural">Madhur (Hindi/Indian Male)</option>
                  <option value="en-IN-SwaraNeural">Swara (Indian Female)</option>
                  <option value="en-US-ChristopherNeural">Christopher (US Male - Deep)</option>
                  <option value="en-US-JennyNeural">Jenny (US Female - Warm)</option>
                  <option value="en-GB-RyanNeural">Ryan (UK Male - Cinematic)</option>
                </select>
              </div>

              {/* Background Music */}
              <div>
                <label className="caption" style={{ fontWeight: 700, display: 'block', marginBottom: '6px' }}>
                  Background Score
                </label>
                <select
                  value={musicTrack}
                  onChange={(e) => setMusicTrack(e.target.value)}
                  disabled={isGenerating}
                  style={{
                    width: '100%',
                    padding: '8px 10px',
                    borderRadius: '8px',
                    border: '1px solid var(--line)',
                    backgroundColor: 'var(--surface)',
                    color: 'var(--ink)',
                    fontSize: '0.8125rem'
                  }}
                >
                  <option value="motivational_ambient.mp3">Motivational Ambient (Gentle)</option>
                  <option value="motivational_inspiring.mp3">Motivational Inspiring (Uplifting)</option>
                  <option value="motivational_cinematic.mp3">Cinematic Strings (Dramatic)</option>
                  <option value="random">Random Track</option>
                </select>
              </div>
            </div>

            {/* Checkbox: Use Stock Video Clips */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '24px' }}>
              <input
                type="checkbox"
                id="useStockClips"
                checked={useStockClips}
                onChange={(e) => setUseStockClips(e.target.checked)}
                disabled={isGenerating}
                style={{ width: '16px', height: '16px', accentColor: 'var(--accent)' }}
              />
              <label htmlFor="useStockClips" style={{ fontSize: '0.875rem', color: 'var(--ink)' }}>
                Use 50+ Stock Video Clips & Historical Swami Vivekananda Portraits
              </label>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isGenerating || !prompt.trim()}
              className="btn btn-primary"
              style={{
                width: '100%',
                height: '46px',
                fontSize: '0.95rem',
                fontWeight: 700,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px'
              }}
            >
              {isGenerating ? (
                <>
                  <span className="spinner" style={{ width: '16px', height: '16px' }} />
                  <span>Forging Video ({jobState?.progress || 10}%)...</span>
                </>
              ) : (
                <>
                  <span>🎬</span>
                  <span>Forge Video Reel</span>
                </>
              )}
            </button>
          </form>
        </div>

        {/* Right Column: Video Player & Live Generation Status */}
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
          {/* Progress / Generation Card */}
          {isGenerating && (
            <div
              className="card"
              style={{
                width: '100%',
                maxWidth: '420px',
                padding: '24px',
                marginBottom: '20px',
                backgroundColor: 'var(--surface)',
                borderColor: 'var(--accent)',
                boxShadow: 'var(--card-shadow)',
                animation: 'fadeIn 0.2s ease-out'
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                <span className="caption" style={{ fontWeight: 700, color: 'var(--accent)' }}>
                  ⚡ FORGING REEL ({jobState?.progress || 10}%)
                </span>
                <span className="caption" style={{ color: 'var(--muted)', fontSize: '0.75rem' }}>
                  {jobState?.stage || 'processing'}
                </span>
              </div>

              {/* Progress Bar */}
              <div style={{ width: '100%', height: '8px', backgroundColor: 'var(--line)', borderRadius: '4px', overflow: 'hidden', marginBottom: '14px' }}>
                <div
                  style={{
                    height: '100%',
                    width: `${jobState?.progress || 15}%`,
                    backgroundColor: 'var(--accent)',
                    transition: 'width 0.4s ease'
                  }}
                />
              </div>

              <p style={{ fontSize: '0.875rem', color: 'var(--ink)', marginBottom: '14px' }}>
                {jobState?.message || 'Writing cinematic script and timing narration...'}
              </p>

              {/* Activity Logs toggle */}
              <button
                type="button"
                onClick={() => setShowLogs(!showLogs)}
                style={{
                  background: 'none',
                  border: 'none',
                  padding: 0,
                  fontSize: '0.8125rem',
                  color: 'var(--accent)',
                  cursor: 'pointer',
                  fontWeight: 600
                }}
              >
                {showLogs ? '▲ Hide Activity Logs' : '▼ View Live Render Logs'}
              </button>

              {showLogs && jobState?.logs && (
                <div
                  style={{
                    marginTop: '12px',
                    padding: '10px',
                    borderRadius: '8px',
                    backgroundColor: '#111',
                    color: '#a3e635',
                    fontFamily: 'monospace',
                    fontSize: '0.75rem',
                    maxHeight: '140px',
                    overflowY: 'auto',
                    textAlign: 'left'
                  }}
                >
                  {jobState.logs.map((log, idx) => (
                    <div key={idx}>{log}</div>
                  ))}
                  <div ref={logsEndRef} />
                </div>
              )}
            </div>
          )}

          {/* Rendered or Showcase Video Player */}
          <div
            style={{
              width: '100%',
              maxWidth: aspectRatio === '9:16' ? '360px' : '520px',
              aspectRatio: aspectRatio === '9:16' ? '9/16' : '16/9',
              borderRadius: 'var(--radius)',
              overflow: 'hidden',
              backgroundColor: '#000',
              boxShadow: '0 12px 40px rgba(0,0,0,0.28)',
              position: 'relative',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}
          >
            {renderedVideoUrl ? (
              <video
                src={renderedVideoUrl}
                controls
                autoPlay
                loop
                playsInline
                style={{ width: '100%', height: '100%', objectFit: 'cover' }}
              />
            ) : showcase?.videoUrl ? (
              <video
                src={showcase.videoUrl}
                controls
                loop
                playsInline
                poster="/figures/vivekananda/vivekananda_01_chicago_1893_signed.jpg"
                style={{ width: '100%', height: '100%', objectFit: 'cover' }}
              />
            ) : (
              <div style={{ textAlign: 'center', color: '#fff', padding: '24px' }}>
                <p style={{ fontSize: '1rem', marginBottom: '8px' }}>🎬 Video Output Screen</p>
                <p style={{ fontSize: '0.8125rem', opacity: 0.7 }}>Click "Forge Video Reel" to render your reel.</p>
              </div>
            )}
          </div>

          {/* Action Buttons beneath Video */}
          <div style={{ marginTop: '16px', display: 'flex', gap: '12px' }}>
            {(renderedVideoUrl || showcase?.videoUrl) && (
              <a
                href={renderedVideoUrl || showcase?.videoUrl || '#'}
                download="reel.mp4"
                className="btn btn-secondary btn-sm"
                style={{ textDecoration: 'none', display: 'inline-flex', alignItems: 'center', gap: '6px' }}
              >
                <span>⬇</span>
                <span>Download MP4</span>
              </a>
            )}
            <Link
              to="/journey"
              className="btn btn-secondary btn-sm"
              style={{ textDecoration: 'none', display: 'inline-flex', alignItems: 'center', gap: '6px' }}
            >
              <span>🧭</span>
              <span>Explore Journey Mode</span>
            </Link>
          </div>
        </div>
      </div>

      <Toast toasts={toasts} onDismiss={(id) => setToasts((prev) => prev.filter((t) => t.id !== id))} />
    </main>
  );
};
