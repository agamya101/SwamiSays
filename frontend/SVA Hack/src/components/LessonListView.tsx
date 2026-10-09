import React from 'react';
import { Link } from 'react-router-dom';
import { Lesson } from '../types';
import { getDone } from '../lib/progress';

interface LessonListViewProps {
  lessons: Lesson[];
}

export const LessonListView: React.FC<LessonListViewProps> = ({ lessons }) => {
  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '20px', width: '100%' }}>
      {lessons.map((lesson) => {
        const done = getDone(lesson.id);
        const percent = Math.round((done.length / 6) * 100);

        return (
          <article key={lesson.id} className="card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                <span className="caption" style={{ fontWeight: 700, textTransform: 'uppercase' }}>
                  Lesson {lesson.id}
                </span>
                <span className="caption" style={{ color: 'var(--accent)', fontWeight: 600 }}>
                  {done.length}/6 done ({percent}%)
                </span>
              </div>

              <h3 style={{ marginBottom: '6px' }}>{lesson.title}</h3>

              <p style={{ fontStyle: 'italic', color: 'var(--muted)', fontSize: '0.9375rem', marginBottom: '12px' }}>
                "{lesson.painPoint}"
              </p>

              <p style={{ fontSize: '0.875rem', color: 'var(--ink)', marginBottom: '18px', lineHeight: 1.45 }}>
                {lesson.summary}
              </p>
            </div>

            <Link
              to={`/journey/${lesson.id}`}
              className="btn btn-secondary btn-sm"
              style={{ width: '100%' }}
            >
              {done.length > 0 ? 'Continue Lesson →' : 'Begin Lesson →'}
            </Link>
          </article>
        );
      })}
    </div>
  );
};
