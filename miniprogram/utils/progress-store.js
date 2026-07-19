const PROGRESS_SYNC_TTL = 5 * 60 * 1000;
const PROGRESS_SYNC_KEY = (bookId) => `progressSync.v2.${bookId}`;
const TODAY_RESET_KEY = 'learnReset.today';

function getDateKeyAsiaShanghai(ms = Date.now()) {
  return new Date(Number(ms || Date.now()) + 8 * 60 * 60 * 1000)
    .toISOString()
    .slice(0, 10);
}

function getProgressTime(progress) {
  if (!progress) return 0;
  const value = progress.clientUpdatedAt || progress.updatedAt;
  if (!value) return 0;
  if (typeof value === 'number') return value;
  if (value instanceof Date) return value.getTime();
  const parsed = Date.parse(value);
  return Number.isFinite(parsed) ? parsed : 0;
}

export function mergeProgressRecords(local = {}, records = []) {
  const merged = { ...local };
  const resetToday = wx.getStorageSync(TODAY_RESET_KEY) || {};
  const resetDateKey = resetToday.dateKey || getDateKeyAsiaShanghai();
  const resetAt = Number(resetToday.resetAt || 0);

  for (const record of records) {
    const key = record.normalized || record.word;
    if (!key) continue;

    const existing = merged[key];
    const recordTime = getProgressTime(record);
    const shouldIgnoreResetTodayFields = resetAt
      && recordTime
      && recordTime <= resetAt
      && (
        record.dailyDoneDateKey === resetDateKey
        || record.dailyWrongDateKey === resetDateKey
      );
    if (existing && getProgressTime(record) < getProgressTime(existing)) {
      existing.bookIds = Array.from(new Set([
        ...(Array.isArray(existing.bookIds) ? existing.bookIds : []),
        ...(Array.isArray(record.bookIds) ? record.bookIds : [])
      ]));
      continue;
    }

    merged[key] = {
      easiness: record.easiness,
      interval: record.interval,
      nextReviewAt: record.nextReviewAt,
      correctCount: record.correctCount || 0,
      wrongCount: record.wrongCount || 0,
      streakCorrect: record.streakCorrect || 0,
      status: record.status || 'learning',
      lastResult: record.lastResult || '',
      favorite: Boolean(record.favorite),
      favoritedAt: record.favoritedAt || null,
      ignoredAt: record.ignoredAt || null,
      dailyDoneDateKey: shouldIgnoreResetTodayFields
        ? ''
        : (record.dailyDoneDateKey || (existing && existing.dailyDoneDateKey) || ''),
      dailyWrongDateKey: shouldIgnoreResetTodayFields
        ? ''
        : (record.dailyWrongDateKey || (existing && existing.dailyWrongDateKey) || ''),
      dailyRecoveryCorrectCount: shouldIgnoreResetTodayFields ? 0 : (record.dailyRecoveryCorrectCount || 0),
      wordId: record.wordId,
      bookId: record.bookId || record.lastReviewedBookId || (existing && existing.bookId) || '',
      bookIds: Array.isArray(record.bookIds)
        ? record.bookIds
        : ((existing && existing.bookIds) || []),
      normalized: record.normalized || key,
      _todayDone: false,
      clientUpdatedAt: record.clientUpdatedAt || 0,
      updatedAt: record.updatedAt || record.clientUpdatedAt || 0
    };
  }

  return merged;
}

export function shouldSyncProgress(bookId, now = Date.now()) {
  const lastSyncedAt = Number(wx.getStorageSync(PROGRESS_SYNC_KEY(bookId)) || 0);
  return !lastSyncedAt || now - lastSyncedAt >= PROGRESS_SYNC_TTL;
}

export function markProgressSynced(bookId, now = Date.now()) {
  wx.setStorageSync(PROGRESS_SYNC_KEY(bookId), now);
}
