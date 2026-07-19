const SHANGHAI_OFFSET_MS = 8 * 60 * 60 * 1000;
const DAY_MS = 24 * 60 * 60 * 1000;

export function getDateKeyAsiaShanghai(now = Date.now()) {
  const timestamp = now instanceof Date ? now.getTime() : Number(now);
  return new Date(timestamp + SHANGHAI_OFFSET_MS).toISOString().slice(0, 10);
}

export function getStartOfDayAsiaShanghai(now = Date.now()) {
  const timestamp = now instanceof Date ? now.getTime() : Number(now);
  const shifted = new Date(timestamp + SHANGHAI_OFFSET_MS);
  return Date.UTC(
    shifted.getUTCFullYear(),
    shifted.getUTCMonth(),
    shifted.getUTCDate()
  ) - SHANGHAI_OFFSET_MS;
}

export function getReviewDueAtAsiaShanghai(now = Date.now(), intervalDays = 1) {
  const days = Math.max(1, Math.round(Number(intervalDays) || 1));
  return getStartOfDayAsiaShanghai(now) + days * DAY_MS;
}

export function getReviewCutoffAsiaShanghai(now = Date.now()) {
  return getStartOfDayAsiaShanghai(now) + DAY_MS - 1;
}

export function isReviewDueToday(nextReviewAt, now = Date.now()) {
  const dueAt = Number(nextReviewAt);
  return Boolean(dueAt && dueAt <= getReviewCutoffAsiaShanghai(now));
}
