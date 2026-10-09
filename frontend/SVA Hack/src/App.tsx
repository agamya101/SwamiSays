import React, { useEffect } from 'react';
import { Routes, Route, Navigate, useLocation, useNavigate } from 'react-router-dom';
import { Nav } from './components/Nav';
import { TabBar } from './components/TabBar';
import { ThemeSwitcher } from './components/ThemeSwitcher';
import { Home } from './pages/Home';
import { Journey } from './pages/Journey';
import { LessonPage } from './pages/Lesson';
import { EpisodePage } from './pages/Episode';
import { Sos } from './pages/Sos';
import { SosResult } from './pages/SosResult';
import { History } from './pages/History';
import { About } from './pages/About';
import { ReelForge } from './pages/ReelForge';
import { Compare } from './pages/Compare';
import { DEFAULT_ROUTE, SHOW_COMPARE } from './config';

export const AppContent: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();

  const isEmbedded = typeof window !== 'undefined' && window.self !== window.top;
  const searchParams = new URLSearchParams(location.search);
  const isEmbed = isEmbedded || searchParams.get('embed') === '1' || window.location.search.includes('embed=1');
  const urlTheme = searchParams.get('theme');
  const isCompareRoute = location.pathname === '/compare';

  // Apply theme immediately
  useEffect(() => {
    if (urlTheme && ['kesari', 'clay', 'indigo'].includes(urlTheme)) {
      document.documentElement.setAttribute('data-theme', urlTheme);
    } else {
      const saved = localStorage.getItem('theme') || 'kesari';
      document.documentElement.setAttribute('data-theme', saved);
    }

    if (isEmbed) {
      document.documentElement.classList.add('is-embed');
      document.body.classList.add('is-embed-app');
    }
  }, [urlTheme, isEmbed]);

  // Bi-directional postMessage sync for compare mode
  useEffect(() => {
    if (isEmbed) {
      // Notify parent of route changes inside this iframe (only if user changed route)
      try {
        window.parent.postMessage({ type: 'ARISE_NAV_UPDATE', path: location.pathname }, '*');
      } catch (e) {}

      // Listen for commands from parent compare controller
      const handleMessage = (e: MessageEvent) => {
        if (e.data?.type === 'ARISE_NAV_GOTO' && typeof e.data.path === 'string') {
          const targetPath = e.data.path;
          if (targetPath !== location.pathname) {
            // Keep current theme query param
            const currentTheme = document.documentElement.getAttribute('data-theme') || 'kesari';
            navigate(`${targetPath}?theme=${currentTheme}&embed=1`);
          }
        }
      };

      window.addEventListener('message', handleMessage);
      return () => window.removeEventListener('message', handleMessage);
    }
  }, [isEmbed, location.pathname, navigate]);

  // Root landing check: ONLY redirect to compare if top-level window (never inside iframe)
  const shouldRedirectToCompare =
    !isEmbed &&
    !isEmbedded &&
    SHOW_COMPARE &&
    DEFAULT_ROUTE === '/compare' &&
    location.pathname === '/';

  if (shouldRedirectToCompare) {
    return <Navigate to="/compare" replace />;
  }

  return (
    <div className={`app-root ${isEmbed ? 'embedded-view' : ''}`} style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* Top Nav (hidden on standalone /compare page) */}
      {!isCompareRoute && <Nav />}

      <div style={{ flex: 1 }}>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/journey" element={<Journey />} />
          <Route path="/journey/:id" element={<LessonPage />} />
          <Route path="/journey/:id/:ep" element={<EpisodePage />} />
          <Route path="/sos" element={<Sos />} />
          <Route path="/sos/result" element={<SosResult />} />
          <Route path="/history" element={<History />} />
          <Route path="/about" element={<About />} />
          <Route path="/forge" element={<ReelForge />} />
          <Route path="/studio" element={<ReelForge />} />
          {SHOW_COMPARE && !isEmbedded && <Route path="/compare" element={<Compare />} />}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>

      {/* Mobile Tab Bar */}
      {!isCompareRoute && <TabBar />}

      {/* Floating 3-dot Theme Switcher for testing */}
      {!isEmbed && !isCompareRoute && <ThemeSwitcher />}
    </div>
  );
};
