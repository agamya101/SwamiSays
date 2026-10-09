import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { AppContent } from './App';
import './styles/tokens.css';
import './styles/base.css';
import './styles/components.css';

ReactDOM.createRoot(document.getElementById('root') as HTMLElement).render(
  <React.StrictMode>
    <BrowserRouter>
      <AppContent />
    </BrowserRouter>
  </React.StrictMode>
);
