import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Lesson } from '../types';
import { getLessons } from '../lib/api';
import { IkigaiWheel } from '../components/IkigaiWheel';
import { LessonListView } from '../components/LessonListView';
import { Chip } from '../components/Chip';

export const Journey: React.FC = () => {
  const [lessons, setLessons] = useState<Lesson[]>([]);
  const [viewMode, setViewMode] = useState<'wheel' | 'list'>('wheel');
  const navigate = useNavigate();

  useEffect(() => {
    getLessons().then(setLessons);
  }, []);

  return (
    <main className="container" style={{ paddingTop: '32px', paddingBottom: '60px' }}>
      {/* Header and View Toggle */}
      <div style={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'space-between', alignItems: 'flex-end', gap: '16px', marginBottom: '32px' }}>
        <div>
          <p className="caption" style={{ textTransform: 'uppercase', letterSpacing: '0.08em', fontWeight: 700, color: 'var(--accent)', marginBottom: '6px' }}>
            Interactive Curriculum
          </p>
          <h1 style={{ marginBottom: '8px' }}>
            <span className="accent-underline">The Swami Chakra</span>
          </h1>
          <p style={{ color: 'var(--muted)', margin: 0, fontSize: '1.05rem' }}>
            Eight overlapping spheres of character. Tap any petal to explore Swami Chakra.
          </p>
        </div>

        {/* View toggle button */}
        <div style={{ display: 'flex', gap: '4px', backgroundColor: 'var(--surface)', padding: '4px', borderRadius: '9999px', border: '1px solid var(--line)' }}>
          <button
            type="button"
            className={`btn btn-sm ${viewMode === 'wheel' ? 'btn-primary' : 'btn-secondary'}`}
            style={{ border: 'none' }}
            onClick={() => setViewMode('wheel')}
          >
            Chakra View
          </button>
          <button
            type="button"
            className={`btn btn-sm ${viewMode === 'list' ? 'btn-primary' : 'btn-secondary'}`}
            style={{ border: 'none' }}
            onClick={() => setViewMode('list')}
          >
            List View
          </button>
        </div>
      </div>

      {/* Main View Area */}
      <div style={{ marginBottom: '48px', display: 'flex', justifyContent: 'center' }}>
        {viewMode === 'wheel' ? (
          <IkigaiWheel lessons={lessons} />
        ) : (
          <LessonListView lessons={lessons} />
        )}
      </div>

      {/* Start Where It Hurts - Chips Strip */}
      <section style={{ borderTop: '1px solid var(--line)', paddingTop: '32px' }}>
        <h3 style={{ fontSize: '1.125rem', marginBottom: '16px' }}>
          Start Where It Hurts:
        </h3>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px' }}>
          {lessons.map((lesson) => (
            <Chip
              key={lesson.id}
              label={`"${lesson.painPoint}"`}
              onClick={() => navigate(`/journey/${lesson.id}`)}
            />
          ))}
        </div>
      </section>
    </main>
  );
};
