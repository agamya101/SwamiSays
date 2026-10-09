import React from 'react';
import { AiLabel } from '../components/AiLabel';

export const About: React.FC = () => {
  return (
    <main className="container" style={{ paddingTop: '32px', paddingBottom: '60px', maxWidth: '780px' }}>
      <div style={{ marginBottom: '32px' }}>
        <p className="caption" style={{ textTransform: 'uppercase', letterSpacing: '0.08em', fontWeight: 700, color: 'var(--accent)', marginBottom: '8px' }}>
          Methodology & Transparency
        </p>
        <h1 style={{ marginBottom: '16px' }}>
          <span className="accent-underline">About SwamiSays</span>
        </h1>
        <p style={{ fontSize: '1.2rem', color: 'var(--muted)', margin: 0 }}>
          Bridging Swami Vivekananda's unvarnished fire to modern Gen Z & Alpha challenges with strict factual integrity.
        </p>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '32px' }}>
        {/* Section 1: What this is */}
        <section className="card">
          <h2 style={{ fontSize: '1.35rem', marginBottom: '12px' }}>1. What This Is</h2>
          <p style={{ color: 'var(--ink)', lineHeight: 1.6, margin: 0 }}>
            SwamiSays is a digital sanctuary and teaching-to-reel generator. It offers two intuitive doorways:
            a structured 8-lesson <strong>Journey</strong> (visualized as the 8-petal <strong>Swami Chakra</strong>) and an on-demand <strong>SOS</strong> doorway that synthesizes authentic 45-second micro-reels directly mapped to your present struggles—from exam dread to career paralysis.
          </p>
        </section>

        {/* Section 2: How quotes are verified */}
        <section className="card">
          <h2 style={{ fontSize: '1.35rem', marginBottom: '12px' }}>2. How Quotes Are Verified (Zero Invention)</h2>
          <p style={{ color: 'var(--ink)', lineHeight: 1.6, marginBottom: '16px' }}>
            We strictly enforce the primary principle: <strong>Never invent or misattribute quotes</strong>. The internet is flooded with inspirational quotes falsely attributed to Swami Vivekananda. Every single quotation rendered in SwamiSays is cataloged in an audited library (<code style={{ color: 'var(--accent)' }}>quotes.json</code>) with exact volume and page citations from the <em>Complete Works of Swami Vivekananda</em> published by Advaita Ashrama (Belur Math).
          </p>
          <div style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', padding: '6px 14px', borderRadius: '9999px', backgroundColor: 'var(--accent-soft)', border: '1px solid var(--line)' }}>
            <span style={{ color: 'var(--accent)', fontWeight: 700 }}>✓ Verified Source</span>
            <span className="caption">• All cards link to full canonical transcripts</span>
          </div>
        </section>

        {/* Section 3: What is AI-written */}
        <section className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px', flexWrap: 'wrap', gap: '8px' }}>
            <h2 style={{ fontSize: '1.35rem', margin: 0 }}>3. What is AI-Written</h2>
            <AiLabel />
          </div>
          <p style={{ color: 'var(--ink)', lineHeight: 1.6, marginBottom: '12px' }}>
            The AI engine is restricted strictly to generating contemporary scenario narratives, relatable teenage analogies, and structured 2-minute actionable habits.
          </p>
          <p style={{ color: 'var(--ink)', lineHeight: 1.6, margin: 0 }}>
            The core teachings and quotations are <strong>never written or modified by the AI</strong>; they are injected immutable directly from the verified database.
          </p>
        </section>

        {/* Section 4: Sources & References */}
        <section className="card">
          <h2 style={{ fontSize: '1.35rem', marginBottom: '12px' }}>4. Canonical Sources</h2>
          <ul style={{ paddingLeft: '20px', color: 'var(--ink)', lineHeight: 1.7, margin: 0 }}>
            <li>
              <a href="https://belurmath.org" target="_blank" rel="noopener noreferrer" style={{ color: 'var(--accent)', fontWeight: 600 }}>
                Belur Math Official Headquarters (Ramakrishna Math and Ramakrishna Mission)
              </a>
            </li>
            <li>
              <a href="https://www.ramakrishnavivekananda.info/vivekananda/complete_works.htm" target="_blank" rel="noopener noreferrer" style={{ color: 'var(--accent)', fontWeight: 600 }}>
                Complete Works of Swami Vivekananda (Vols 1–9), Advaita Ashrama
              </a>
            </li>
            <li>
              <a href="https://advaitaashrama.org" target="_blank" rel="noopener noreferrer" style={{ color: 'var(--accent)', fontWeight: 600 }}>
                Advaita Ashrama Publication Center, Mayavati / Kolkata
              </a>
            </li>
          </ul>
        </section>

        {/* Section 5: Limitations & Safety */}
        <section className="card">
          <h2 style={{ fontSize: '1.35rem', marginBottom: '12px' }}>5. Limitations & Safety Disclaimer</h2>
          <p style={{ color: 'var(--ink)', lineHeight: 1.6, margin: 0 }}>
            SwamiSays is an educational and reflective tool. It is not a substitute for clinical psychiatric care or emergency intervention. If someone is experiencing severe distress or crisis thoughts, our real-time safety layer intercepts the prompt and provides verified 24/7 mental health emergency helplines including Tele-MANAS (14416) and KIRAN (1800-599-0019).
          </p>
        </section>
      </div>
    </main>
  );
};
