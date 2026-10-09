import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { HistoryEntry } from '../types';
import { getHistory, deleteHistoryEntry, verifyGeminiApi, clearAllHistory } from '../lib/api';
import { ReelPlayer } from '../components/ReelPlayer';
import { QuoteCard } from '../components/QuoteCard';
import { Toast, ToastMessage } from '../components/Toast';
import { MandalaWatermark } from '../components/MandalaWatermark';

export const History: React.FC = () => {
  const navigate = useNavigate();
  const [history, setHistory] = useState<HistoryEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [expandedTranscripts, setExpandedTranscripts] = useState<Record<string, boolean>>({});
  const [activeInteractivePlayer, setActiveInteractivePlayer] = useState<string | null>(null);
  const [toasts, setToasts] = useState<ToastMessage[]>([]);

  const [apiVerifyResult, setApiVerifyResult] = useState<{
    status: string;
    api_called: boolean;
    model?: string;
    latency_ms?: number;
    tokens_used?: number;
    message?: string;
  } | null>(null);
  const [isVerifying, setIsVerifying] = useState(false);

  const checkApiVerification = async () => {
    setIsVerifying(true);
    try {
      const res = await verifyGeminiApi();
      setApiVerifyResult(res);
      if (res.api_called) {
        showToast(`✓ Gemini API Verified! Connected to ${res.model} (${res.latency_ms}ms)`);
      } else {
        showToast(`⚠️ Gemini API check failed: ${res.message || 'offline'}`);
      }
    } catch (e) {
      showToast('⚠️ Could not verify Gemini API connectivity.');
    } finally {
      setIsVerifying(false);
    }
  };

  const loadHistory = async () => {
    setLoading(true);
    try {
      const items = await getHistory();
      setHistory(items);
    } catch (err) {
      console.error('Failed to load history:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadHistory();
  }, []);

  const showToast = (text: string) => {
    const id = String(Date.now());
    setToasts((prev) => [...prev, { id, text }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 3500);
  };

  const handleDelete = async (id: string) => {
    const success = await deleteHistoryEntry(id);
    if (success) {
      setHistory((prev) => prev.filter((item) => item.id !== id));
      showToast('Reel history entry removed.');
    } else {
      showToast('Could not delete history entry.');
    }
  };

  const handleResetBrowserHistory = async () => {
    if (window.confirm('Are you sure you want to remove all saved browser and reel history?')) {
      const success = await clearAllHistory();
      if (success) {
        setHistory([]);
        showToast('✓ All browser history and reels have been cleared.');
      } else {
        showToast('Could not clear history.');
      }
    }
  };

  const toggleTranscript = (id: string) => {
    setExpandedTranscripts((prev) => ({
      ...prev,
      [id]: !prev[id]
    }));
  };

  const formatDate = (isoString: string) => {
    try {
      const date = new Date(isoString);
      return date.toLocaleDateString(undefined, {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch {
      return isoString;
    }
  };

  return (
    <main className="container" style={{ paddingTop: '32px', paddingBottom: '60px', maxWidth: '840px', position: 'relative' }}>
      <div style={{ position: 'absolute', top: 0, right: '5%', opacity: 0.04, pointerEvents: 'none' }}>
        <MandalaWatermark size={360} />
      </div>

      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '20px', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <span className="caption" style={{ textTransform: 'uppercase', letterSpacing: '0.1em', fontWeight: 700, color: 'var(--accent)' }}>
            Saved Perspectives & Reels
          </span>
          <h1 style={{ marginTop: '6px', marginBottom: '8px' }}>
            <span className="accent-underline">SOS Reel History</span>
          </h1>
          <p style={{ color: 'var(--muted)', fontSize: '1rem', margin: 0, maxWidth: '580px' }}>
            Every dilemma you submitted, the verified teaching mapped to it, the generated script transcript, and your video reels.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
          <button
            type="button"
            disabled={isVerifying}
            onClick={checkApiVerification}
            className="btn btn-secondary btn-sm"
            style={{ display: 'flex', alignItems: 'center', gap: '6px', backgroundColor: 'var(--surface)' }}
            title="Ping Gemini API and test connectivity"
          >
            <span style={{ color: isVerifying ? 'var(--muted)' : '#10b981' }}>●</span>
            <span>{isVerifying ? 'Testing API...' : 'Verify Gemini API'}</span>
          </button>
          <button
            type="button"
            onClick={loadHistory}
            className="btn btn-secondary btn-sm"
            style={{ display: 'flex', alignItems: 'center', gap: '6px' }}
            title="Refresh history"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M23 4v6h-6" />
              <path d="M1 20v-6h6" />
              <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15" />
            </svg>
            <span>Refresh</span>
          </button>
          {history.length > 0 && (
            <button
              type="button"
              onClick={handleResetBrowserHistory}
              className="btn btn-secondary btn-sm"
              style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#ef4444', borderColor: '#fca5a5' }}
              title="Remove all browser history from database"
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <polyline points="3 6 5 6 21 6" />
                <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
              </svg>
              <span>Reset History</span>
            </button>
          )}
          <Link to="/sos" className="btn btn-primary btn-sm">
            + New Dilemma
          </Link>
        </div>
      </div>

      {/* Live API Verification Result Banner */}
      {apiVerifyResult && (
        <div
          style={{
            marginBottom: '24px',
            padding: '12px 18px',
            borderRadius: 'var(--radius)',
            backgroundColor: apiVerifyResult.api_called ? 'rgba(16, 185, 129, 0.08)' : 'var(--accent-soft)',
            border: `1px solid ${apiVerifyResult.api_called ? '#10b981' : 'var(--accent)'}`,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            gap: '12px',
            flexWrap: 'wrap',
            animation: 'fadeIn 0.2s ease-out'
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span style={{ fontSize: '1.2rem' }}>{apiVerifyResult.api_called ? '✨' : '⚠️'}</span>
            <div>
              <strong style={{ fontSize: '0.88rem', color: 'var(--ink)', display: 'block' }}>
                {apiVerifyResult.api_called
                  ? `Gemini API Verified Live (${apiVerifyResult.model})`
                  : 'Gemini API Offline / Fallback'}
              </strong>
              <span className="caption" style={{ fontSize: '0.78rem', color: 'var(--muted)' }}>
                {apiVerifyResult.api_called
                  ? `Roundtrip: ${apiVerifyResult.latency_ms}ms • Tokens: ${apiVerifyResult.tokens_used} • Live script synthesis enabled`
                  : apiVerifyResult.message || 'API call failed'}
              </span>
            </div>
          </div>
          <span
            style={{
              fontSize: '0.75rem',
              fontWeight: 700,
              color: apiVerifyResult.api_called ? '#059669' : 'var(--accent)',
              backgroundColor: apiVerifyResult.api_called ? '#d1fae5' : 'var(--bg)',
              padding: '2px 8px',
              borderRadius: '999px',
              border: `1px solid ${apiVerifyResult.api_called ? '#a7f3d0' : 'var(--line)'}`
            }}
          >
            {apiVerifyResult.api_called ? 'ONLINE ✓' : 'OFFLINE'}
          </span>
        </div>
      )}

      {/* Loading State */}
      {loading && (
        <div className="card" style={{ padding: '40px', textAlign: 'center', color: 'var(--muted)' }}>
          <p style={{ margin: 0 }}>Loading your reel history from database...</p>
        </div>
      )}

      {/* Empty State */}
      {!loading && history.length === 0 && (
        <div className="card" style={{ padding: '48px 24px', textAlign: 'center' }}>
          <div style={{ display: 'inline-flex', padding: '16px', borderRadius: '50%', backgroundColor: 'var(--accent-soft)', marginBottom: '16px' }}>
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ color: 'var(--accent)' }}>
              <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
            </svg>
          </div>
          <h2 style={{ fontSize: '1.35rem', marginBottom: '8px' }}>No Saved Reels Yet</h2>
          <p style={{ color: 'var(--muted)', maxWidth: '420px', margin: '0 auto 24px auto', fontSize: '0.95rem' }}>
            Whenever you submit a question or feeling in SOS, your personalized script, verified teaching, and 45-second reel will automatically appear here.
          </p>
          <Link to="/sos" className="btn btn-primary">
            Ask Your First Dilemma in SOS →
          </Link>
        </div>
      )}

      {/* History Items List */}
      {!loading && history.length > 0 && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          {history.map((entry) => {
            const isTranscriptOpen = !!expandedTranscripts[entry.id];
            const isPlayingInteractive = activeInteractivePlayer === entry.id;

            return (
              <article
                key={entry.id}
                className="card"
                style={{
                  padding: '24px',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '18px',
                  border: '1px solid var(--line)',
                  borderRadius: 'var(--radius)'
                }}
              >
                {/* Entry Top Meta Bar */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '10px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
                    <span
                      style={{
                        padding: '4px 12px',
                        borderRadius: '999px',
                        fontSize: '0.78rem',
                        fontWeight: 700,
                        backgroundColor: 'var(--accent)',
                        color: 'var(--on-accent)',
                        letterSpacing: '0.04em',
                        textTransform: 'uppercase'
                      }}
                    >
                      {entry.journey}
                    </span>

                    <span
                      style={{
                        padding: '3px 10px',
                        borderRadius: '999px',
                        fontSize: '0.75rem',
                        fontWeight: 600,
                        backgroundColor: entry.video_url ? 'var(--accent-soft)' : 'var(--bg)',
                        color: 'var(--ink)',
                        border: '1px solid var(--line)'
                      }}
                    >
                      {entry.video_url ? '🎬 MP4 Video Ready' : entry.status === 'rendering' ? '⚡ Rendering...' : 'Interactive Reel'}
                    </span>

                    <span className="caption" style={{ color: 'var(--muted)' }}>
                      {formatDate(entry.created_at)}
                    </span>

                    <span
                      style={{
                        padding: '2px 8px',
                        borderRadius: '999px',
                        fontSize: '0.72rem',
                        fontWeight: 700,
                        backgroundColor: 'rgba(16, 185, 129, 0.1)',
                        color: '#059669',
                        border: '1px solid #a7f3d0'
                      }}
                    >
                      ✨ {entry.api_model || 'gemini-2.5-flash'}
                    </span>
                  </div>

                  <button
                    type="button"
                    onClick={() => handleDelete(entry.id)}
                    className="btn btn-secondary btn-sm"
                    style={{ padding: '4px 8px', color: 'var(--muted)', height: '28px', minHeight: '28px' }}
                    title="Delete history entry"
                    aria-label="Delete history entry"
                  >
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <polyline points="3 6 5 6 21 6" />
                      <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
                    </svg>
                  </button>
                </div>

                {/* User Dilemma Prompt & Context Badges */}
                <div style={{ backgroundColor: 'var(--bg)', padding: '16px', borderRadius: '10px', border: '1px solid var(--line)' }}>
                  <p style={{ margin: '0 0 12px 0', fontSize: '1.05rem', fontWeight: 600, color: 'var(--ink)', lineHeight: 1.45 }}>
                    "{entry.prompt}"
                  </p>

                  <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                    {entry.name && (
                      <span className="caption" style={{ backgroundColor: 'var(--surface)', padding: '3px 8px', borderRadius: '6px', border: '1px solid var(--line)' }}>
                        👤 {entry.name}
                      </span>
                    )}
                    {entry.age && (
                      <span className="caption" style={{ backgroundColor: 'var(--surface)', padding: '3px 8px', borderRadius: '6px', border: '1px solid var(--line)' }}>
                        🎂 {entry.age} yrs
                      </span>
                    )}
                    {entry.profession && (
                      <span className="caption" style={{ backgroundColor: 'var(--surface)', padding: '3px 8px', borderRadius: '6px', border: '1px solid var(--line)' }}>
                        💼 {entry.profession}
                      </span>
                    )}
                    <span className="caption" style={{ backgroundColor: 'var(--surface)', padding: '3px 8px', borderRadius: '6px', border: '1px solid var(--line)' }}>
                      🌐 {entry.lang === 'hi' ? 'Hindi' : 'English'}
                    </span>
                  </div>
                </div>

                {/* Video Playback or Interactive Player Toggle */}
                {entry.video_url ? (
                  <div>
                    <span className="caption" style={{ fontWeight: 700, textTransform: 'uppercase', display: 'block', marginBottom: '8px' }}>
                      Generated 9:16 Vertical Reel:
                    </span>
                    <div style={{ maxWidth: '320px', borderRadius: '14px', overflow: 'hidden', boxShadow: '0 8px 24px rgba(0,0,0,0.15)', backgroundColor: '#000' }}>
                      <video
                        src={entry.video_url}
                        controls
                        playsInline
                        style={{ width: '100%', display: 'block' }}
                      />
                    </div>
                  </div>
                ) : (
                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
                      <span className="caption" style={{ fontWeight: 700, textTransform: 'uppercase' }}>
                        Interactive Micro-Reel:
                      </span>
                      {entry.scenes && entry.scenes.length > 0 && (
                        <button
                          type="button"
                          className="btn btn-secondary btn-sm"
                          onClick={() => setActiveInteractivePlayer(isPlayingInteractive ? null : entry.id)}
                          style={{ fontSize: '0.8rem', padding: '4px 10px' }}
                        >
                          {isPlayingInteractive ? 'Hide Interactive Player' : 'Play Interactive Reel ▶'}
                        </button>
                      )}
                    </div>

                    {isPlayingInteractive && entry.scenes && entry.scenes.length > 0 && (
                      <div style={{ display: 'flex', justifyContent: 'center', marginTop: '12px' }}>
                        <ReelPlayer
                          scenes={entry.scenes}
                          lang={entry.lang}
                          disclaimer="Story and interpretation are AI-generated. The quote in the gold card is authentic and verified."
                        />
                      </div>
                    )}
                  </div>
                )}

                {/* Verified Complete Works Quote */}
                <div>
                  <span className="caption" style={{ fontWeight: 700, textTransform: 'uppercase', display: 'block', marginBottom: '8px' }}>
                    Authentic Verified Teaching:
                  </span>
                  <QuoteCard
                    quote={{
                      id: entry.quote_id,
                      text: entry.quote_text,
                      source: entry.quote_source,
                      sourceUrl: `https://advaitaashrama.org`,
                      verified: true,
                      topics: [entry.journey]
                    }}
                  />
                </div>

                {/* Accordion: Full 40s Transcript */}
                {entry.transcript && (
                  <div style={{ borderTop: '1px solid var(--line)', paddingTop: '12px' }}>
                    <button
                      type="button"
                      onClick={() => toggleTranscript(entry.id)}
                      style={{
                        background: 'none',
                        border: 'none',
                        color: 'var(--ink)',
                        cursor: 'pointer',
                        padding: 0,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        width: '100%',
                        fontSize: '0.9rem',
                        fontWeight: 600
                      }}
                    >
                      <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                          <polyline points="14 2 14 8 20 8" />
                          <line x1="16" y1="13" x2="8" y2="13" />
                          <line x1="16" y1="17" x2="8" y2="17" />
                        </svg>
                        Full Reel Transcript & Scenes
                      </span>
                      <span>{isTranscriptOpen ? '▲' : '▼'}</span>
                    </button>

                    {isTranscriptOpen && (
                      <div
                        style={{
                          marginTop: '10px',
                          padding: '14px',
                          borderRadius: '8px',
                          backgroundColor: 'var(--bg)',
                          fontSize: '0.88rem',
                          color: 'var(--ink)',
                          lineHeight: 1.6,
                          whiteSpace: 'pre-line',
                          border: '1px solid var(--line)'
                        }}
                      >
                        {entry.transcript}
                      </div>
                    )}
                  </div>
                )}

                {/* Bottom Action: Continue into corresponding Journey */}
                <div style={{ display: 'flex', justifyContent: 'flex-end', paddingTop: '8px', borderTop: '1px solid var(--line)' }}>
                  <button
                    type="button"
                    onClick={() => navigate(`/journey/${entry.lesson_id}`)}
                    className="btn btn-primary btn-sm"
                  >
                    Continue with {entry.journey} Journey →
                  </button>
                </div>
              </article>
            );
          })}
        </div>
      )}

      <Toast toasts={toasts} onDismiss={(id) => setToasts((prev) => prev.filter((t) => t.id !== id))} />
    </main>
  );
};
