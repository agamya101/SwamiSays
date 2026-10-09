import React from 'react';
import { NavLink, Link } from 'react-router-dom';
import { SHOW_COMPARE } from '../config';
import { ThemeToggle } from './ThemeToggle';

export const Nav: React.FC = () => {
  return (
    <header className="site-nav">
      <div className="container nav-inner">
        <Link to="/" className="nav-brand" aria-label="SwamiSays - Home">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
            <path d="M12 2v8M12 18v4M4.93 4.93l4.24 4.24M14.83 14.83l4.24 4.24M2 12h8M18 12h4M4.93 19.07l4.24-4.24M14.83 9.17l4.24-4.24" />
          </svg>
          <span>SwamiSays</span>
        </Link>

        <nav className="nav-links" aria-label="Primary navigation">
          <NavLink to="/" end className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
            Home
          </NavLink>
          <NavLink to="/journey" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
            Journey
          </NavLink>
          <NavLink to="/history" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
            History
          </NavLink>
          <NavLink to="/about" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
            About
          </NavLink>
          {SHOW_COMPARE && (
            <NavLink to="/compare" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
              Compare
            </NavLink>
          )}
        </nav>

        <div className="nav-actions">
          <ThemeToggle />
          <Link to="/sos" className="nav-sos-btn" aria-label="Emergency SOS">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
              <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
            </svg>
            <span>SOS</span>
          </Link>
        </div>
      </div>
    </header>
  );
};
