export type SupportedLang = 'en' | 'hi';

export interface Quote {
  id: string;
  text: string;
  source: string;
  sourceUrl: string;
  verified: boolean;
  topics: string[];
}

export interface Lesson {
  id: number;
  slug: string;
  title: string;
  painPoint: string;
  summary: string;
  icon: string;
  quoteIds: string[];
}

export interface Episode {
  lessonId: number;
  ep: number;
  title: string;
  situation?: string;
  moral?: string;
  hook: string;
  story: string;
  quoteId: string;
  meaning: string;
  tryThis: string;
  nextHook: string;
  ai?: boolean;
  videoUrl?: string;
}

export type SceneType = 'hook' | 'situation' | 'quote' | 'meaning' | 'action' | 'outro';

export interface ReelScene {
  type: SceneType;
  text: string;
  durationMs: number;
  quoteId?: string;
}

export interface ReelRequest {
  prompt: string;
  lang: SupportedLang;
  name?: string;
  age?: number;
  profession?: string;
  device_id?: string;
  render_video?: boolean;
  subtitle_color?: string;
  voice_id?: string;
  music_track?: string;
}

export interface ReelResponse {
  quoteId: string;
  quote: {
    text: string;
    source: string;
    sourceUrl: string;
    verified: boolean;
  };
  lessonId: number;
  episode: number;
  scenes: ReelScene[];
  transcript: string;
  disclaimer: string;
  videoUrl?: string;
  jobId?: string;
  journey?: string;
  confidence?: number;
  apiVerified?: boolean;
  modelUsed?: string;
  verification?: {
    api_called: boolean;
    provider: string;
    model: string;
    tokens_used?: number;
    finish_reason?: string;
    reason?: string;
    timestamp?: string;
  };
}

export interface HistoryEntry {
  id: string;
  device_id: string;
  created_at: string;
  prompt: string;
  name: string;
  age: number | null;
  profession: string;
  lang: SupportedLang;
  journey: string;
  lesson_id: number;
  quote_id: string;
  quote_text: string;
  quote_source: string;
  transcript: string;
  scenes: ReelScene[];
  job_id: string | null;
  video_url: string | null;
  status: string;
  api_model?: string;
  api_verified?: number | boolean;
}

export type UserProgress = Record<string, number[]>;

export type ThemeName = 'kesari' | 'clay' | 'indigo';

export interface ForgeVoice {
  id: string;
  name: string;
  gender: string;
  lang: string;
}

export interface ForgeStatus {
  status: string;
  ffmpeg: string;
  voices: ForgeVoice[];
  styles: string[];
  aspect_ratios: Record<string, { width: number; height: number; label: string }>;
  stock_categories: Record<string, number>;
  total_clips: number;
  figures: string[];
  music_tracks: string[];
}

export interface ForgeTemplate {
  id: string;
  title: string;
  description: string;
  prompt: string;
}

export interface ForgeJob {
  id: string;
  stage: string;
  progress: number;
  message: string;
  logs: string[];
  error?: string | null;
  completed: boolean;
  video_url?: string | null;
}
