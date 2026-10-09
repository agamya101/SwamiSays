export interface Helpline {
  name: string;
  number: string;
  hours: string;
  description: string;
}

export const CRISIS_HELPLINES: Helpline[] = [
  {
    name: 'Tele-MANAS (Govt of India)',
    number: '14416 / 1800-891-4416',
    hours: '24/7 Free & Confidential',
    description: 'National tele-mental health programme across all Indian languages'
  },
  {
    name: 'KIRAN Mental Health Helpline',
    number: '1800-599-0019',
    hours: '24/7 Toll-free',
    description: 'Ministry of Social Justice and Empowerment support line'
  },
  {
    name: 'Vandrevala Foundation',
    number: '+91 9999 666 555',
    hours: '24/7 Helpline',
    description: 'Free, confidential psychological counseling and crisis intervention'
  }
];

const CRISIS_PATTERNS: RegExp[] = [
  /\bsuicid(e|al)\b/i,
  /\bkill\s+(my\s*self|me)\b/i,
  /\bend\s+(my\s*life|it\s*all)\b/i,
  /\bself[\s-]*harm\b/i,
  /\bwant\s+to\s+die\b/i,
  /\bno\s+reason\s+to\s+live\b/i,
  /\bhurt(ing)?\s+myself\b/i,
  /\bdie\b.*\btonight\b/i,
  /\bcut(ting)?\s+my\s*wrists?\b/i
];

export function checkCrisis(text: string): boolean {
  if (!text) return false;
  return CRISIS_PATTERNS.some((pattern) => pattern.test(text));
}
