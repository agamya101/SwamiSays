import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Quote } from '../types';
import { getDailyQuote } from '../lib/api';
import { QuoteCard } from '../components/QuoteCard';
import { MandalaWatermark } from '../components/MandalaWatermark';

export const Home: React.FC = () => {
  const [dailyQuote, setDailyQuote] = useState<Quote | null>(null);

  useEffect(() => {
    getDailyQuote().then(setDailyQuote);
  }, []);

  return (
    <main className="container" style={{ paddingTop: '40px', paddingBottom: '60px', position: 'relative' }}>
      {/* Hero section */}
      <section style={{ position: 'relative', textAlign: 'center', marginBottom: '56px', paddingTop: '20px' }}>
        <div style={{ position: 'absolute', top: '-40px', left: '50%', transform: 'translateX(-50%)' }}>
          <MandalaWatermark size={380} />
        </div>

        <div style={{ position: 'relative', zIndex: 2 }}>
          <p className="caption" style={{ textTransform: 'uppercase', letterSpacing: '0.12em', fontWeight: 700, marginBottom: '12px', color: 'var(--accent)' }}>
            Timeless Courage for Gen Z & Alpha
          </p>
          <h1 style={{ marginBottom: '16px' }}>
            <span className="accent-underline">Arise. Awake.</span>
          </h1>
          <p style={{ margin: '0 auto', fontSize: '1.2rem', color: 'var(--muted)', maxWidth: '44ch' }}>
            Swami Vivekananda, for the problems you actually have.
          </p>
        </div>
      </section>

      {/* Two Doors: Journey and SOS */}
      <section style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '24px', marginBottom: '56px' }}>
        {/* Door 1: Journey */}
        <Link to="/journey" style={{ textDecoration: 'none', color: 'inherit' }}>
          <div className="card" style={{ height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'space-between', cursor: 'pointer' }}>
            <div>
              <div style={{ display: 'inline-flex', padding: '10px', borderRadius: '12px', backgroundColor: 'var(--accent-soft)', color: 'var(--accent)', marginBottom: '16px' }}>
                <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                  <circle cx="12" cy="12" r="10" />
                  <polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76" />
                </svg>
              </div>
              <h2 style={{ fontSize: '1.75rem', marginBottom: '8px' }}>The Journey</h2>
              <p style={{ color: 'var(--muted)', marginBottom: '16px' }}>
                A calm, structured series through the 8 essential Life Lessons.
              </p>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', paddingTop: '16px', borderTop: '1px solid var(--line)' }}>
              <span className="caption" style={{ fontWeight: 600 }}>8 lessons · 6 episodes each</span>
              <span style={{ color: 'var(--accent)', fontWeight: 700, fontSize: '0.9375rem' }}>Explore Chakra →</span>
            </div>
          </div>
        </Link>

        {/* Door 2: SOS */}
        <Link to="/sos" style={{ textDecoration: 'none', color: 'inherit' }}>
          <div className="card" style={{ height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'space-between', cursor: 'pointer', border: '1.5px solid var(--accent)' }}>
            <div>
              <div style={{ display: 'inline-flex', padding: '10px', borderRadius: '12px', backgroundColor: 'var(--accent)', color: 'var(--on-accent)', marginBottom: '16px' }}>
                <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                  <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
                </svg>
              </div>
              <h2 style={{ fontSize: '1.75rem', marginBottom: '8px' }}>Emergency SOS</h2>
              <p style={{ color: 'var(--muted)', marginBottom: '16px' }}>
                Stuck right now? Type what is hurting and receive a 45-second reel + the closest lesson.
              </p>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', paddingTop: '16px', borderTop: '1px solid var(--line)' }}>
              <span className="caption" style={{ fontWeight: 600 }}>Under 60 seconds · Multi-lingual</span>
              <span style={{ color: 'var(--accent)', fontWeight: 700, fontSize: '0.9375rem' }}>Get Instant Reel →</span>
            </div>
          </div>
        </Link>
      </section>

      {/* Daily Verified Quote */}
      <section style={{ marginBottom: '56px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
          <span className="caption" style={{ textTransform: 'uppercase', letterSpacing: '0.08em', fontWeight: 700 }}>
            Daily Verified Quote
          </span>
          <span className="caption">•</span>
          <span className="caption">Rotates daily from Complete Works</span>
        </div>
        {dailyQuote && <QuoteCard quote={dailyQuote} />}
      </section>

      {/* Footer */}
      <footer style={{ borderTop: '1px solid var(--line)', paddingTop: '28px', display: 'flex', flexWrap: 'wrap', justifyContent: 'space-between', alignItems: 'center', gap: '16px' }}>
        <p className="caption" style={{ margin: 0 }}>
          SwamiSays is an educational non-commercial tribute. Quotes verified via Belur Math & Advaita Ashrama Complete Works.
        </p>
        <div style={{ display: 'flex', gap: '16px' }}>
          <Link to="/about" className="caption" style={{ textDecoration: 'none', color: 'var(--accent)', fontWeight: 600 }}>
            Method & Transparency →
          </Link>
        </div>
      </footer>
    </main>
  );
};
