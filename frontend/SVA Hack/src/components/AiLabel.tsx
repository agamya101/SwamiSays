import React from 'react';

export const AiLabel: React.FC<{ className?: string }> = ({ className = '' }) => {
  return (
    <span className={`ai-label ${className}`} title="AI-written story / interpretation — not Swami Vivekananda's words">
      <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
        <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83" />
      </svg>
      <span>AI-written · not Swami Vivekananda's words</span>
    </span>
  );
};
