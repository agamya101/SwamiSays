import React, { useState, useEffect, useRef } from 'react';
import { ThemeName } from '../types';
import { Toast, ToastMessage } from '../components/Toast';

interface ThemeConfig {
  id: ThemeName;
  name: string;
  tagline: string;
  swatches: string[];
  vibe: string;
}

const THEMES: ThemeConfig[] = [
  {
    id: 'kesari',
    name: 'Theme A: Kesari',
    tagline: 'Light caramel + off-white',
    swatches: ['#FBF6EC', '#FFFFFF', '#3B2A1A', '#E08A2E', '#FFF1D6'],
    vibe: 'Warm, airy, sunrise — joyful morning vitality for Gen Z'
  },
  {
    id: 'clay',
    name: 'Theme B: Chai & Clay',
    tagline: 'Brown, dark, grounded',
    swatches: ['#2A1E17', '#38291F', '#F3E6D3', '#C9894F', '#43322A'],
    vibe: 'Contemplative, earthy sanctuary — dark mode for late-night focus'
  },
  {
    id: 'indigo',
    name: 'Theme C: Indigo & Marigold',
    tagline: 'Belur Math official palette',
    swatches: ['#F7F5EF', '#FFFFFF', '#1F2A5C', '#D9A21B', '#ECEEFA'],
    vibe: 'Deep indigo authority with vivid gold accents — authentic & scholastic'
  }
];

const QUICK_JUMPS = [
  { label: 'Home', path: '/' },
  { label: 'Journey', path: '/journey' },
  { label: 'Lesson', path: '/journey/3' },
  { label: 'Episode', path: '/journey/3/1' },
  { label: 'SOS', path: '/sos' },
  { label: 'SOS Result', path: '/sos/result' }
];

export const Compare: React.FC = () => {
  const [deviceMode, setDeviceMode] = useState<'phone' | 'laptop'>('phone');
  const [syncNav, setSyncNav] = useState(true);
  const [toasts, setToasts] = useState<ToastMessage[]>([]);

  const iframeRefs = {
    kesari: useRef<HTMLIFrameElement>(null),
    clay: useRef<HTMLIFrameElement>(null),
    indigo: useRef<HTMLIFrameElement>(null)
  };

  const showToast = (text: string) => {
    const id = String(Date.now());
    setToasts((prev) => [...prev, { id, text }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 4000);
  };

  const handleChooseTheme = (themeId: ThemeName, themeName: string) => {
    localStorage.setItem('theme', themeId);
    document.documentElement.setAttribute('data-theme', themeId);
    showToast(`✓ Selected ${themeName}! Saved to localStorage.`);
  };

  const handleQuickJump = (path: string) => {
    THEMES.forEach((t) => {
      const iframe = iframeRefs[t.id].current;
      if (iframe?.contentWindow) {
        iframe.contentWindow.postMessage({ type: 'ARISE_NAV_GOTO', path }, '*');
      }
    });
  };

  // Listen for sync messages from any iframe
  useEffect(() => {
    const handleMessage = (e: MessageEvent) => {
      if (e.data?.type === 'ARISE_NAV_UPDATE' && syncNav) {
        const sourcePath = e.data.path;
        THEMES.forEach((t) => {
          const iframe = iframeRefs[t.id].current;
          if (iframe && iframe.contentWindow !== e.source) {
            iframe.contentWindow?.postMessage({ type: 'ARISE_NAV_GOTO', path: sourcePath }, '*');
          }
        });
      }
    };
    window.addEventListener('message', handleMessage);
    return () => window.removeEventListener('message', handleMessage);
  }, [syncNav]);

  const isPhone = deviceMode === 'phone';
  const frameWidth = isPhone ? 390 : 1280;
  const frameHeight = isPhone ? 780 : 800;
  // Scaled dimensions for preview container
  const scaleRatio = isPhone ? 0.85 : 0.42;

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#121214', color: '#ECECF1', padding: '24px 16px', fontFamily: "'Inter', sans-serif" }}>
      {/* Top Bar Chrome */}
      <header style={{ maxWidth: '1400px', margin: '0 auto 28px auto', backgroundColor: '#1E1E24', borderRadius: '16px', padding: '16px 24px', border: '1px solid #2E2E38', display: 'flex', flexWrap: 'wrap', alignItems: 'center', justifyContent: 'space-between', gap: '16px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <span style={{ fontSize: '1.25rem', fontWeight: 800, letterSpacing: '-0.02em', color: '#FFFFFF' }}>
              Arise — 3-Theme Live Compare
            </span>
            <span style={{ fontSize: '0.75rem', backgroundColor: '#E08A2E', color: '#FFFFFF', padding: '2px 8px', borderRadius: '9999px', fontWeight: 700 }}>
              Live Interactive
            </span>
          </div>
          <p style={{ margin: '4px 0 0 0', fontSize: '0.85rem', color: '#9E9EA8' }}>
            Compare Kesari, Chai & Clay, and Indigo & Marigold running live side-by-side.
          </p>
        </div>

        {/* Controls: Device toggle + Sync toggle */}
        <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', gap: '16px' }}>
          {/* Device Toggle */}
          <div style={{ display: 'flex', backgroundColor: '#121214', borderRadius: '9999px', padding: '3px', border: '1px solid #2E2E38' }}>
            <button
              type="button"
              onClick={() => setDeviceMode('phone')}
              style={{
                backgroundColor: isPhone ? '#E08A2E' : 'transparent',
                color: isPhone ? '#FFFFFF' : '#9E9EA8',
                border: 'none',
                borderRadius: '9999px',
                padding: '6px 14px',
                fontSize: '0.8125rem',
                fontWeight: 600,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '6px'
              }}
            >
              <span>📱</span> Phone (390×780)
            </button>
            <button
              type="button"
              onClick={() => setDeviceMode('laptop')}
              style={{
                backgroundColor: !isPhone ? '#E08A2E' : 'transparent',
                color: !isPhone ? '#FFFFFF' : '#9E9EA8',
                border: 'none',
                borderRadius: '9999px',
                padding: '6px 14px',
                fontSize: '0.8125rem',
                fontWeight: 600,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '6px'
              }}
            >
              <span>💻</span> Laptop (1280×800)
            </button>
          </div>

          {/* Sync Navigation Toggle */}
          <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer', fontSize: '0.85rem', color: '#D0D0DA', fontWeight: 500, userSelect: 'none' }}>
            <input
              type="checkbox"
              checked={syncNav}
              onChange={(e) => setSyncNav(e.target.checked)}
              style={{ accentColor: '#E08A2E', width: '16px', height: '16px', cursor: 'pointer' }}
            />
            <span>Sync navigation across all 3</span>
          </label>
        </div>
      </header>

      {/* Quick-Jump Bar */}
      <div style={{ maxWidth: '1400px', margin: '0 auto 28px auto', display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: '8px', padding: '0 4px' }}>
        <span style={{ fontSize: '0.8125rem', color: '#9E9EA8', fontWeight: 600, marginRight: '4px' }}>
          Quick Jump All Frames:
        </span>
        {QUICK_JUMPS.map((q) => (
          <button
            key={q.label}
            type="button"
            onClick={() => handleQuickJump(q.path)}
            style={{
              backgroundColor: '#1E1E24',
              color: '#ECECF1',
              border: '1px solid #2E2E38',
              borderRadius: '9999px',
              padding: '5px 12px',
              fontSize: '0.8125rem',
              fontWeight: 500,
              cursor: 'pointer',
              transition: 'all 0.15s ease'
            }}
            onMouseEnter={(e) => (e.currentTarget.style.borderColor = '#E08A2E')}
            onMouseLeave={(e) => (e.currentTarget.style.borderColor = '#2E2E38')}
          >
            {q.label}
          </button>
        ))}
      </div>

      {/* 3 Themes Grid / Carousel */}
      <main
        style={{
          maxWidth: '1400px',
          margin: '0 auto',
          display: 'grid',
          gridTemplateColumns: isPhone ? 'repeat(auto-fit, minmax(350px, 1fr))' : '1fr',
          gap: '32px',
          alignItems: 'start',
          overflowX: 'auto'
        }}
      >
        {THEMES.map((theme) => (
          <div
            key={theme.id}
            style={{
              backgroundColor: '#1E1E24',
              borderRadius: '20px',
              border: '1px solid #2E2E38',
              padding: '20px',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              boxShadow: '0 8px 32px rgba(0, 0, 0, 0.4)'
            }}
          >
            {/* Frame Header */}
            <div style={{ width: '100%', marginBottom: '16px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                <h2 style={{ margin: 0, fontSize: '1.15rem', color: '#FFFFFF', fontWeight: 700 }}>
                  {theme.name}
                </h2>
                <button
                  type="button"
                  onClick={() => handleChooseTheme(theme.id, theme.name)}
                  style={{
                    backgroundColor: theme.id === 'clay' ? '#C9894F' : theme.id === 'indigo' ? '#D9A21B' : '#E08A2E',
                    color: '#FFFFFF',
                    border: 'none',
                    borderRadius: '9999px',
                    padding: '6px 14px',
                    fontSize: '0.8125rem',
                    fontWeight: 700,
                    cursor: 'pointer',
                    boxShadow: '0 2px 8px rgba(0, 0, 0, 0.25)'
                  }}
                >
                  Choose this theme
                </button>
              </div>

              {/* 5-swatch palette strip */}
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '8px' }}>
                <span style={{ fontSize: '0.75rem', color: '#9E9EA8', marginRight: '4px' }}>Palette:</span>
                {theme.swatches.map((swatch, idx) => (
                  <div
                    key={idx}
                    title={swatch}
                    style={{
                      width: '20px',
                      height: '20px',
                      borderRadius: '50%',
                      backgroundColor: swatch,
                      border: '1px solid rgba(255, 255, 255, 0.2)'
                    }}
                  />
                ))}
              </div>

              {/* One-line vibe description */}
              <p style={{ margin: 0, fontSize: '0.8125rem', color: '#B5B5C2', fontStyle: 'italic' }}>
                "{theme.vibe}"
              </p>
            </div>

            {/* Simulated Device Frame */}
            <div
              style={{
                width: `${frameWidth * scaleRatio}px`,
                height: `${frameHeight * scaleRatio}px`,
                borderRadius: isPhone ? '36px' : '16px',
                border: isPhone ? '8px solid #2A2A34' : '6px solid #2A2A34',
                overflow: 'hidden',
                backgroundColor: '#000000',
                position: 'relative',
                boxShadow: '0 12px 40px rgba(0, 0, 0, 0.6)'
              }}
            >
              {/* Phone speaker/camera notch */}
              {isPhone && (
                <div
                  style={{
                    position: 'absolute',
                    top: '8px',
                    left: '50%',
                    transform: 'translateX(-50%)',
                    width: '80px',
                    height: '14px',
                    backgroundColor: '#1C1C22',
                    borderRadius: '9999px',
                    zIndex: 20,
                    pointerEvents: 'none'
                  }}
                />
              )}

              {/* Scaled iframe containing full interactive app instance */}
              <div
                style={{
                  width: `${frameWidth}px`,
                  height: `${frameHeight}px`,
                  transform: `scale(${scaleRatio})`,
                  transformOrigin: 'top left'
                }}
              >
                <iframe
                  ref={iframeRefs[theme.id]}
                  src={`/?theme=${theme.id}&embed=1`}
                  title={`Live instance: ${theme.name}`}
                  style={{
                    width: '100%',
                    height: '100%',
                    border: 'none',
                    display: 'block'
                  }}
                />
              </div>
            </div>
          </div>
        ))}
      </main>

      <Toast toasts={toasts} onDismiss={(id) => setToasts((prev) => prev.filter((t) => t.id !== id))} />
    </div>
  );
};
