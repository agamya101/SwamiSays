import React, { useState, useEffect } from 'react';
import { LIGHT_THEME, DARK_THEME } from '../config';

interface ThemeToggleProps {
  className?: string;
}

export const ThemeToggle: React.FC<ThemeToggleProps> = ({ className = '' }) => {
  const [currentTheme, setCurrentTheme] = useState<string>(() => {
    return document.documentElement.getAttribute('data-theme') || LIGHT_THEME;
  });

  useEffect(() => {
    const observer = new MutationObserver(() => {
      const theme = document.documentElement.getAttribute('data-theme') || LIGHT_THEME;
      setCurrentTheme(theme);
    });

    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ['data-theme']
    });

    return () => observer.disconnect();
  }, []);

  const isDark = currentTheme === DARK_THEME;

  const toggleTheme = () => {
    const nextTheme = isDark ? LIGHT_THEME : DARK_THEME;
    document.documentElement.setAttribute('data-theme', nextTheme);
    localStorage.setItem('theme', nextTheme);
    setCurrentTheme(nextTheme);
    window.dispatchEvent(new CustomEvent('theme_changed', { detail: nextTheme }));
  };

  return (
    <button
      type="button"
      onClick={toggleTheme}
      className={`theme-toggle-btn ${className}`}
      aria-label={isDark ? 'Switch to light mode (Kesari)' : 'Switch to dark mode (Chai & Clay)'}
      title={isDark ? 'Switch to Light Mode (Theme A: Kesari)' : 'Switch to Dark Mode (Theme B: Chai & Clay)'}
    >
      {isDark ? (
        /* Sun icon for switching back to light mode */
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
          <circle cx="12" cy="12" r="5" />
          <line x1="12" y1="1" x2="12" y2="3" />
          <line x1="12" y1="21" x2="12" y2="23" />
          <line x1="4.22" y1="4.22" x2="5.64" y2="5.64" />
          <line x1="18.36" y1="18.36" x2="19.78" y2="19.78" />
          <line x1="1" y1="12" x2="3" y2="12" />
          <line x1="21" y1="12" x2="23" y2="12" />
          <line x1="4.22" y1="19.78" x2="5.64" y2="18.36" />
          <line x1="18.36" y1="5.64" x2="19.78" y2="4.22" />
        </svg>
      ) : (
        /* Moon icon for switching to dark mode */
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
          <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
        </svg>
      )}
    </button>
  );
};
