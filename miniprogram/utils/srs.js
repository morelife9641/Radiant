import { getReviewDueAtAsiaShanghai } from './date';

const MIN_EASE = 1.3;
const MAX_EASE = 2.5;
const CORRECT_INTERVAL_DAYS = [1, 3, 7, 15, 30];

export function nextSchedule(progress, result) {
  const now = Date.now();
  let { easiness = 2.5, correctCount = 0, wrongCount = 0, streakCorrect = 0 } = progress || {};
  let interval = Number(progress && progress.interval) || 0;
  let nextReviewAt = Number(progress && progress.nextReviewAt) || 0;
  let status = 'learning';

  if (result === 'known') {
    easiness = Math.min(MAX_EASE, easiness + 0.1);
    correctCount += 1;
    streakCorrect += 1;
    const day = CORRECT_INTERVAL_DAYS[Math.min(streakCorrect - 1, CORRECT_INTERVAL_DAYS.length - 1)];
    interval = day * 24 * 60;
    nextReviewAt = getReviewDueAtAsiaShanghai(now, day);
    status = streakCorrect >= 5 ? 'mastered' : 'reviewing';
  } else {
    easiness = Math.max(MIN_EASE, easiness - 0.2);
    wrongCount += 1;
    streakCorrect = 0;
    status = wrongCount >= 3 ? 'difficult' : 'learning';
  }

  return { easiness, interval, nextReviewAt, correctCount, wrongCount, streakCorrect, status };
}
