import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate, Link } from 'react-router-dom';
import { ReelResponse, SupportedLang, Lesson } from '../types';
import { generateReel, getLessons, getJobProgress } from '../lib/api';
import { SUPPORTED_LANGS } from '../lib/i18n';
import { ReelPlayer } from '../components/ReelPlayer';
import { QuoteCard } from '../components/QuoteCard';
import { Toast, ToastMessage } from '../components/Toast';

export const SosResult: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();

  const stateData = location.state as {
    reelData?: ReelResponse;
    lang?: SupportedLang;
    prompt?: string;
    name?: string;
    age?: number;
    profession?: string;
  } | undefined;

  const [reel, setReel] = useState<ReelResponse | null>(stateData?.reelData || null);
  const [lang, setLang] = useState<SupportedLang>(stateData?.lang || 'en');
  const [lessons, setLessons] = useState<Lesson[]>([]);
  const [isTranscriptOpen, setIsTranscriptOpen] = useState(false);
  const [isTranslating, setIsTranslating] = useState(false);
  const [toasts, setToasts] = useState<ToastMessage[]>([]);
  const [videoProgress, setVideoProgress] = useState<number>(0);
  const [isVideoRendering, setIsVideoRendering] = useState<boolean>(false);

  const promptText = stateData?.prompt || "Feeling distracted and anxious";

  useEffect(() => {
    getLessons().then(setLessons);

    // If navigated directly to /sos/result without state
    if (!stateData?.reelData) {
      generateReel({ prompt: promptText, lang }).then(setReel);
    }
  }, []);

  // Poll for background video render completion if jobId present and videoUrl not set
  useEffect(() => {
    if (!reel?.jobId || reel.videoUrl) return;

    setIsVideoRendering(true);
    const interval = window.setInterval(async () => {
      try {
        const res = await getJobProgress(reel.jobId!);
        if (res.progress) setVideoProgress(res.progress);
        if (res.status === 'completed' && res.videoUrl) {
          clearInterval(interval);
          setIsVideoRendering(false);
          setReel((prev) => (prev ? { ...prev, videoUrl: res.videoUrl } : prev));
          showToast('🎬 Vertical MP4 video rendered and ready!');
        } else if (res.status === 'failed') {
          clearInterval(interval);
          setIsVideoRendering(false);
        }
      } catch (e) {
        clearInterval(interval);
      }
    }, 2500);

    return () => clearInterval(interval);
  }, [reel?.jobId, reel?.videoUrl]);

  const showToast = (text: string) => {
    const id = String(Date.now());
    setToasts((prev) => [...prev, { id, text }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 3500);
  };

  const handleLangChange = async (newLang: SupportedLang) => {
    if (newLang === lang || isTranslating) return;
    setLang(newLang);
    setIsTranslating(true);
    try {
      const updated = await generateReel({ prompt: promptText, lang: newLang });
      setReel(updated);
      showToast(`Language switched to ${SUPPORTED_LANGS.find((l) => l.code === newLang)?.label}`);
    } catch (e) {
      showToast('Could not reload reel language.');
    } finally {
      setIsTranslating(false);
    }
  };

  const handleShare = async () => {
    const shareData = {
      title: 'SwamiSays — Swami Vivekananda for Gen Z',
      text: reel ? `"${reel.quote.text}" — Complete Works of Swami Vivekananda` : 'SwamiSays Reel',
      url: window.location.href
    };

    if (navigator.share) {
      try {
        await navigator.share(shareData);
        return;
      } catch (err) {}
    }

    try {
      await navigator.clipboard.writeText(window.location.href);
      showToast('✓ Link copied to clipboard!');
    } catch (e) {
      showToast('Could not copy link.');
    }
  };

  if (!reel) {
    return (
      <main className="container" style={{ paddingTop: '80px', textAlign: 'center' }}>
        <p>Loading reel response...</p>
      </main>
    );
  }

  const recommendedLesson = lessons.find((l) => l.id === reel.lessonId) || lessons[0];

  return (
    <main className="container" style={{ paddingTop: '28px', paddingBottom: '60px' }}>
      {/* Top bar back link */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <Link to="/sos" style={{ color: 'var(--muted)', textDecoration: 'none', fontSize: '0.875rem', fontWeight: 600 }}>
          ← Back to SOS Input
        </Link>
        <span className="caption" style={{ fontWeight: 600, color: 'var(--accent)' }}>
          Generated Reel
        </span>
      </div>

      {/* Main 2-column or stacked layout */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '36px', alignItems: 'start' }}>
        {/* Left column: 9:16 Reel Player */}
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
          {isVideoRendering && !reel.videoUrl && (
            <div style={{ marginBottom: '10px', textAlign: 'center' }}>
              <span className="caption" style={{ display: 'inline-block', padding: '4px 14px', borderRadius: '999px', backgroundColor: 'var(--accent-soft)', color: 'var(--ink)', border: '1px solid var(--line)' }}>
                ⚡ Rendering full 9:16 MP4 video ({videoProgress}%)... Interactive player ready below
              </span>
            </div>
          )}
          {reel.videoUrl && (
            <div style={{ marginBottom: '10px', textAlign: 'center' }}>
              <span className="caption" style={{ display: 'inline-block', padding: '4px 14px', borderRadius: '999px', backgroundColor: 'var(--accent-soft)', color: 'var(--accent)', fontWeight: 700, border: '1px solid var(--accent)' }}>
                🎬 High-Definition 9:16 Video Ready
              </span>
            </div>
          )}
          <ReelPlayer
            scenes={reel.scenes}
            lang={lang}
            videoUrl={reel.videoUrl}
            disclaimer={reel.disclaimer}
            isRendering={isVideoRendering && !reel.videoUrl}
            renderProgress={videoProgress}
          />
        </div>

        {/* Right column: Details, Sources, Recommendation, Actions */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          {/* AI Generation Verification Card */}
          {reel.verification && (
            <div
              style={{
                padding: '14px 18px',
                borderRadius: 'var(--radius)',
                backgroundColor: reel.verification.api_called ? 'rgba(16, 185, 129, 0.08)' : 'var(--accent-soft)',
                border: `1px solid ${reel.verification.api_called ? '#10b981' : 'var(--accent)'}`,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                gap: '12px',
                flexWrap: 'wrap'
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <span style={{ fontSize: '1.2rem' }}>
                  {reel.verification.api_called ? '✨' : '⚠️'}
                </span>
                <div>
                  <strong style={{ fontSize: '0.88rem', color: 'var(--ink)', display: 'block' }}>
                    {reel.verification.api_called
                      ? `Verified AI Generation: Google ${reel.verification.model}`
                      : 'Offline Rule-Based Template'}
                  </strong>
                  <span className="caption" style={{ fontSize: '0.78rem', color: 'var(--muted)', display: 'block', marginTop: '2px' }}>
                    {reel.verification.api_called
                      ? `Tokens: ${reel.verification.tokens_used || 'N/A'} • Authenticity: Zero Quote Invention`
                      : reel.verification.reason || 'Fallback used'}
                  </span>
                </div>
              </div>
              {reel.verification.api_called && (
                <span
                  style={{
                    fontSize: '0.75rem',
                    fontWeight: 700,
                    color: '#059669',
                    backgroundColor: '#d1fae5',
                    padding: '3px 10px',
                    borderRadius: '999px',
                    border: '1px solid #a7f3d0'
                  }}
                >
                  GEMINI ACTIVE ✓
                </span>
              )}
            </div>
          )}

          {/* Language Switcher Card */}
          <div className="card" style={{ padding: '20px' }}>
            <span className="caption" style={{ fontWeight: 700, textTransform: 'uppercase', display: 'block', marginBottom: '10px' }}>
              Switch Reel Language:
            </span>
            <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
              {SUPPORTED_LANGS.map((item) => (
                <button
                  key={item.code}
                  type="button"
                  disabled={isTranslating}
                  onClick={() => handleLangChange(item.code)}
                  className={`btn btn-sm ${lang === item.code ? 'btn-primary' : 'btn-secondary'}`}
                  style={{ opacity: isTranslating ? 0.6 : 1 }}
                >
                  {item.label}
                </button>
              ))}
            </div>
            {isTranslating && (
              <p className="caption" style={{ marginTop: '8px', marginBottom: 0 }}>
                Translating narration & scenes...
              </p>
            )}
          </div>

          {/* Recommended Journey Lesson Card */}
          {recommendedLesson && (
            <div className="card" style={{ border: '2px solid var(--accent)', padding: '24px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                <span className="caption" style={{ fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em', color: 'var(--accent)' }}>
                  Recommended Journey Lesson
                </span>
                <span className="caption" style={{ fontWeight: 600 }}>
                  Ep {reel.episode} of 6
                </span>
              </div>

              <h2 style={{ fontSize: '1.4rem', marginBottom: '6px' }}>
                Lesson {recommendedLesson.id} · {recommendedLesson.title}
              </h2>

              <p style={{ fontStyle: 'italic', color: 'var(--muted)', fontSize: '0.9375rem', marginBottom: '12px' }}>
                "{recommendedLesson.painPoint}"
              </p>

              <p style={{ fontSize: '0.9375rem', color: 'var(--ink)', marginBottom: '20px', lineHeight: 1.45 }}>
                {recommendedLesson.summary}
              </p>

              <button
                type="button"
                className="btn btn-primary btn-sm"
                onClick={() => navigate(`/journey/${recommendedLesson.id}/${reel.episode}`)}
                style={{ width: '100%' }}
              >
                Begin Lesson {recommendedLesson.id} (Episode {reel.episode}) →
              </button>
            </div>
          )}

          {/* Original Verified Source Card */}
          <div>
            <span className="caption" style={{ fontWeight: 700, textTransform: 'uppercase', display: 'block', marginBottom: '10px' }}>
              Original Verified Source:
            </span>
            <QuoteCard
              quote={{
                id: reel.quoteId,
                text: reel.quote.text,
                source: reel.quote.source,
                sourceUrl: reel.quote.sourceUrl,
                verified: reel.quote.verified,
                topics: []
              }}
            />
          </div>

          {/* Transcript Accordion */}
          <div className="card" style={{ padding: '20px' }}>
            <button
              type="button"
              onClick={() => setIsTranscriptOpen(!isTranscriptOpen)}
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                width: '100%',
                background: 'none',
                border: 'none',
                color: 'var(--ink)',
                cursor: 'pointer',
                padding: 0,
                textAlign: 'left',
                fontFamily: 'var(--font-head)',
                fontSize: '1.1rem',
                fontWeight: 700
              }}
            >
              <span>Full Reel Transcript</span>
              <span>{isTranscriptOpen ? '▲' : '▼'}</span>
            </button>

            {isTranscriptOpen && (
              <div style={{ marginTop: '16px', paddingTop: '16px', borderTop: '1px solid var(--line)', whiteSpace: 'pre-line', fontSize: '0.9375rem', color: 'var(--ink)', lineHeight: 1.6 }}>
                {reel.transcript}
              </div>
            )}
          </div>

          {/* Actions: Share & Try Another */}
          <div style={{ display: 'flex', gap: '12px' }}>
            <button
              type="button"
              onClick={handleShare}
              className="btn btn-primary"
              style={{ flex: 1 }}
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                <circle cx="18" cy="5" r="3" />
                <circle cx="6" cy="12" r="3" />
                <circle cx="18" cy="19" r="3" />
                <line x1="8.59" y1="13.51" x2="15.42" y2="17.49" />
                <line x1="15.41" y1="6.51" x2="8.59" y2="10.49" />
              </svg>
              <span>Share Reel</span>
            </button>

            <Link to="/sos" className="btn btn-secondary" style={{ flex: 1, textDecoration: 'none' }}>
              Ask Another
            </Link>
          </div>
        </div>
      </div>

      <Toast toasts={toasts} onDismiss={(id) => setToasts((prev) => prev.filter((t) => t.id !== id))} />
    </main>
  );
};
