import React, { useEffect, useState } from 'react';
import { ThemeName } from '../types';
import { SHOW_THEME_SWITCHER } from '../config';

export const ThemeSwitcher: React.FC = () => {
  const [currentTheme, setCurrentTheme] = useState<ThemeName>('kesari');

  useEffect(() => {
    const saved = (localStorage.getItem('theme') as ThemeName) || 'kesari';
    const attr = (document.documentElement.getAttribute('data-theme') as ThemeName) || saved;
    setCurrentTheme(attr);
  }, []);

  if (!SHOW_THEME_SWITCHER) return null;

  const handleSelect = (theme: ThemeName) => {
    setCurrentTheme(theme);
    localStorage.setItem('theme', theme);
    document.documentElement.setAttribute('data-theme', theme);
  };

  return (
    <div className="theme-switcher" role="radiogroup" aria-label="Theme switcher">
      <button
        type="button"
        role="radio"
        aria-checked={currentTheme === 'kesari'}
        className={`theme-switcher-dot dot-kesari ${currentTheme === 'kesari' ? 'active' : ''}`}
        title="Theme A: Kesari (Caramel & Sunrise)"
        onClick={() => handleSelect('kesari')}
      />
      <button
        type="button"
        role="radio"
        aria-checked={currentTheme === 'clay'}
        className={`theme-switcher-dot dot-clay ${currentTheme === 'clay' ? 'active' : ''}`}
        title="Theme B: Chai & Clay (Dark, Grounded)"
        onClick={() => handleSelect('clay')}
      />
      <button
        type="button"
        role="radio"
        aria-checked={currentTheme === 'indigo'}
        className={`theme-switcher-dot dot-indigo ${currentTheme === 'indigo' ? 'active' : ''}`}
        title="Theme C: Indigo & Marigold (Belur Math)"
        onClick={() => handleSelect('indigo')}
      />
    </div>
  );
};
