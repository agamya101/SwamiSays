import React from 'react';
import { NavLink } from 'react-router-dom';

export const TabBar: React.FC = () => {
  return (
    <nav className="tab-bar" aria-label="Mobile navigation">
      <NavLink
        to="/"
        end
        className={({ isActive }) => `tab-item ${isActive ? 'active' : ''}`}
        aria-label="Home"
      >
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
          <path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
          <polyline points="9 22 9 12 15 12 15 22" />
        </svg>
        <span>Home</span>
      </NavLink>

      <NavLink
        to="/journey"
        className={({ isActive }) => `tab-item ${isActive ? 'active' : ''}`}
        aria-label="Journey"
      >
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
          <circle cx="12" cy="12" r="10" />
          <polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76" />
        </svg>
        <span>Journey</span>
      </NavLink>

      <NavLink
        to="/sos"
        className="tab-sos"
        aria-label="Emergency SOS"
      >
        <div className="tab-sos-circle">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
            <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
          </svg>
        </div>
        <span className="tab-sos-label">SOS</span>
      </NavLink>

      <NavLink
        to="/history"
        className={({ isActive }) => `tab-item ${isActive ? 'active' : ''}`}
        aria-label="Reel History"
      >
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
          <circle cx="12" cy="12" r="10" />
          <polyline points="12 6 12 12 16 14" />
        </svg>
        <span>History</span>
      </NavLink>

    </nav>
  );
};
