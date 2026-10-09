import lessonsData from '../data/lessons.json';
import quotesData from '../data/quotes.json';

interface MatchResult {
  lessonId: number;
  episode: number;
  quoteId: string;
}

const LESSON_KEYWORDS: Record<number, string[]> = {
  1: ['judged', 'judgment', 'scared', 'fear', 'anxious', 'nervous', 'awkward', 'presentation', 'shy', 'embarrassed', 'paralyzed', 'terrified', 'exam fear'],
  2: ['not good enough', 'imposter', 'fraud', 'self doubt', 'doubt', 'insecure', 'unworthy', 'inferior', 'talentless', 'believing in myself', 'loser'],
  3: ['focus', 'distracted', 'concentration', 'attention', 'cant focus', 'phone', 'scrolling', 'multitask', 'procrastinating', 'studying', 'mind everywhere'],
  4: ['lost', 'dont know what to do', 'career', 'path', 'purpose', 'direction', 'future', 'which way', 'confusion', 'decisions', 'one idea'],
  5: ['failed', 'quit', 'giving up', 'give up', 'rejected', 'rejection', 'failure', 'stumbled', 'cant do this', 'done trying', 'feeling like a failure'],
  6: ['burnt out', 'burnout', 'drained', 'exhausted', 'tired', 'energy', 'weak', 'body', 'sleep', 'overworked', 'collapse', 'heaviness'],
  7: ['comparison', 'comparing', 'jealous', 'envy', 'fomo', 'everyone is doing better', 'instagram', 'feed', 'ahead of me', 'behind in life', 'anger'],
  8: ['empty', 'why bother', 'meaning', 'pointless', 'lonely', 'isolated', 'success feels empty', 'service', 'selfish', 'hollow', 'depressed']
};

export function matchLesson(prompt: string): MatchResult {
  const clean = prompt.toLowerCase();
  let bestLesson = 3; // Default to focus
  let highestScore = 0;

  for (const [lessonIdStr, keywords] of Object.entries(LESSON_KEYWORDS)) {
    const lessonId = Number(lessonIdStr);
    let score = 0;
    for (const kw of keywords) {
      if (clean.includes(kw)) {
        score += 2;
      }
    }
    if (score > highestScore) {
      highestScore = score;
      bestLesson = lessonId;
    }
  }

  const lesson = lessonsData.find((l) => l.id === bestLesson) || lessonsData[0];
  const quoteId = lesson.quoteIds[0] || 'q1';

  return {
    lessonId: bestLesson,
    episode: 2, // Start with "Why it happens" or core episode
    quoteId
  };
}

export function getQuoteById(quoteId: string) {
  return quotesData.find((q) => q.id === quoteId) || quotesData[0];
}
