import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Lesson } from '../types';
import { getDone } from '../lib/progress';

interface PetalSheetProps {
  lesson: Lesson | null;
  onClose: () => void;
}

export const PetalSheet: React.FC<PetalSheetProps> = ({ lesson, onClose }) => {
  const navigate = useNavigate();

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [onClose]);

  if (!lesson) return null;

  const completedEpisodes = getDone(lesson.id);

  return (
    <div className="petal-sheet-backdrop" onClick={onClose} role="dialog" aria-modal="true" aria-labelledby="sheet-title">
      <div className="petal-sheet" onClick={(e) => e.stopPropagation()}>
        <button
          type="button"
          className="petal-sheet-close"
          onClick={onClose}
          aria-label="Close dialog"
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
            <line x1="18" y1="6" x2="6" y2="18" />
            <line x1="6" y1="6" x2="18" y2="18" />
          </svg>
        </button>

        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
          <span className="caption" style={{ fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Lesson {lesson.id} of 8
          </span>
          <span className="caption">•</span>
          <span className="caption">
            {completedEpisodes.length}/6 completed
          </span>
        </div>

        <h2 id="sheet-title" style={{ marginBottom: '8px' }}>{lesson.title}</h2>

        <p style={{ fontStyle: 'italic', color: 'var(--muted)', marginBottom: '16px', fontSize: '1.05rem' }}>
          "{lesson.painPoint}"
        </p>

        <p style={{ color: 'var(--ink)', marginBottom: '24px', lineHeight: 1.5 }}>
          {lesson.summary}
        </p>

        <div style={{ display: 'flex', gap: '12px' }}>
          <button
            type="button"
            className="btn btn-primary"
            style={{ flex: 1 }}
            onClick={() => {
              onClose();
              navigate(`/journey/${lesson.id}`);
            }}
          >
            {completedEpisodes.length > 0 ? 'Continue Lesson →' : 'Begin Lesson →'}
          </button>
          <button
            type="button"
            className="btn btn-secondary"
            onClick={onClose}
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
