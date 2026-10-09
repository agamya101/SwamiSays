import { UserProgress } from '../types';

const STORAGE_KEY = 'arise_progress';

export function getProgress(): UserProgress {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return {};
    return JSON.parse(raw);
  } catch (e) {
    return {};
  }
}

export function saveProgress(progress: UserProgress): void {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(progress));
    window.dispatchEvent(new Event('progress_updated'));
  } catch (e) {}
}

export function getDone(lessonId: number): number[] {
  const p = getProgress();
  return p[String(lessonId)] || [];
}

export function isEpDone(lessonId: number, ep: number): boolean {
  const list = getDone(lessonId);
  return list.includes(ep);
}

export function markDone(lessonId: number, ep: number): void {
  const p = getProgress();
  const key = String(lessonId);
  const current = p[key] || [];
  if (!current.includes(ep)) {
    p[key] = [...current, ep].sort((a, b) => a - b);
    saveProgress(p);
  }
}

export function totalDone(): number {
  const p = getProgress();
  let count = 0;
  for (const key of Object.keys(p)) {
    count += p[key].length;
  }
  return count;
}
