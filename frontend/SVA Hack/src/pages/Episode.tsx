import React, { useState, useEffect, useMemo } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { Episode as EpisodeType, ReelScene } from '../types';
import { getEpisodes } from '../lib/api';
import { getQuoteById } from '../lib/recommend';
import { markDone, isEpDone } from '../lib/progress';
import { QuoteCard } from '../components/QuoteCard';
import { ReelPlayer } from '../components/ReelPlayer';

export const EpisodePage: React.FC = () => {
  const { id, ep } = useParams<{ id: string; ep: string }>();
  const lessonId = Number(id) || 1;
  const epNum = Number(ep) || 1;
  const navigate = useNavigate();

  const [episodes, setEpisodes] = useState<EpisodeType[]>([]);
  const [isCompleted, setIsCompleted] = useState(false);

  useEffect(() => {
    getEpisodes(lessonId).then(setEpisodes);
    setIsCompleted(isEpDone(lessonId, epNum));
  }, [lessonId, epNum]);

  const episode = episodes.find((e) => e.ep === epNum) || episodes[0];

  const quote = useMemo(() => {
    if (!episode) return null;
    return getQuoteById(episode.quoteId);
  }, [episode]);

  // Construct scenes for placeholder ReelPlayer
  const episodeScenes: ReelScene[] = useMemo(() => {
    if (!episode) return [];
    return [
      {
        type: 'hook',
        text: `Episode ${episode.ep}: ${episode.title}`,
        durationMs: 4500
      },
      {
        type: 'situation',
        text: episode.situation || episode.story,
        durationMs: 7000
      },
      {
        type: 'quote',
        text: quote ? `"${quote.text}"` : 'All power is within you; you can do anything and everything.',
        quoteId: episode.quoteId,
        durationMs: 7500
      },
      {
        type: 'meaning',
        text: episode.moral || episode.meaning,
        durationMs: 6500
      },
      {
        type: 'outro',
        text: 'Step forward with courage and self-mastery. Arise and conquer.',
        durationMs: 4500
      }
    ];
  }, [episode, quote]);

  if (!episode) {
    return <div className="container" style={{ padding: '60px 20px' }}>Loading episode...</div>;
  }

  const handleCompleteAndNext = () => {
    markDone(lessonId, epNum);
    setIsCompleted(true);
    if (epNum < 6) {
      navigate(`/journey/${lessonId}/${epNum + 1}`);
    } else if (lessonId < 8) {
      navigate(`/journey/${lessonId + 1}`);
    } else {
      navigate('/journey');
    }
  };

  return (
    <main className="container" style={{ paddingTop: '28px', paddingBottom: '60px', maxWidth: '760px' }}>
      {/* Top Header & Breadcrumbs */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <Link
          to={`/journey/${lessonId}`}
          style={{ color: 'var(--muted)', textDecoration: 'none', fontSize: '0.875rem', fontWeight: 600 }}
        >
          ← Back to Lesson {lessonId}
        </Link>
        <span className="caption" style={{ fontWeight: 700, color: 'var(--accent)' }}>
          Episode {epNum} of 6 {isCompleted && '✓ Completed'}
        </span>
      </div>

      {/* Episode Header & Details Card */}
      <div className="card" style={{ padding: '32px', marginBottom: '32px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
          <span className="caption" style={{ fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em', color: 'var(--accent)' }}>
            Lesson {lessonId} · Episode {epNum}
          </span>
        </div>

        <h1 style={{ fontSize: '2rem', marginBottom: '24px', lineHeight: 1.25 }}>
          Episode {epNum} — {episode.title}
        </h1>

        {/* 1. SITUATION */}
        <div
          style={{
            backgroundColor: 'var(--surface)',
            padding: '22px 24px',
            borderRadius: 'var(--radius)',
            border: '1px solid var(--line)',
            marginBottom: '20px'
          }}
        >
          <span
            style={{
              fontSize: '0.78rem',
              fontWeight: 800,
              textTransform: 'uppercase',
              letterSpacing: '0.09em',
              color: 'var(--muted)',
              display: 'block',
              marginBottom: '8px'
            }}
          >
            Situation
          </span>
          <p style={{ margin: 0, fontSize: '1.18rem', lineHeight: 1.6, color: 'var(--ink)' }}>
            {episode.situation || episode.story}
          </p>
        </div>

        {/* 2. MORAL */}
        <div
          style={{
            backgroundColor: 'var(--accent-soft)',
            padding: '22px 24px',
            borderRadius: 'var(--radius)',
            border: '1.5px solid var(--accent)',
            marginBottom: '28px'
          }}
        >
          <span
            style={{
              fontSize: '0.78rem',
              fontWeight: 800,
              textTransform: 'uppercase',
              letterSpacing: '0.09em',
              color: 'var(--accent)',
              display: 'block',
              marginBottom: '8px'
            }}
          >
            Moral & Takeaway
          </span>
          <p style={{ margin: 0, fontSize: '1.18rem', lineHeight: 1.6, color: 'var(--ink)', fontWeight: 600 }}>
            {episode.moral || episode.meaning}
          </p>
        </div>

        {/* 3. VERIFIED TEACHING */}
        {quote && (
          <div style={{ marginBottom: '32px' }}>
            <span
              style={{
                fontSize: '0.78rem',
                fontWeight: 800,
                textTransform: 'uppercase',
                letterSpacing: '0.09em',
                color: 'var(--muted)',
                display: 'block',
                marginBottom: '10px'
              }}
            >
              Timeless Vivekananda Teaching
            </span>
            <QuoteCard quote={quote} />
          </div>
        )}

        {/* 4. PLACEHOLDER MEDIA PLAYER */}
        <div style={{ paddingTop: '16px', borderTop: '1px solid var(--line)' }}>
          <div style={{ textAlign: 'center', marginBottom: '16px' }}>
            <span
              className="caption"
              style={{
                fontSize: '0.85rem',
                fontWeight: 700,
                textTransform: 'uppercase',
                letterSpacing: '0.08em',
                color: 'var(--accent)',
                display: 'inline-flex',
                alignItems: 'center',
                gap: '6px'
              }}
            >
              ▶ 9:16 Reel Player (Placeholder / Ready for Media)
            </span>
            <p className="caption" style={{ margin: '4px 0 0 0', color: 'var(--muted)' }}>
              Interactive preview with touch controls and multi-speed playback
            </p>
          </div>

          <ReelPlayer
            scenes={episodeScenes}
            videoUrl={episode.videoUrl}
            lang="en"
            disclaimer="Media generator placeholder powered by ReelForge. Teachings verified from Complete Works of Swami Vivekananda."
          />
        </div>

        {/* Navigation Buttons */}
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginTop: '36px',
            paddingTop: '20px',
            borderTop: '1px solid var(--line)'
          }}
        >
          <button
            type="button"
            className="btn btn-secondary btn-sm"
            onClick={() => {
              if (epNum > 1) navigate(`/journey/${lessonId}/${epNum - 1}`);
            }}
            disabled={epNum === 1}
            style={{ opacity: epNum === 1 ? 0.4 : 1 }}
          >
            ← Previous Episode
          </button>

          <button
            type="button"
            className="btn btn-primary"
            onClick={handleCompleteAndNext}
          >
            {epNum < 6
              ? `Complete & Next Episode (${epNum + 1}) →`
              : lessonId < 8
              ? `Finish Lesson ${lessonId} & Next Sphere →`
              : 'Complete Swami Chakra Journey! →'}
          </button>
        </div>
      </div>
    </main>
  );
};
