import React from 'react';
import { Quote } from '../types';
import { ALLOW_UNVERIFIED_IN_DEV } from '../config';

interface QuoteCardProps {
  quote: Quote;
  className?: string;
}

export const QuoteCard: React.FC<QuoteCardProps> = ({ quote, className = '' }) => {
  // Split into multiple lines if containing newlines or comma/arrow breaks so source fits completely in 9:16
  const sourceLines = React.useMemo(() => {
    if (!quote.source) return [];
    if (quote.source.includes('\n')) {
      return quote.source.split('\n').map(s => s.trim()).filter(Boolean);
    }
    const parts = quote.source.split(/(?:,\s*(?=Advaita Ashrama)|,\s*(?=Complete Works, Vol\.)|(?:\s*→\s*))/i);
    if (parts.length > 1) {
      return parts.map(p => p.trim()).filter(Boolean);
    }
    if (quote.source.length > 40) {
      return quote.source.split(/,\s+/).map(p => p.trim()).filter(Boolean);
    }
    return [quote.source];
  }, [quote.source]);

  return (
    <figure className={`quote-card ${className}`}>
      <div className="quote-ornament" aria-hidden="true">“</div>
      <blockquote className="quote-text">
        "{quote.text}"
      </blockquote>
      <figcaption className="quote-footer">
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', width: '100%', marginBottom: '2px' }}>
          <span style={{ fontSize: '0.68rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: 'var(--accent)', fontWeight: 700 }}>
            Original Source
          </span>
          {quote.verified ? (
            <span className="quote-verified-chip" style={{ fontSize: '0.68rem', padding: '2px 8px' }}>
              <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                <polyline points="20 6 9 17 4 12" />
              </svg>
              Verified
            </span>
          ) : (
            ALLOW_UNVERIFIED_IN_DEV && (
              <span className="quote-unverified-chip" style={{ fontSize: '0.68rem', padding: '2px 8px' }}>
                ⚠ UNVERIFIED (dev)
              </span>
            )
          )}
        </div>

        <a
          href={quote.sourceUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="quote-source"
          title="View source in Complete Works of Swami Vivekananda"
        >
          <div className="quote-source-lines">
            {sourceLines.map((line, idx) => (
              <span key={idx} className="quote-source-line">{line}</span>
            ))}
          </div>
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" style={{ flexShrink: 0, marginTop: '2px' }}>
            <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
            <polyline points="15 3 21 3 21 9" />
            <line x1="10" y1="14" x2="21" y2="3" />
          </svg>
        </a>
      </figcaption>
    </figure>
  );
};
