import { Lesson, Episode, Quote, ReelRequest, ReelResponse, UserProgress, SupportedLang, HistoryEntry } from '../types';
import lessonsData from '../data/lessons.json';
import episodesData from '../data/episodes.json';
import quotesData from '../data/quotes.json';
import { matchLesson, getQuoteById } from './recommend';
import { I18N_SCENE_TEMPLATES } from './i18n';
import { getProgress as getLocalProgress, saveProgress as saveLocalProgress } from './progress';

// Environment switch: default to REAL backend API, fallback to mock if offline
const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true';
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

/**
 * Returns a stable anonymous device ID stored in localStorage.
 */
export function getDeviceId(): string {
  let id = localStorage.getItem('sva_device_id');
  if (!id) {
    id = 'dev_' + Math.random().toString(36).substring(2, 9) + '_' + Date.now().toString(36);
    localStorage.setItem('sva_device_id', id);
  }
  return id;
}

/**
 * Validate runtime structure of ReelResponse
 */
function validateReelResponse(data: any): data is ReelResponse {
  if (!data || typeof data !== 'object') return false;
  if (typeof data.quoteId !== 'string') return false;
  if (!data.quote || typeof data.quote.text !== 'string' || typeof data.quote.source !== 'string') return false;
  if (typeof data.lessonId !== 'number' || typeof data.episode !== 'number') return false;
  if (!Array.isArray(data.scenes) || data.scenes.length === 0) return false;
  for (const s of data.scenes) {
    if (!s.type || !s.text || typeof s.durationMs !== 'number') return false;
  }
  if (typeof data.transcript !== 'string' || typeof data.disclaimer !== 'string') return false;
  return true;
}

export async function getLessons(): Promise<Lesson[]> {
  if (USE_MOCK) {
    return lessonsData as Lesson[];
  }
  try {
    const res = await fetch(`${API_BASE_URL}/api/lessons`);
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn('Backend fetch failed, falling back to local lessons:', err);
    return lessonsData as Lesson[];
  }
}

export async function getEpisodes(lessonId?: number): Promise<Episode[]> {
  if (USE_MOCK) {
    const eps = episodesData as Episode[];
    return lessonId !== undefined ? eps.filter((e) => e.lessonId === lessonId) : eps;
  }
  try {
    const url = lessonId !== undefined ? `${API_BASE_URL}/api/episodes?lessonId=${lessonId}` : `${API_BASE_URL}/api/episodes`;
    const res = await fetch(url);
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn('Backend fetch failed, falling back to local episodes:', err);
    const eps = episodesData as Episode[];
    return lessonId !== undefined ? eps.filter((e) => e.lessonId === lessonId) : eps;
  }
}

export async function getDailyQuote(): Promise<Quote> {
  const verified = (quotesData as Quote[]).filter((q) => q.verified);
  const now = new Date();
  const start = new Date(now.getFullYear(), 0, 0);
  const diff = now.getTime() - start.getTime();
  const oneDay = 1000 * 60 * 60 * 24;
  const dayOfYear = Math.floor(diff / oneDay);
  const quote = verified[dayOfYear % verified.length] || verified[0];

  if (USE_MOCK) {
    return quote;
  }
  try {
    const res = await fetch(`${API_BASE_URL}/api/quote/daily`);
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn('Backend fetch failed, falling back to local daily quote:', err);
    return quote;
  }
}

export async function generateReel(req: ReelRequest): Promise<ReelResponse> {
  if (USE_MOCK) {
    // Simulate 3.2s network latency per specification
    await new Promise((resolve) => setTimeout(resolve, 3200));

    const match = matchLesson(req.prompt);
    const quote = getQuoteById(match.quoteId);
    const lang: SupportedLang = req.lang || 'en';
    const templates = I18N_SCENE_TEMPLATES[lang] || I18N_SCENE_TEMPLATES.en;

    const matchedEpisode = (episodesData as Episode[]).find(
      (e) => e.lessonId === match.lessonId && e.ep === match.episode
    ) || (episodesData[0] as Episode);

    const scenes = [
      {
        type: 'hook' as const,
        text: `${templates.hookPrefix} "${req.prompt.slice(0, 75)}"`,
        durationMs: 6500
      },
      {
        type: 'situation' as const,
        text: `${templates.situationPrefix} ${matchedEpisode.hook}`,
        durationMs: 7000
      },
      {
        type: 'quote' as const,
        text: `"${quote.text}"`,
        durationMs: 8500,
        quoteId: quote.id
      },
      {
        type: 'meaning' as const,
        text: `${templates.meaningPrefix} ${matchedEpisode.meaning}`,
        durationMs: 7500
      },
      {
        type: 'action' as const,
        text: `${templates.actionPrefix} ${matchedEpisode.tryThis}`,
        durationMs: 7000
      },
      {
        type: 'outro' as const,
        text: templates.outro,
        durationMs: 5500
      }
    ];

    const transcript = scenes.map((s) => s.text).join('\n\n');

    const mockResponse: ReelResponse = {
      quoteId: quote.id,
      quote: {
        text: quote.text,
        source: quote.source,
        sourceUrl: quote.sourceUrl,
        verified: quote.verified
      },
      lessonId: match.lessonId,
      episode: match.episode,
      scenes,
      transcript,
      disclaimer: "Story and interpretation are AI-generated. The quote in the gold card is authentic and verified."
    };

    return mockResponse;
  }

  // Real backend integration
  try {
    const devId = getDeviceId();
    const payload = { ...req, device_id: req.device_id || devId };
    const res = await fetch(`${API_BASE_URL}/api/reel`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Device-Id': devId
      },
      body: JSON.stringify(payload)
    });

    if (res.ok) {
      const data = await res.json();
      if (validateReelResponse(data)) {
        return data;
      }
    }
  } catch (err) {
    console.warn('Real backend call failed, using client-side fallback:', err);
  }

  // Graceful client fallback if backend unreachable
  const match = matchLesson(req.prompt);
  const quote = getQuoteById(match.quoteId);
  const lang: SupportedLang = req.lang || 'en';
  const templates = I18N_SCENE_TEMPLATES[lang] || I18N_SCENE_TEMPLATES.en;
  const matchedEpisode = (episodesData as Episode[]).find(
    (e) => e.lessonId === match.lessonId && e.ep === match.episode
  ) || (episodesData[0] as Episode);

  const scenes = [
    { type: 'hook' as const, text: `${templates.hookPrefix} "${req.prompt.slice(0, 75)}"`, durationMs: 6500 },
    { type: 'situation' as const, text: `${templates.situationPrefix} ${matchedEpisode.hook}`, durationMs: 7000 },
    { type: 'quote' as const, text: `"${quote.text}"`, durationMs: 8500, quoteId: quote.id },
    { type: 'meaning' as const, text: `${templates.meaningPrefix} ${matchedEpisode.meaning}`, durationMs: 7500 },
    { type: 'action' as const, text: `${templates.actionPrefix} ${matchedEpisode.tryThis}`, durationMs: 7000 },
    { type: 'outro' as const, text: templates.outro, durationMs: 5500 }
  ];

  return {
    quoteId: quote.id,
    quote: {
      text: quote.text,
      source: quote.source,
      sourceUrl: quote.sourceUrl,
      verified: quote.verified
    },
    lessonId: match.lessonId,
    episode: match.episode,
    scenes,
    transcript: scenes.map((s) => s.text).join('\n\n'),
    disclaimer: "Story and interpretation are AI-generated. The quote in the gold card is authentic and verified."
  };
}

export async function getJobProgress(jobId: string): Promise<any> {
  try {
    const res = await fetch(`${API_BASE_URL}/api/job/${jobId}`);
    if (res.ok) return await res.json();
  } catch (e) {}
  return { status: 'unknown', progress: 0 };
}

export async function getProgress(): Promise<UserProgress> {
  return getLocalProgress();
}

export async function saveProgress(progress: UserProgress): Promise<void> {
  saveLocalProgress(progress);
}

// ─────────────────────────────────────────────────────────────────────────────
// SQLite History API Methods
// ─────────────────────────────────────────────────────────────────────────────

export async function getHistory(): Promise<HistoryEntry[]> {
  try {
    const devId = getDeviceId();
    const res = await fetch(`${API_BASE_URL}/api/history?device_id=${encodeURIComponent(devId)}`, {
      headers: { 'X-Device-Id': devId }
    });
    if (res.ok) return await res.json();
  } catch (err) {
    console.warn('Failed to load history:', err);
  }
  return [];
}

export async function getHistoryEntry(id: string): Promise<HistoryEntry | null> {
  try {
    const devId = getDeviceId();
    const res = await fetch(`${API_BASE_URL}/api/history/${encodeURIComponent(id)}`, {
      headers: { 'X-Device-Id': devId }
    });
    if (res.ok) return await res.json();
  } catch (err) {
    console.warn('Failed to load history entry:', err);
  }
  return null;
}

export async function deleteHistoryEntry(id: string): Promise<boolean> {
  try {
    const devId = getDeviceId();
    const res = await fetch(`${API_BASE_URL}/api/history/${encodeURIComponent(id)}?device_id=${encodeURIComponent(devId)}`, {
      method: 'DELETE',
      headers: { 'X-Device-Id': devId }
    });
    return res.ok;
  } catch (err) {
    console.warn('Failed to delete history entry:', err);
    return false;
  }
}

export async function clearAllHistory(): Promise<boolean> {
  try {
    const devId = getDeviceId();
    const res = await fetch(`${API_BASE_URL}/api/history?device_id=${encodeURIComponent(devId)}`, {
      method: 'DELETE',
      headers: { 'X-Device-Id': devId }
    });
    return res.ok;
  } catch (err) {
    console.warn('Failed to clear all history:', err);
    return false;
  }
}

export async function verifyGeminiApi(): Promise<{
  status: string;
  api_called: boolean;
  model?: string;
  latency_ms?: number;
  tokens_used?: number;
  test_output?: any;
  message?: string;
}> {
  try {
    const res = await fetch(`${API_BASE_URL}/api/verify-gemini`);
    if (res.ok) return await res.json();
  } catch (err) {
    console.warn('Failed to verify Gemini API:', err);
  }
  return { status: 'error', api_called: false, message: 'Could not contact verification endpoint' };
}

// ─────────────────────────────────────────────────────────────────────────────
// ReelForge Studio Client Methods
// ─────────────────────────────────────────────────────────────────────────────

export async function getForgeStatus(): Promise<any> {
  try {
    const res = await fetch(`${API_BASE_URL}/api/forge/status`);
    if (res.ok) return await res.json();
  } catch (e) {
    console.warn('Failed to load ReelForge status:', e);
  }
  return null;
}

export async function getForgeTemplates(): Promise<any[]> {
  try {
    const res = await fetch(`${API_BASE_URL}/api/forge/templates`);
    if (res.ok) return await res.json();
  } catch (e) {
    console.warn('Failed to load ReelForge templates:', e);
  }
  return [];
}

export async function getForgeShowcase(): Promise<any> {
  try {
    const res = await fetch(`${API_BASE_URL}/api/forge/showcase`);
    if (res.ok) return await res.json();
  } catch (e) {
    console.warn('Failed to load ReelForge showcase:', e);
  }
  return null;
}

export async function generateForgeVideo(data: {
  prompt: string;
  scene_count?: number;
  aspect_ratio?: string;
  style?: string;
  voice_id?: string;
  add_music?: boolean;
  subtitle_color?: string;
  use_stock_clips?: boolean;
  music_track?: string;
}): Promise<{ jobId: string }> {
  const res = await fetch(`${API_BASE_URL}/api/forge/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to start video generation');
  }
  return await res.json();
}

export async function getForgeJob(jobId: string): Promise<any> {
  try {
    const res = await fetch(`${API_BASE_URL}/api/forge/job/${jobId}`);
    if (res.ok) return await res.json();
  } catch (e) {
    console.warn(`Failed to fetch job ${jobId}:`, e);
  }
  return { id: jobId, progress: 0, completed: false, stage: 'unknown' };
}
