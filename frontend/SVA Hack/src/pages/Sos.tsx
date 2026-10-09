import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { SupportedLang, Quote } from '../types';
import { generateReel, getDailyQuote } from '../lib/api';
import { checkCrisis, CRISIS_HELPLINES } from '../lib/safety';
import { SUPPORTED_LANGS } from '../lib/i18n';
import { Chip } from '../components/Chip';
import { QuoteCard } from '../components/QuoteCard';
import { MandalaWatermark } from '../components/MandalaWatermark';

const QUICK_CHIPS = [
  'Exam fear',
  "Can't focus",
  'Feeling like a failure',
  'Comparing myself',
  'Anxious & overwhelmed',
  'Lost about what to do with my life'
];

const GENERATION_STEPS = [
  'Understanding you...',
  'Finding a verified teaching...',
  'Writing the story...',
  'Building your reel...'
];

export const Sos: React.FC = () => {
  const navigate = useNavigate();

  const [prompt, setPrompt] = useState('');
  const [name, setName] = useState('');
  const [age, setAge] = useState<string>('19');
  const [profession, setProfession] = useState('Student');
  const [lang, setLang] = useState<SupportedLang>('en');
  const [subtitleColor, setSubtitleColor] = useState<string>('yellow');
  const [voiceId, setVoiceId] = useState<string>('en-IN-PrabhatNeural');
  const [musicTrack, setMusicTrack] = useState<string>('motivational_ambient.mp3');
  const [isCrisis, setIsCrisis] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [genStepIdx, setGenStepIdx] = useState(0);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [dailyQuote, setDailyQuote] = useState<Quote | null>(null);

  useEffect(() => {
    getDailyQuote().then(setDailyQuote);
  }, []);

  // Monitor text for crisis keywords in real-time
  const handleTextChange = (val: string) => {
    setPrompt(val);
    if (checkCrisis(val)) {
      setIsCrisis(true);
    } else {
      setIsCrisis(false);
    }
  };

  const handleChipClick = (text: string) => {
    handleTextChange(text);
  };

  // Step advancement timer while generating
  useEffect(() => {
    let interval: number;
    if (isGenerating) {
      interval = window.setInterval(() => {
        setGenStepIdx((prev) => (prev < GENERATION_STEPS.length - 1 ? prev + 1 : prev));
      }, 1100);
    }
    return () => clearInterval(interval);
  }, [isGenerating]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (prompt.trim().length < 10) return;

    if (checkCrisis(prompt)) {
      setIsCrisis(true);
      return;
    }

    setIsGenerating(true);
    setErrorMsg(null);
    setGenStepIdx(0);

    try {
      const reelData = await generateReel({
        prompt,
        lang,
        name: name.trim() || undefined,
        age: age ? parseInt(age, 10) : undefined,
        profession: profession || undefined,
        subtitle_color: subtitleColor,
        voice_id: voiceId,
        music_track: musicTrack,
        render_video: true
      });
      // Navigate to result screen with generated data
      navigate('/sos/result', { state: { reelData, lang, prompt, name, age, profession } });
    } catch (err: any) {
      console.error(err);
      setErrorMsg('Could not create your reel right now. Please try again.');
      setIsGenerating(false);
    }
  };

  return (
    <main className="container" style={{ paddingTop: '32px', paddingBottom: '60px', position: 'relative' }}>
      <div style={{ position: 'absolute', top: 0, right: '10%', opacity: 0.05 }}>
        <MandalaWatermark size={360} />
      </div>

      <div style={{ maxWidth: '640px', margin: '0 auto', position: 'relative', zIndex: 2 }}>
        {/* Header */}
        <div style={{ textAlign: 'center', marginBottom: '32px' }}>
          <span className="caption" style={{ textTransform: 'uppercase', letterSpacing: '0.1em', fontWeight: 700, color: 'var(--accent)' }}>
            Immediate Perspective
          </span>
          <h1 style={{ marginTop: '8px', marginBottom: '12px' }}>
            <span className="accent-underline">What's going on?</span>
          </h1>
          <p style={{ color: 'var(--muted)', fontSize: '1.05rem', margin: 0 }}>
            Type what feels heavy right now. We'll generate a 45-second reel rooted in verified teachings.
          </p>
        </div>

        {/* Crisis Safety Card */}
        {isCrisis ? (
          <div
            className="card"
            style={{
              borderColor: 'var(--accent)',
              backgroundColor: 'var(--surface)',
              padding: '32px',
              marginBottom: '32px',
              animation: 'fadeIn 0.2s ease-out'
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', color: 'var(--accent)', marginBottom: '16px' }}>
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                <circle cx="12" cy="12" r="10" />
                <line x1="12" y1="8" x2="12" y2="12" />
                <line x1="12" y1="16" x2="12.01" y2="16" />
              </svg>
              <h2 style={{ fontSize: '1.4rem', margin: 0 }}>You matter. Please talk to someone now.</h2>
            </div>

            <p style={{ fontSize: '1.05rem', color: 'var(--ink)', marginBottom: '24px', lineHeight: 1.5 }}>
              If you or someone you know is going through a difficult time, please know that you are not alone. Kind, free, and confidential help is available right now:
            </p>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', marginBottom: '24px' }}>
              {CRISIS_HELPLINES.map((h) => (
                <div key={h.name} style={{ padding: '16px', borderRadius: 'var(--radius)', backgroundColor: 'var(--accent-soft)', border: '1px solid var(--line)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                    <strong style={{ color: 'var(--ink)' }}>{h.name}</strong>
                    <span className="caption" style={{ fontWeight: 600 }}>{h.hours}</span>
                  </div>
                  <a
                    href={`tel:${h.number.split('/')[0].trim()}`}
                    style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--accent)', textDecoration: 'none', display: 'block', margin: '4px 0' }}
                  >
                    📞 {h.number}
                  </a>
                  <p className="caption" style={{ margin: 0 }}>{h.description}</p>
                </div>
              ))}
            </div>

            <button
              type="button"
              className="btn btn-secondary"
              onClick={() => {
                setPrompt('');
                setIsCrisis(false);
              }}
            >
              Reset Input
            </button>
          </div>
        ) : isGenerating ? (
          /* Screen 2: Animated Generating state */
          <div
            className="card"
            style={{
              padding: '48px 24px',
              textAlign: 'center',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              gap: '24px',
              marginBottom: '32px'
            }}
          >
            <div style={{ position: 'relative' }}>
              <MandalaWatermark size={180} animate={true} />
            </div>

            <div>
              <h2 style={{ fontSize: '1.5rem', marginBottom: '8px' }}>
                {GENERATION_STEPS[genStepIdx]}
              </h2>
              <p className="caption" style={{ margin: 0 }}>
                Synthesizing authentic wisdom with a 45-second micro-reel...
              </p>
            </div>

            <div style={{ display: 'flex', gap: '8px', marginTop: '12px' }}>
              {GENERATION_STEPS.map((_, idx) => (
                <div
                  key={idx}
                  style={{
                    width: '10px',
                    height: '10px',
                    borderRadius: '50%',
                    backgroundColor: idx <= genStepIdx ? 'var(--accent)' : 'var(--line)',
                    transition: 'background-color 0.3s ease'
                  }}
                />
              ))}
            </div>
          </div>
        ) : (
          /* Screen 1: Input form */
          <form onSubmit={handleSubmit} className="card" style={{ padding: '28px', marginBottom: '40px' }}>
            {/* User Profile Context */}
            <div style={{ marginBottom: '24px', paddingBottom: '20px', borderBottom: '1px solid var(--line)' }}>
              <span className="caption" style={{ textTransform: 'uppercase', letterSpacing: '0.08em', fontWeight: 700, color: 'var(--accent)', display: 'block', marginBottom: '12px' }}>
                About You (Personalizes Your Reel)
              </span>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: '12px', marginBottom: '14px' }}>
                <div>
                  <label htmlFor="user-name" className="caption" style={{ fontWeight: 600, display: 'block', marginBottom: '6px' }}>
                    First Name:
                  </label>
                  <input
                    id="user-name"
                    type="text"
                    placeholder="e.g. Aarav"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    style={{
                      width: '100%',
                      padding: '10px 12px',
                      borderRadius: 'var(--radius)',
                      border: '1px solid var(--line)',
                      backgroundColor: 'var(--bg)',
                      color: 'var(--ink)',
                      fontSize: '0.9375rem'
                    }}
                  />
                </div>
                <div>
                  <label htmlFor="user-age" className="caption" style={{ fontWeight: 600, display: 'block', marginBottom: '6px' }}>
                    Age:
                  </label>
                  <input
                    id="user-age"
                    type="number"
                    min="10"
                    max="99"
                    placeholder="19"
                    value={age}
                    onChange={(e) => setAge(e.target.value)}
                    style={{
                      width: '100%',
                      padding: '10px 12px',
                      borderRadius: 'var(--radius)',
                      border: '1px solid var(--line)',
                      backgroundColor: 'var(--bg)',
                      color: 'var(--ink)',
                      fontSize: '0.9375rem'
                    }}
                  />
                </div>
              </div>

              <div>
                <span className="caption" style={{ fontWeight: 600, display: 'block', marginBottom: '6px' }}>
                  What do you do right now?
                </span>
                <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                  {['Student', 'Corporate', 'Creative', 'Preparing for Exams', 'Self-Employed'].map((p) => (
                    <button
                      key={p}
                      type="button"
                      onClick={() => setProfession(p)}
                      className={`btn btn-sm ${profession === p ? 'btn-primary' : 'btn-secondary'}`}
                      style={{ fontSize: '0.8rem', padding: '6px 12px' }}
                    >
                      {p}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Quick chips */}
            <div style={{ marginBottom: '20px' }}>
              <span className="caption" style={{ fontWeight: 600, display: 'block', marginBottom: '10px' }}>
                Quick Prompts:
              </span>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                {QUICK_CHIPS.map((chipText) => (
                  <Chip
                    key={chipText}
                    label={chipText}
                    onClick={() => handleChipClick(chipText)}
                  />
                ))}
              </div>
            </div>

            {/* Textarea */}
            <div style={{ marginBottom: '20px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                <label htmlFor="sos-input" style={{ fontWeight: 600, fontSize: '0.9375rem' }}>
                  Your situation or feeling:
                </label>
                <span className="caption">
                  {prompt.length}/400 chars (min 10)
                </span>
              </div>
              <textarea
                id="sos-input"
                rows={4}
                maxLength={400}
                placeholder="e.g. I got a bad score on my test and everyone in my family thinks I'm falling behind..."
                value={prompt}
                onChange={(e) => handleTextChange(e.target.value)}
                style={{
                  width: '100%',
                  padding: '14px',
                  borderRadius: 'var(--radius)',
                  border: '1px solid var(--line)',
                  backgroundColor: 'var(--bg)',
                  color: 'var(--ink)',
                  fontFamily: 'var(--font-body)',
                  fontSize: '1rem',
                  lineHeight: 1.5,
                  resize: 'vertical'
                }}
              />
            </div>

            {/* Language Selector */}
            <div style={{ marginBottom: '24px' }}>
              <span className="caption" style={{ fontWeight: 600, display: 'block', marginBottom: '8px' }}>
                Reel Language:
              </span>
              <div style={{ display: 'flex', gap: '8px' }}>
                {SUPPORTED_LANGS.map((item) => (
                  <button
                    key={item.code}
                    type="button"
                    onClick={() => {
                      setLang(item.code);
                      if (item.code === 'hi') {
                        setVoiceId('hi-IN-MadhurNeural');
                      }
                    }}
                    className={`btn btn-sm ${lang === item.code ? 'btn-primary' : 'btn-secondary'}`}
                  >
                    {item.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Reel Customization (Subtitles, Voice, Background Score) */}
            <div
              style={{
                marginBottom: '24px',
                padding: '16px',
                borderRadius: 'var(--radius)',
                backgroundColor: 'var(--accent-soft)',
                border: '1px solid var(--line)'
              }}
            >
              <span
                className="caption"
                style={{
                  textTransform: 'uppercase',
                  letterSpacing: '0.08em',
                  fontWeight: 700,
                  color: 'var(--accent)',
                  display: 'block',
                  marginBottom: '12px'
                }}
              >
                Reel Audio & Subtitle Styling
              </span>
              <div
                style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))',
                  gap: '12px'
                }}
              >
                {/* Subtitle Style Dropdown */}
                <div>
                  <label
                    htmlFor="sos-subtitle"
                    className="caption"
                    style={{ fontWeight: 600, display: 'block', marginBottom: '6px' }}
                  >
                    Subtitle Style
                  </label>
                  <select
                    id="sos-subtitle"
                    value={subtitleColor}
                    onChange={(e) => setSubtitleColor(e.target.value)}
                    style={{
                      width: '100%',
                      padding: '9px 12px',
                      borderRadius: 'var(--radius)',
                      border: '1px solid var(--line)',
                      backgroundColor: 'var(--bg)',
                      color: 'var(--ink)',
                      fontSize: '0.85rem'
                    }}
                  >
                    <option value="yellow">Yellow (Viral / TikTok)</option>
                    <option value="gold">Gold (Sacred / Classical)</option>
                    <option value="saffron">Saffron (Kesari)</option>
                    <option value="white">Clean White</option>
                    <option value="cyan">Cyber Cyan</option>
                  </select>
                </div>

                {/* Narrator Voice Dropdown */}
                <div>
                  <label
                    htmlFor="sos-voice"
                    className="caption"
                    style={{ fontWeight: 600, display: 'block', marginBottom: '6px' }}
                  >
                    Narrator Voice
                  </label>
                  <select
                    id="sos-voice"
                    value={voiceId}
                    onChange={(e) => setVoiceId(e.target.value)}
                    style={{
                      width: '100%',
                      padding: '9px 12px',
                      borderRadius: 'var(--radius)',
                      border: '1px solid var(--line)',
                      backgroundColor: 'var(--bg)',
                      color: 'var(--ink)',
                      fontSize: '0.85rem'
                    }}
                  >
                    <option value="en-IN-PrabhatNeural">Prabhat (Indian Male - Clear)</option>
                    <option value="hi-IN-MadhurNeural">Madhur (Hindi/Indian Male)</option>
                    <option value="en-IN-SwaraNeural">Swara (Indian Female)</option>
                    <option value="en-US-ChristopherNeural">Christopher (US Male - Deep)</option>
                    <option value="en-US-JennyNeural">Jenny (US Female - Warm)</option>
                    <option value="en-GB-RyanNeural">Ryan (UK Male - Cinematic)</option>
                  </select>
                </div>

                {/* Background Score Dropdown */}
                <div>
                  <label
                    htmlFor="sos-music"
                    className="caption"
                    style={{ fontWeight: 600, display: 'block', marginBottom: '6px' }}
                  >
                    Background Score
                  </label>
                  <select
                    id="sos-music"
                    value={musicTrack}
                    onChange={(e) => setMusicTrack(e.target.value)}
                    style={{
                      width: '100%',
                      padding: '9px 12px',
                      borderRadius: 'var(--radius)',
                      border: '1px solid var(--line)',
                      backgroundColor: 'var(--bg)',
                      color: 'var(--ink)',
                      fontSize: '0.85rem'
                    }}
                  >
                    <option value="motivational_ambient.mp3">Motivational Ambient (Gentle)</option>
                    <option value="motivational_inspiring.mp3">Motivational Inspiring (Uplifting)</option>
                    <option value="motivational_cinematic.mp3">Cinematic Strings (Dramatic)</option>
                    <option value="random">Random Track</option>
                  </select>
                </div>
              </div>
            </div>

            {errorMsg && (
              <div style={{ padding: '12px', borderRadius: '8px', backgroundColor: 'var(--accent-soft)', color: 'var(--ink)', marginBottom: '16px', fontSize: '0.875rem' }}>
                {errorMsg}
              </div>
            )}

            {/* Submit button */}
            <button
              type="submit"
              disabled={prompt.trim().length < 10}
              className="btn btn-primary"
              style={{
                width: '100%',
                opacity: prompt.trim().length < 10 ? 0.5 : 1,
                cursor: prompt.trim().length < 10 ? 'not-allowed' : 'pointer'
              }}
            >
              Make My 45-Second Reel →
            </button>
          </form>
        )}

        {/* How it works 3-step strip */}
        <section style={{ marginBottom: '40px' }}>
          <h3 style={{ fontSize: '1.125rem', marginBottom: '16px', textAlign: 'center' }}>
            How SOS Works
          </h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '16px' }}>
            <div className="card" style={{ padding: '18px', textAlign: 'center' }}>
              <div style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--accent)', marginBottom: '6px' }}>1</div>
              <h4 style={{ fontSize: '0.9375rem', marginBottom: '4px' }}>Match Teaching</h4>
              <p className="caption" style={{ margin: 0 }}>Verified quote library mapped to your exact struggle.</p>
            </div>
            <div className="card" style={{ padding: '18px', textAlign: 'center' }}>
              <div style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--accent)', marginBottom: '6px' }}>2</div>
              <h4 style={{ fontSize: '0.9375rem', marginBottom: '4px' }}>Gen-Z Reel</h4>
              <p className="caption" style={{ margin: 0 }}>Short vertical story with zero preaching or fluff.</p>
            </div>
            <div className="card" style={{ padding: '18px', textAlign: 'center' }}>
              <div style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--accent)', marginBottom: '6px' }}>3</div>
              <h4 style={{ fontSize: '0.9375rem', marginBottom: '4px' }}>Deep Path</h4>
              <p className="caption" style={{ margin: 0 }}>Direct bridge into the 8-lesson Journey for lasting change.</p>
            </div>
          </div>
        </section>

        {/* Daily Quote card filler */}
        {dailyQuote && (
          <section>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
              <span className="caption" style={{ fontWeight: 700, textTransform: 'uppercase' }}>Daily Grounding</span>
            </div>
            <QuoteCard quote={dailyQuote} />
          </section>
        )}
      </div>
    </main>
  );
};
