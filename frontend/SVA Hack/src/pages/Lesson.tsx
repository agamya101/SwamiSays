import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { Lesson, Episode } from '../types';
import { getLessons, getEpisodes } from '../lib/api';
import { getDone } from '../lib/progress';

export const LessonPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const lessonId = Number(id) || 1;
  const navigate = useNavigate();

  const [lesson, setLesson] = useState<Lesson | null>(null);
  const [episodes, setEpisodes] = useState<Episode[]>([]);

  useEffect(() => {
    getLessons().then((all) => {
      const found = all.find((l) => l.id === lessonId);
      setLesson(found || all[0]);
    });
    getEpisodes(lessonId).then(setEpisodes);
  }, [lessonId]);

  if (!lesson) {
    return <div className="container" style={{ padding: '60px 20px' }}>Loading lesson...</div>;
  }

  const completed = getDone(lessonId);
  const nextIncomplete = episodes.find((e) => !completed.includes(e.ep)) || episodes[0];

  return (
    <main className="container" style={{ paddingTop: '32px', paddingBottom: '60px' }}>
      {/* Breadcrumb */}
      <div style={{ marginBottom: '20px' }}>
        <Link to="/journey" style={{ color: 'var(--muted)', textDecoration: 'none', fontSize: '0.875rem', fontWeight: 600 }}>
          ← Back to Swami Chakra
        </Link>
      </div>

      {/* Lesson Header */}
      <div style={{ marginBottom: '40px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
          <span className="caption" style={{ fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em', color: 'var(--accent)' }}>
            Lesson {lesson.id} of 8
          </span>
          <span className="caption">•</span>
          <span className="caption">{completed.length} / 6 completed</span>
        </div>

        <h1 style={{ marginBottom: '12px' }}>
          <span className="accent-underline">{lesson.title}</span>
        </h1>

        <p style={{ fontStyle: 'italic', color: 'var(--muted)', fontSize: '1.25rem', marginBottom: '16px', maxWidth: '50ch' }}>
          "{lesson.painPoint}"
        </p>

        <p style={{ color: 'var(--ink)', fontSize: '1.0625rem', marginBottom: '24px', maxWidth: '60ch' }}>
          {lesson.summary}
        </p>

        {nextIncomplete && (
          <button
            type="button"
            className="btn btn-primary"
            onClick={() => navigate(`/journey/${lesson.id}/${nextIncomplete.ep}`)}
          >
            {completed.length > 0 ? `Continue Episode ${nextIncomplete.ep}: ${nextIncomplete.title} →` : `Start Episode 1: ${episodes[0]?.title || ''} →`}
          </button>
        )}
      </div>

      {/* Episode list */}
      <section>
        <h2 style={{ fontSize: '1.35rem', marginBottom: '20px' }}>
          Episodes in this lesson
        </h2>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {episodes.map((ep) => {
            const isDone = completed.includes(ep.ep);

            return (
              <Link
                key={ep.ep}
                to={`/journey/${lesson.id}/${ep.ep}`}
                style={{ textDecoration: 'none', color: 'inherit' }}
              >
                <div
                  className="card"
                  style={{
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '12px',
                    padding: '20px 24px',
                    borderColor: isDone ? 'var(--accent)' : 'var(--line)',
                    transition: 'transform 0.15s ease, border-color 0.15s ease'
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                      <div
                        style={{
                          width: '32px',
                          height: '32px',
                          borderRadius: '50%',
                          backgroundColor: isDone ? 'var(--accent)' : 'var(--surface)',
                          color: isDone ? 'var(--on-accent)' : 'var(--muted)',
                          border: '1px solid var(--line)',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          fontWeight: 700,
                          fontSize: '0.85rem'
                        }}
                      >
                        {isDone ? '✓' : ep.ep}
                      </div>
                      <h3 style={{ margin: 0, fontSize: '1.15rem', fontWeight: 700 }}>
                        Episode {ep.ep} — {ep.title}
                      </h3>
                    </div>
                    <span style={{ color: 'var(--accent)', fontWeight: 600, fontSize: '0.875rem' }}>
                      Play Episode →
                    </span>
                  </div>

                  {ep.situation && (
                    <div style={{ paddingLeft: '44px' }}>
                      <p style={{ margin: 0, fontSize: '0.9375rem', lineHeight: 1.5, color: 'var(--ink)' }}>
                        <strong style={{ color: 'var(--muted)' }}>Situation: </strong>
                        {ep.situation}
                      </p>
                    </div>
                  )}

                  {ep.moral && (
                    <div style={{ paddingLeft: '44px' }}>
                      <p style={{ margin: 0, fontSize: '0.9375rem', lineHeight: 1.5, color: 'var(--ink)' }}>
                        <strong style={{ color: 'var(--accent)' }}>Moral: </strong>
                        {ep.moral}
                      </p>
                    </div>
                  )}
                </div>
              </Link>
            );
          })}
        </div>
      </section>
    </main>
  );
};
