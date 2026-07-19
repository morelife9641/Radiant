const cloud = require('wx-server-sdk');
cloud.init({ env: cloud.DYNAMIC_CURRENT_ENV });

const db = cloud.database();
const _ = db.command;

const PAGE_SIZE = 100;
const MAX_PROGRESS_PAGE_SIZE = 500;
const DEFAULT_REVIEW_LIMIT = 50;
const MAX_REVIEW_LIMIT = 100;
const MAX_SUBMIT_RECORDS = 20;
const MAX_REVIEW_SCAN_ROWS = 5000;
const RESET_BATCH_SIZE = 100;
const RESET_PROGRESS_COLLECTIONS = ['user_word_progress', 'user_book_progress', 'user_learn_sessions', 'user_learning_activity'];
const STATUS_VALUES = ['new', 'learning', 'reviewing', 'difficult', 'mastered', 'ignored'];
const RESULT_VALUES = ['known', 'unknown'];
const CORRECT_INTERVAL_DAYS = [1, 3, 7, 15, 30];
const DAILY_RECOVERY_REQUIRED = 3;
const SHANGHAI_OFFSET_MS = 8 * 60 * 60 * 1000;
const DAY_MS = 24 * 60 * 60 * 1000;
const IN_QUERY_CHUNK_SIZE = 10;
const MAX_SESSION_BYTES = 600 * 1024;

function ok(data) {
  return { ok: true, ...data };
}

function fail(code, message) {
  return { ok: false, code, message };
}

function wordIdFor(normalized) {
  const slug = String(normalized || '')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '_')
    .replace(/^_+|_+$/g, '')
    .replace(/_+/g, '_');

  return slug ? `word_${slug}` : '';
}

function numberOrDefault(value, fallback) {
  const n = Number(value);
  return Number.isFinite(n) ? n : fallback;
}

function normalizeLimit(limit, fallback = DEFAULT_REVIEW_LIMIT, max = MAX_REVIEW_LIMIT) {
  const n = Number(limit || fallback);
  if (!Number.isFinite(n) || n <= 0) return fallback;
  return Math.min(Math.floor(n), max);
}

function normalizeStatus(status, fallback = 'learning') {
  return STATUS_VALUES.includes(status) ? status : fallback;
}

function normalizeSessionScope(event = {}) {
  const wordbookId = String(event.wordbookId || event.bookId || '').trim().slice(0, 80);
  const mode = event.mode === 'review' ? 'review' : 'daily';
  const dateKey = String(event.dateKey || getDateKeyAsiaShanghai()).trim().slice(0, 10);
  if (!wordbookId || !/^\d{4}-\d{2}-\d{2}$/.test(dateKey)) return null;
  return { wordbookId, mode, dateKey };
}

function learnSessionId(openid, scope) {
  return `${openid}:${scope.wordbookId}:${scope.mode}:${scope.dateKey}`;
}

function normalizeClientUpdatedAt(value) {
  const now = Date.now();
  return Math.min(numberOrDefault(value, now), now + 5 * 60 * 1000);
}

function getSessionWordKey(word) {
  return String(word && (word.wordId || word._id || word.id || word.normalized || word.word) || '')
    .trim()
    .toLowerCase();
}

function mergeSessionNumberMaps(first = {}, second = {}) {
  const merged = { ...(first || {}) };
  Object.keys(second || {}).forEach((key) => {
    merged[key] = Math.max(numberOrDefault(merged[key], 0), numberOrDefault(second[key], 0));
  });
  return merged;
}

function mergeSessionWords(first = [], second = []) {
  const merged = [];
  const seen = new Set();
  [...(first || []), ...(second || [])].forEach((word) => {
    const key = getSessionWordKey(word);
    if (!key || seen.has(key)) return;
    seen.add(key);
    merged.push(word);
  });
  return merged;
}

function getCurrentQueuePassedKeys(words = [], passedKeys = []) {
  const queueKeys = new Set((Array.isArray(words) ? words : []).map(getSessionWordKey).filter(Boolean));
  return new Set((Array.isArray(passedKeys) ? passedKeys : Array.from(passedKeys || []))
    .filter(key => queueKeys.has(key)));
}

function mergeSessionHistory(first = [], second = []) {
  const merged = [];
  const indexByKey = {};
  [...(first || []), ...(second || [])].forEach((item) => {
    const key = String(item && (item.key || item.word) || '').trim().toLowerCase();
    if (!key) return;
    const index = indexByKey[key];
    if (index === undefined) {
      indexByKey[key] = merged.length;
      merged.push(item);
    } else if (item && item.correct && !merged[index].correct) {
      merged[index] = item;
    }
  });
  return merged.slice(0, 120);
}

function normalizeCompletedHistory(value) {
  if (!value || typeof value !== 'object' || Array.isArray(value)) return null;
  const answerHistory = mergeSessionHistory(value.answerHistory, []);
  if (!answerHistory.length) return null;
  return {
    answerHistory,
    stats: {
      known: Math.max(0, numberOrDefault(value.stats && value.stats.known, 0)),
      unknown: Math.max(0, numberOrDefault(value.stats && value.stats.unknown, 0))
    },
    completedAt: normalizeClientUpdatedAt(value.completedAt)
  };
}

function nextSessionIndex(words = [], passedKeys, preferredIndex = 0) {
  if (!words.length) return 0;
  const start = Math.min(Math.max(0, Math.floor(numberOrDefault(preferredIndex, 0))), words.length - 1);
  for (let offset = 0; offset < words.length; offset += 1) {
    const index = (start + offset) % words.length;
    if (!passedKeys.has(getSessionWordKey(words[index]))) return index;
  }
  return start;
}

function countDailySessionPasses(words = [], passedKeys) {
  const seen = new Set();
  return (words || []).reduce((count, word) => {
    const key = getSessionWordKey(word);
    if (!key || seen.has(key) || word._learnSource === 'review' || !passedKeys.has(key)) return count;
    seen.add(key);
    return count + 1;
  }, 0);
}

function mergeLearnSession(existing = {}, incoming = {}, existingUpdatedAt = 0, incomingUpdatedAt = 0) {
  const preferred = incomingUpdatedAt >= existingUpdatedAt ? incoming : existing;
  const secondary = preferred === incoming ? existing : incoming;
  const preferredQueueId = String(preferred.queueId || '');
  const secondaryQueueId = String(secondary.queueId || '');
  if (preferredQueueId !== secondaryQueueId && (preferredQueueId || secondaryQueueId)) {
    return preferred;
  }
  const mergedPassedKeys = [
    ...(Array.isArray(preferred.groupPassedKeys) ? preferred.groupPassedKeys : []),
    ...(Array.isArray(secondary.groupPassedKeys) ? secondary.groupPassedKeys : [])
  ].filter(Boolean);
  const words = mergeSessionWords(preferred.words, secondary.words);
  const passedKeys = getCurrentQueuePassedKeys(words, mergedPassedKeys);
  const index = nextSessionIndex(words, passedKeys, preferred.index);
  const currentWord = words[index] || null;
  const keepsCurrentQuestion = getSessionWordKey(preferred.currentWord) === getSessionWordKey(currentWord);
  const stats = {
    ...(preferred.stats || {}),
    known: passedKeys.size,
    unknown: Math.max(numberOrDefault(preferred.stats && preferred.stats.unknown, 0), numberOrDefault(secondary.stats && secondary.stats.unknown, 0))
  };

  return {
    ...preferred,
    words,
    index,
    total: words.length,
    targetTotal: Math.max(numberOrDefault(preferred.targetTotal, 0), numberOrDefault(secondary.targetTotal, 0), words.length),
    currentWord,
    currentQuestion: keepsCurrentQuestion ? preferred.currentQuestion : null,
    answered: keepsCurrentQuestion ? Boolean(preferred.answered) : false,
    pendingNextState: keepsCurrentQuestion ? preferred.pendingNextState : null,
    groupPassedKeys: Array.from(passedKeys),
    groupRecoveryCount: mergeSessionNumberMaps(preferred.groupRecoveryCount, secondary.groupRecoveryCount),
    todayRetryCount: mergeSessionNumberMaps(preferred.todayRetryCount, secondary.todayRetryCount),
    answerHistory: mergeSessionHistory(preferred.answerHistory, secondary.answerHistory),
    stats,
    dailyProgressBase: Math.max(numberOrDefault(preferred.dailyProgressBase, 0), numberOrDefault(secondary.dailyProgressBase, 0)),
    dailyQueueKnown: countDailySessionPasses(words, passedKeys)
  };
}

async function ensureLearnSessionCollection() {
  if (typeof db.createCollection === 'function') {
    await db.createCollection('user_learn_sessions').catch(() => null);
  }
}

async function ensureLearningActivityCollection() {
  if (typeof db.createCollection === 'function') {
    await db.createCollection('user_learning_activity').catch(() => null);
  }
}

function chunk(values, size = IN_QUERY_CHUNK_SIZE) {
  const chunks = [];
  for (let index = 0; index < values.length; index += size) {
    chunks.push(values.slice(index, index + size));
  }
  return chunks;
}

async function fetchWordsByIds(wordIds) {
  const words = [];
  for (const ids of chunk(Array.from(new Set(wordIds.filter(Boolean))))) {
    const result = await db.collection('words')
      .where({ _id: _.in(ids) })
      .limit(ids.length)
      .get();
    words.push(...(result.data || []));
  }
  return words;
}

async function fetchLearningContentByWordIds(wordIds) {
  const groups = chunk(Array.from(new Set(wordIds.filter(Boolean))));
  const results = await Promise.all(groups.map(ids => (
    db.collection('word_learning_content')
      .where({ wordId: _.in(ids) })
      .field({
        _id: true,
        wordId: true,
        coreSense: true,
        shortDefinitionEn: true,
        shortDefinitionZh: true,
        short_definition_en: true,
        short_definition_zh: true
      })
      .limit(ids.length)
      .get()
      .catch(() => ({ data: [] }))
  )));
  return results.reduce((all, result) => all.concat(result.data || []), []);
}

function normalizeCoreSense(content = {}) {
  const source = content || {};
  const coreSense = source.coreSense && typeof source.coreSense === 'object'
    ? source.coreSense
    : {};
  const en = String(coreSense.en || source.shortDefinitionEn || source.short_definition_en || '').trim();
  const zh = String(coreSense.zh || source.shortDefinitionZh || source.short_definition_zh || '').trim();
  return en || zh ? { ...coreSense, en, zh } : null;
}

async function filterProgressByWordbook(rows, wordbookId) {
  if (!wordbookId || !rows.length) return rows;

  const relationIds = rows
    .map(row => row.wordId)
    .filter(Boolean)
    .map(wordId => `${wordbookId}:${wordId}`);
  const memberships = [];

  for (const ids of chunk(Array.from(new Set(relationIds)))) {
    const result = await db.collection('wordbook_words')
      .where({ _id: _.in(ids) })
      .limit(ids.length)
      .get();
    memberships.push(...(result.data || []));
  }

  const memberWordIds = new Set(memberships.map(item => item.wordId));
  return rows
    .filter(row => memberWordIds.has(row.wordId))
    .map(row => ({
      ...row,
      bookIds: Array.from(new Set([
        ...(Array.isArray(row.bookIds) ? row.bookIds : []),
        wordbookId
      ]))
    }));
}

function getDateKeyAsiaShanghai(ms = Date.now()) {
  return new Date(numberOrDefault(ms, Date.now()) + SHANGHAI_OFFSET_MS)
    .toISOString()
    .slice(0, 10);
}

function getStartOfDayAsiaShanghai(ms = Date.now()) {
  const shifted = new Date(numberOrDefault(ms, Date.now()) + SHANGHAI_OFFSET_MS);
  return Date.UTC(
    shifted.getUTCFullYear(),
    shifted.getUTCMonth(),
    shifted.getUTCDate()
  ) - SHANGHAI_OFFSET_MS;
}

function getReviewDueAtAsiaShanghai(ms = Date.now(), intervalDays = 1) {
  const days = Math.max(1, Math.round(numberOrDefault(intervalDays, 1)));
  return getStartOfDayAsiaShanghai(ms) + days * DAY_MS;
}

function getReviewCutoffAsiaShanghai(ms = Date.now()) {
  return getStartOfDayAsiaShanghai(ms) + DAY_MS - 1;
}

function getDailyPassState(prev = {}, result, mode, now = Date.now()) {
  const dateKey = getDateKeyAsiaShanghai(now);
  if (mode !== 'daily') {
    return {
      passedToday: false,
      dailyDoneDateKey: prev.dailyDoneDateKey || '',
      dailyWrongDateKey: prev.dailyWrongDateKey || '',
      dailyRecoveryCorrectCount: numberOrDefault(prev.dailyRecoveryCorrectCount, 0)
    };
  }

  if (prev.dailyDoneDateKey === dateKey) {
    return {
      passedToday: true,
      dailyDoneDateKey: dateKey,
      dailyWrongDateKey: prev.dailyWrongDateKey || '',
      dailyRecoveryCorrectCount: numberOrDefault(prev.dailyRecoveryCorrectCount, 0)
    };
  }

  if (result === 'unknown') {
    return {
      passedToday: false,
      dailyDoneDateKey: prev.dailyDoneDateKey === dateKey ? '' : (prev.dailyDoneDateKey || ''),
      dailyWrongDateKey: dateKey,
      dailyRecoveryCorrectCount: 0
    };
  }

  if (prev.dailyWrongDateKey === dateKey) {
    const dailyRecoveryCorrectCount = numberOrDefault(prev.dailyRecoveryCorrectCount, 0) + 1;
    const passedToday = dailyRecoveryCorrectCount >= DAILY_RECOVERY_REQUIRED;
    return {
      passedToday,
      dailyDoneDateKey: passedToday ? dateKey : (prev.dailyDoneDateKey === dateKey ? '' : (prev.dailyDoneDateKey || '')),
      dailyWrongDateKey: dateKey,
      dailyRecoveryCorrectCount
    };
  }

  return {
    passedToday: true,
    dailyDoneDateKey: dateKey,
    dailyWrongDateKey: prev.dailyWrongDateKey || '',
    dailyRecoveryCorrectCount: numberOrDefault(prev.dailyRecoveryCorrectCount, 0)
  };
}

function getNextProgress(prev = {}, result, now = Date.now()) {
  let correctCount = numberOrDefault(prev.correctCount, 0);
  let wrongCount = numberOrDefault(prev.wrongCount, 0);
  let streakCorrect = numberOrDefault(prev.streakCorrect, 0);
  let interval = numberOrDefault(prev.interval, 0);
  let nextReviewAt = numberOrDefault(prev.nextReviewAt, 0);
  let status = 'learning';

  if (result === 'known') {
    correctCount += 1;
    streakCorrect += 1;
    const day = CORRECT_INTERVAL_DAYS[Math.min(streakCorrect - 1, CORRECT_INTERVAL_DAYS.length - 1)];
    interval = day * 24 * 60;
    nextReviewAt = getReviewDueAtAsiaShanghai(now, day);
    status = streakCorrect >= 5 ? 'mastered' : 'reviewing';
  } else {
    wrongCount += 1;
    streakCorrect = 0;
    status = wrongCount >= 3 ? 'difficult' : 'learning';
  }

  return { interval, nextReviewAt, correctCount, wrongCount, streakCorrect, status };
}

function mapWord(word = {}, progress = {}, learningContent = {}) {
  const coreSense = normalizeCoreSense(learningContent);
  return {
    wordId: word._id || progress.wordId,
    bookId: progress.bookId || progress.lastReviewedBookId || '',
    word: word.word || progress.word || progress.normalized || '',
    normalized: word.normalized || progress.normalized || '',
    type: word.type || 'word',
    phonetic: word.phonetic || {},
    senses: Array.isArray(word.senses) ? word.senses : [],
    audio: word.audio || null,
    audioPolicy: word.audioPolicy || null,
    coreSense,
    shortDefinitionEn: coreSense ? coreSense.en : '',
    shortDefinitionZh: coreSense ? coreSense.zh : '',
    progress: {
      status: normalizeStatus(progress.status),
      nextReviewAt: progress.nextReviewAt || 0,
      correctCount: progress.correctCount || 0,
      wrongCount: progress.wrongCount || 0,
      streakCorrect: progress.streakCorrect || 0,
      lastResult: progress.lastResult || '',
      favorite: Boolean(progress.favorite),
      favoritedAt: progress.favoritedAt || null,
      ignoredAt: progress.ignoredAt || null,
      dailyDoneDateKey: progress.dailyDoneDateKey || '',
      dailyWrongDateKey: progress.dailyWrongDateKey || '',
      dailyRecoveryCorrectCount: progress.dailyRecoveryCorrectCount || 0
    }
  };
}

function normalizeRecord(record = {}) {
  const normalized = String(record.normalized || record.word || '').trim().toLowerCase();
  const wordId = record.wordId || wordIdFor(normalized);
  const result = record.lastResult || record.result || '';

  if (!wordId || !normalized || !RESULT_VALUES.includes(result)) return null;
  if (String(wordId).length > 160 || normalized.length > 160) return null;

  const now = Date.now();
  const requestedUpdatedAt = numberOrDefault(record.clientUpdatedAt || record.updatedAt, now);
  const clientUpdatedAt = Math.min(requestedUpdatedAt, now + 5 * 60 * 1000);

  return {
    wordId,
    word: String(record.word || normalized).slice(0, 160),
    normalized,
    bookId: String(record.bookId || record.lastReviewedBookId || '').trim().slice(0, 80),
    mode: record.mode === 'daily' ? 'daily' : 'review',
    easiness: numberOrDefault(record.easiness, 2.5),
    interval: numberOrDefault(record.interval, 0),
    nextReviewAt: numberOrDefault(record.nextReviewAt, 0),
    correctCount: numberOrDefault(record.correctCount, 0),
    wrongCount: numberOrDefault(record.wrongCount, 0),
    streakCorrect: numberOrDefault(record.streakCorrect, 0),
    status: normalizeStatus(record.status),
    lastResult: result,
    favorite: typeof record.favorite === 'boolean' ? record.favorite : undefined,
    favoritedAt: record.favoritedAt === null ? null : numberOrDefault(record.favoritedAt, undefined),
    ignoredAt: record.ignoredAt === null ? null : numberOrDefault(record.ignoredAt, undefined),
    dailyDoneDateKey: String(record.dailyDoneDateKey || '').trim().slice(0, 10),
    dailyWrongDateKey: String(record.dailyWrongDateKey || '').trim().slice(0, 10),
    dailyRecoveryCorrectCount: numberOrDefault(record.dailyRecoveryCorrectCount, 0),
    advanceSrs: record.advanceSrs !== false,
    clientUpdatedAt
  };
}

async function upsertProgress(openid, rawRecord) {
  const record = normalizeRecord(rawRecord);
  if (!record) {
    return { ok: false, code: 'BAD_RECORD' };
  }

  const id = `${openid}:${record.wordId}`;
  const now = db.serverDate();
  const ref = db.collection('user_word_progress').doc(id);
  const existing = await ref.get().then(result => result.data || null).catch(() => null);
  const existingClientUpdatedAt = numberOrDefault(existing && existing.clientUpdatedAt, 0);
  if (existing && (
    existingClientUpdatedAt > record.clientUpdatedAt
    || (existingClientUpdatedAt === record.clientUpdatedAt && existing.lastResult === record.lastResult)
  )) {
    return { ok: true, id, wordId: record.wordId, skipped: true };
  }

  if (!existing) {
    const wordExists = await db.collection('words').doc(record.wordId).get()
      .then(result => Boolean(result.data))
      .catch(() => false);
    if (!wordExists) return { ok: false, code: 'WORD_NOT_FOUND', wordId: record.wordId };
  }

  const nextProgress = record.advanceSrs
    ? getNextProgress(existing || {}, record.lastResult, record.clientUpdatedAt)
    : {
      interval: numberOrDefault(existing && existing.interval, 0),
      nextReviewAt: numberOrDefault(existing && existing.nextReviewAt, 0),
      correctCount: numberOrDefault(existing && existing.correctCount, 0),
      wrongCount: numberOrDefault(existing && existing.wrongCount, 0),
      streakCorrect: numberOrDefault(existing && existing.streakCorrect, 0),
      status: normalizeStatus(existing && existing.status, 'learning')
    };
  const computedDailyPassState = getDailyPassState(existing || {}, record.lastResult, record.mode, record.clientUpdatedAt);
  const dailyPassState = record.mode === 'daily' && (
    record.dailyDoneDateKey
    || record.dailyWrongDateKey
    || record.dailyRecoveryCorrectCount
  )
    ? {
      dailyDoneDateKey: record.dailyDoneDateKey || '',
      dailyWrongDateKey: record.dailyWrongDateKey || '',
      dailyRecoveryCorrectCount: record.dailyRecoveryCorrectCount || 0
    }
    : computedDailyPassState;
  const data = {
    userId: openid,
    accountId: openid,
    wordId: record.wordId,
    word: record.word,
    normalized: record.normalized,
    bookId: record.bookId,
    lastReviewedBookId: record.bookId,
    easiness: numberOrDefault(existing && existing.easiness, 2.5),
    interval: nextProgress.interval,
    nextReviewAt: nextProgress.nextReviewAt,
    correctCount: nextProgress.correctCount,
    wrongCount: nextProgress.wrongCount,
    streakCorrect: nextProgress.streakCorrect,
    status: nextProgress.status,
    lastResult: record.lastResult,
    dailyDoneDateKey: dailyPassState.dailyDoneDateKey,
    dailyWrongDateKey: dailyPassState.dailyWrongDateKey,
    dailyRecoveryCorrectCount: dailyPassState.dailyRecoveryCorrectCount,
    clientUpdatedAt: record.clientUpdatedAt,
    lastReviewedAt: now,
    updatedAt: now
  };

  data.bookIds = Array.from(new Set([
    ...((existing && Array.isArray(existing.bookIds)) ? existing.bookIds : []),
    record.bookId
  ].filter(Boolean)));

  if (existing) {
    await ref.update({ data });
  } else {
    await ref.set({
      data: {
        ...data,
        createdAt: now
      }
    });
  }

  const dateKey = getDateKeyAsiaShanghai(record.clientUpdatedAt);
  const becameDoneToday = record.mode === 'daily'
    && dailyPassState.dailyDoneDateKey === dateKey
    && (!existing || existing.dailyDoneDateKey !== dateKey);
  await recordLearningActivity(openid, record, { becameDoneToday }).catch((err) => {
    console.warn('[learn-submit] activity write failed', err);
  });

  return { ok: true, id, wordId: record.wordId, created: !existing };
}

async function recordLearningActivity(openid, record, options = {}) {
  const wordbookId = String(record.bookId || '').trim().slice(0, 80);
  if (!wordbookId) return;
  await ensureLearningActivityCollection();

  const dateKey = getDateKeyAsiaShanghai(record.clientUpdatedAt);
  const id = `${openid}:${wordbookId}:${dateKey}`;
  const ref = db.collection('user_learning_activity').doc(id);
  const existing = await ref.get().then(result => result.data || null).catch(() => null);
  const isKnown = record.lastResult === 'known';
  const isReview = record.mode === 'review';
  const increments = {
    attempts: 1,
    correctAnswers: isKnown ? 1 : 0,
    wrongAnswers: isKnown ? 0 : 1,
    dailyAnswers: isReview ? 0 : 1,
    reviewAnswers: isReview ? 1 : 0,
    newLearned: options.becameDoneToday ? 1 : 0
  };
  const now = db.serverDate();

  if (existing) {
    await ref.update({
      data: {
        attempts: _.inc(increments.attempts),
        correctAnswers: _.inc(increments.correctAnswers),
        wrongAnswers: _.inc(increments.wrongAnswers),
        dailyAnswers: _.inc(increments.dailyAnswers),
        reviewAnswers: _.inc(increments.reviewAnswers),
        newLearned: _.inc(increments.newLearned),
        lastAnsweredAt: record.clientUpdatedAt,
        updatedAt: now
      }
    });
    return;
  }

  await ref.set({
    data: {
      userId: openid,
      accountId: openid,
      wordbookId,
      dateKey,
      ...increments,
      lastAnsweredAt: record.clientUpdatedAt,
      createdAt: now,
      updatedAt: now
    }
  });
}

async function submit(openid, event) {
  const records = Array.isArray(event.records)
    ? event.records
    : [event.record || event].filter(Boolean);

  if (!records.length || records.length > MAX_SUBMIT_RECORDS) {
    return fail('BAD_RECORD_COUNT', `records length must be between 1 and ${MAX_SUBMIT_RECORDS}.`);
  }

  const results = [];
  for (const record of records) {
    results.push(await upsertProgress(openid, record));
  }

  return ok({
    saved: results.filter(item => item.ok).length,
    results
  });
}

async function getLearnSession(openid, event) {
  const scope = normalizeSessionScope(event);
  if (!scope) return fail('BAD_SESSION_SCOPE', 'Invalid learn session scope.');
  await ensureLearnSessionCollection();

  const id = learnSessionId(openid, scope);
  const row = await db.collection('user_learn_sessions').doc(id).get()
    .then(result => result.data || null)
    .catch(() => null);

  if (!row) return ok({ session: null, clearedAt: 0 });
  return ok({
    session: row.cleared ? null : (row.session || null),
    completedHistory: normalizeCompletedHistory(row.completedHistory),
    clearedAt: row.cleared ? numberOrDefault(row.clientUpdatedAt, 0) : 0,
    clientUpdatedAt: numberOrDefault(row.clientUpdatedAt, 0)
  });
}

async function saveLearnSession(openid, event) {
  const scope = normalizeSessionScope(event);
  const session = event.session;
  if (!scope || !session || typeof session !== 'object' || Array.isArray(session)) {
    return fail('BAD_SESSION', 'Invalid learn session payload.');
  }
  await ensureLearnSessionCollection();

  let bytes = 0;
  try {
    bytes = Buffer.byteLength(JSON.stringify(session), 'utf8');
  } catch (err) {
    return fail('BAD_SESSION', 'Learn session must be serializable.');
  }
  if (bytes > MAX_SESSION_BYTES) {
    return fail('SESSION_TOO_LARGE', `Learn session exceeds ${MAX_SESSION_BYTES} bytes.`);
  }

  const id = learnSessionId(openid, scope);
  const ref = db.collection('user_learn_sessions').doc(id);
  const existing = await ref.get().then(result => result.data || null).catch(() => null);
  const clientUpdatedAt = normalizeClientUpdatedAt(event.clientUpdatedAt || session.savedAt);
  const existingUpdatedAt = numberOrDefault(existing && existing.clientUpdatedAt, 0);
  if (existing && existing.cleared && existingUpdatedAt >= clientUpdatedAt) {
    return ok({ saved: false, skipped: true, clientUpdatedAt: existing.clientUpdatedAt });
  }

  const mergedSession = existing && !existing.cleared
    ? mergeLearnSession(existing.session || {}, session, existingUpdatedAt, clientUpdatedAt)
    : session;
  const mergedUpdatedAt = Math.max(existingUpdatedAt, clientUpdatedAt);
  let mergedBytes = 0;
  try {
    mergedBytes = Buffer.byteLength(JSON.stringify(mergedSession), 'utf8');
  } catch (err) {
    return fail('BAD_SESSION', 'Learn session must be serializable.');
  }
  if (mergedBytes > MAX_SESSION_BYTES) {
    return fail('SESSION_TOO_LARGE', `Learn session exceeds ${MAX_SESSION_BYTES} bytes.`);
  }

  const now = db.serverDate();
  const data = {
    userId: openid,
    accountId: openid,
    ...scope,
    session: {
      ...mergedSession,
      bookId: scope.wordbookId,
      mode: scope.mode,
      dateKey: scope.dateKey,
      savedAt: mergedUpdatedAt
    },
    completedHistory: null,
    cleared: false,
    clientUpdatedAt: mergedUpdatedAt,
    updatedAt: now
  };
  if (existing) {
    await ref.update({ data });
  } else {
    await ref.set({ data: { ...data, createdAt: now } });
  }
  return ok({ saved: true, clientUpdatedAt: mergedUpdatedAt, session: data.session });
}

async function clearLearnSession(openid, event) {
  const scope = normalizeSessionScope(event);
  if (!scope) return fail('BAD_SESSION_SCOPE', 'Invalid learn session scope.');
  await ensureLearnSessionCollection();

  const id = learnSessionId(openid, scope);
  const ref = db.collection('user_learn_sessions').doc(id);
  const existing = await ref.get().then(result => result.data || null).catch(() => null);
  const clientUpdatedAt = normalizeClientUpdatedAt(event.clientUpdatedAt);
  if (existing && numberOrDefault(existing.clientUpdatedAt, 0) > clientUpdatedAt) {
    return ok({ cleared: false, skipped: true, clientUpdatedAt: existing.clientUpdatedAt });
  }

  const now = db.serverDate();
  const completedHistory = normalizeCompletedHistory(event.completedHistory)
    || normalizeCompletedHistory(existing && existing.session)
    || normalizeCompletedHistory(existing && existing.completedHistory);
  const data = {
    userId: openid,
    accountId: openid,
    ...scope,
    session: null,
    completedHistory,
    cleared: true,
    clientUpdatedAt,
    updatedAt: now
  };
  if (existing) {
    await ref.update({ data });
  } else {
    await ref.set({ data: { ...data, createdAt: now } });
  }
  return ok({ cleared: true, clientUpdatedAt });
}

async function listProgress(openid, event) {
  const limit = normalizeLimit(event.limit, PAGE_SIZE, MAX_PROGRESS_PAGE_SIZE);
  const wordbookId = String(event.wordbookId || event.bookId || '').trim().slice(0, 80);
  const records = [];
  let cursor = String(event.cursor || '');
  let hasMore = true;
  let scanned = 0;

  while (records.length < limit && hasMore && scanned < MAX_REVIEW_SCAN_ROWS) {
    const queryLimit = Math.min(PAGE_SIZE, limit - records.length);
    const where = cursor
      ? { userId: openid, wordId: _.gt(cursor) }
      : { userId: openid };
    const result = await db.collection('user_word_progress')
      .where(where)
      .orderBy('wordId', 'asc')
      .limit(queryLimit)
      .get();
    const rows = result.data || [];
    scanned += rows.length;
    records.push(...await filterProgressByWordbook(rows, wordbookId));
    if (rows.length) cursor = rows[rows.length - 1].wordId;
    hasMore = rows.length === queryLimit;
  }

  return ok({
    records,
    cursor: hasMore && cursor ? cursor : ''
  });
}

async function scanUserProgress(openid, maxRows = MAX_REVIEW_SCAN_ROWS) {
  const records = [];
  let cursor = '';
  let hasMore = true;

  while (records.length < maxRows && hasMore) {
    const queryLimit = Math.min(PAGE_SIZE, maxRows - records.length);
    const where = cursor
      ? { userId: openid, wordId: _.gt(cursor) }
      : { userId: openid };
    const result = await db.collection('user_word_progress')
      .where(where)
      .orderBy('wordId', 'asc')
      .limit(queryLimit)
      .get();
    const rows = result.data || [];
    records.push(...rows);
    if (rows.length) cursor = rows[rows.length - 1].wordId;
    hasMore = rows.length === queryLimit;
  }

  return records;
}

async function learningHistory(openid, event) {
  const wordbookId = String(event.wordbookId || event.bookId || '').trim().slice(0, 80);
  const days = normalizeLimit(event.days, 30, 90);
  const endDateKey = getDateKeyAsiaShanghai();
  const startDateKey = getDateKeyAsiaShanghai(Date.now() - (days - 1) * DAY_MS);
  await ensureLearningActivityCollection();

  const result = await db.collection('user_learning_activity')
    .where({ userId: openid })
    .limit(100)
    .get()
    .catch(() => ({ data: [] }));
  const dayMap = {};
  (result.data || [])
    .filter(row => (
      (!wordbookId || row.wordbookId === wordbookId)
      && row.dateKey >= startDateKey
      && row.dateKey <= endDateKey
    ))
    .forEach((row) => {
      dayMap[row.dateKey] = {
        dateKey: row.dateKey,
        attempts: numberOrDefault(row.attempts, 0),
        correctAnswers: numberOrDefault(row.correctAnswers, 0),
        wrongAnswers: numberOrDefault(row.wrongAnswers, 0),
        dailyAnswers: numberOrDefault(row.dailyAnswers, 0),
        reviewAnswers: numberOrDefault(row.reviewAnswers, 0),
        newLearned: numberOrDefault(row.newLearned, 0),
        difficultWords: 0
      };
    });

  // Progress rows provide a useful history baseline for users who learned before
  // per-answer activity tracking was introduced.
  const progressRows = await filterProgressByWordbook(await scanUserProgress(openid), wordbookId);
  const learnedByDate = {};
  const difficultByDate = {};
  progressRows.forEach((row) => {
    if (row.status === 'ignored') return;
    if (row.dailyDoneDateKey >= startDateKey && row.dailyDoneDateKey <= endDateKey) {
      if (!learnedByDate[row.dailyDoneDateKey]) learnedByDate[row.dailyDoneDateKey] = new Set();
      learnedByDate[row.dailyDoneDateKey].add(row.wordId);
    }
    if (row.dailyWrongDateKey >= startDateKey && row.dailyWrongDateKey <= endDateKey) {
      if (!difficultByDate[row.dailyWrongDateKey]) difficultByDate[row.dailyWrongDateKey] = new Set();
      difficultByDate[row.dailyWrongDateKey].add(row.wordId);
    }
  });
  Object.keys(learnedByDate).forEach((dateKey) => {
    if (!dayMap[dateKey]) dayMap[dateKey] = { dateKey };
    dayMap[dateKey].newLearned = Math.max(numberOrDefault(dayMap[dateKey].newLearned, 0), learnedByDate[dateKey].size);
  });
  Object.keys(difficultByDate).forEach((dateKey) => {
    if (!dayMap[dateKey]) dayMap[dateKey] = { dateKey };
    dayMap[dateKey].difficultWords = difficultByDate[dateKey].size;
  });

  return ok({
    days: Object.values(dayMap).sort((a, b) => a.dateKey.localeCompare(b.dateKey)),
    range: { startDateKey, endDateKey, days }
  });
}

function normalizeWordStatePatch(event = {}) {
  const wordId = event.wordId || wordIdFor(event.normalized || event.word);
  if (!wordId || String(wordId).length > 160) return null;

  const now = Date.now();
  const requestedUpdatedAt = numberOrDefault(event.clientUpdatedAt || event.updatedAt, now);

  const patch = {
    wordId,
    clientUpdatedAt: Math.min(requestedUpdatedAt, now + 5 * 60 * 1000)
  };

  if (typeof event.favorite === 'boolean') {
    patch.favorite = event.favorite;
    patch.favoritedAt = event.favorite
      ? numberOrDefault(event.favoritedAt, patch.clientUpdatedAt)
      : null;
  }

  if (typeof event.status === 'string') {
    if (event.status !== 'ignored') return null;
    patch.status = 'ignored';
    patch.ignoredAt = numberOrDefault(event.ignoredAt, patch.clientUpdatedAt);
  }

  if (event.ignoredAt === null) {
    patch.ignoredAt = null;
  }

  if (patch.favorite === undefined && !patch.status && patch.ignoredAt === undefined) return null;

  return patch;
}

async function updateWordState(openid, event) {
  const patch = normalizeWordStatePatch(event);
  if (!patch) {
    return fail('BAD_RECORD', 'Invalid word state payload.');
  }

  const id = `${openid}:${patch.wordId}`;
  const ref = db.collection('user_word_progress').doc(id);
  let existing = null;

  try {
    const result = await ref.get();
    existing = result.data || null;
  } catch (err) {
    existing = null;
  }

  if (!existing) {
    const wordExists = await db.collection('words').doc(patch.wordId).get()
      .then(result => Boolean(result.data))
      .catch(() => false);
    if (!wordExists) return fail('WORD_NOT_FOUND', `Word not found: ${patch.wordId}`);
  }

  if (existing && numberOrDefault(existing.clientUpdatedAt, 0) > patch.clientUpdatedAt) {
    return ok({
      record: {
        wordId: patch.wordId,
        favorite: Boolean(existing.favorite),
        favoritedAt: existing.favoritedAt || null,
        status: existing.status || 'learning',
        ignoredAt: existing.ignoredAt || null,
        updatedAt: existing.updatedAt || 0
      },
      skipped: true
    });
  }

  const now = db.serverDate();
  const data = {
    userId: openid,
    accountId: openid,
    wordId: patch.wordId,
    clientUpdatedAt: patch.clientUpdatedAt,
    updatedAt: now
  };

  const bookId = String(event.bookId || '').trim().slice(0, 80);
  if (bookId) {
    data.bookId = bookId;
    data.lastReviewedBookId = bookId;
    data.bookIds = Array.from(new Set([
      ...((existing && Array.isArray(existing.bookIds)) ? existing.bookIds : []),
      bookId
    ].filter(Boolean)));
  }

  if (patch.favorite !== undefined) {
    data.favorite = patch.favorite;
    data.favoritedAt = patch.favoritedAt;
  }

  if (patch.status) {
    data.status = patch.status;
  }

  if (patch.ignoredAt !== undefined) {
    data.ignoredAt = patch.ignoredAt;
    if (patch.ignoredAt === null && patch.status !== 'ignored') {
      const correctCount = existing ? numberOrDefault(existing.correctCount, 0) : 0;
      data.status = correctCount > 0 ? 'reviewing' : 'new';
      if (correctCount === 0) data.nextReviewAt = null;
    }
  }

  let updated = 0;
  try {
    const result = await ref.update({ data });
    updated = result && result.stats ? result.stats.updated : 0;
  } catch (err) {
    updated = 0;
  }

  if (!updated) {
    await ref.set({
      data: {
        ...data,
        normalized: String(event.normalized || '').trim().toLowerCase().slice(0, 160),
        word: String(event.word || event.normalized || '').trim().slice(0, 160),
        bookId: String(event.bookId || '').trim().slice(0, 80),
        lastReviewedBookId: String(event.bookId || '').trim().slice(0, 80),
        status: data.status || 'new',
        correctCount: 0,
        wrongCount: 0,
        streakCorrect: 0,
        interval: 0,
        nextReviewAt: null,
        lastResult: '',
        createdAt: now
      }
    });
  }

  return ok({
    record: {
      wordId: patch.wordId,
      favorite: data.favorite !== undefined ? data.favorite : Boolean(existing && existing.favorite),
      favoritedAt: data.favoritedAt !== undefined ? data.favoritedAt : (existing && existing.favoritedAt) || null,
      status: data.status || (existing && existing.status) || 'learning',
      ignoredAt: data.ignoredAt !== undefined ? data.ignoredAt : (existing && existing.ignoredAt) || null,
      updatedAt: Date.now()
    }
  });
}

async function review(openid, event) {
  const limit = normalizeLimit(event.limit);
  const now = numberOrDefault(event.now, Date.now());
  const reviewCutoff = getReviewCutoffAsiaShanghai(now);
  const progressRows = [];

  for (let offset = 0; offset < MAX_REVIEW_SCAN_ROWS && progressRows.length < limit; offset += PAGE_SIZE) {
    const result = await db.collection('user_word_progress')
      .where({ userId: openid, nextReviewAt: _.lte(reviewCutoff) })
      .orderBy('nextReviewAt', 'asc')
      .skip(offset)
      .limit(PAGE_SIZE)
      .get();
    const rows = result.data || [];
    progressRows.push(...rows.filter(item => item && item.status !== 'mastered' && item.status !== 'ignored'));
    if (rows.length < PAGE_SIZE) break;
  }

  progressRows.splice(limit);

  const wordIds = progressRows.map(item => item.wordId).filter(Boolean);
  if (!wordIds.length) {
    return ok({ items: [], total: 0 });
  }

  const [words, learningContents] = await Promise.all([
    fetchWordsByIds(wordIds),
    fetchLearningContentByWordIds(wordIds)
  ]);
  const wordMap = words.reduce((map, word) => {
    map[word._id] = word;
    return map;
  }, {});
  const learningContentMap = learningContents.reduce((map, content) => {
    const wordId = content.wordId || content._id;
    if (wordId) map[wordId] = content;
    return map;
  }, {});

  const items = progressRows
    .map(progress => mapWord(wordMap[progress.wordId], progress, learningContentMap[progress.wordId]))
    .filter(item => item.wordId && item.word);

  return ok({
    items,
    total: items.length
  });
}

async function listFavorites(openid, event) {
  const limit = normalizeLimit(event.limit, PAGE_SIZE, MAX_PROGRESS_PAGE_SIZE);
  const wordbookId = String(event.wordbookId || event.bookId || '').trim().slice(0, 80);
  const result = await db.collection('user_word_progress')
    .where({ userId: openid, favorite: true })
    .limit(limit)
    .get();
  const rows = (await filterProgressByWordbook(result.data || [], wordbookId))
    .sort((a, b) => numberOrDefault(b.favoritedAt, 0) - numberOrDefault(a.favoritedAt, 0));
  const wordIds = rows.map(item => item.wordId).filter(Boolean);
  const [words, learningContents] = await Promise.all([
    fetchWordsByIds(wordIds),
    fetchLearningContentByWordIds(wordIds)
  ]);
  const wordMap = words.reduce((map, word) => {
    map[word._id] = word;
    return map;
  }, {});
  const learningContentMap = learningContents.reduce((map, content) => {
    const wordId = content.wordId || content._id;
    if (wordId) map[wordId] = content;
    return map;
  }, {});

  return ok({
    items: rows
      .map(progress => mapWord(wordMap[progress.wordId], progress, learningContentMap[progress.wordId]))
      .filter(item => item.wordId && item.word),
    total: rows.length
  });
}

async function removeRows(collectionName, openid, scope) {
  let removed = 0;

  while (true) {
    const query = scope === 'all'
      ? db.collection(collectionName)
      : db.collection(collectionName).where({ userId: openid });
    const result = await query
      .limit(RESET_BATCH_SIZE)
      .get();
    const rows = result.data || [];
    if (!rows.length) break;

    await Promise.all(rows.map(row => (
      db.collection(collectionName).doc(row._id).remove()
    )));
    removed += rows.length;

    if (rows.length < RESET_BATCH_SIZE) break;
  }

  return removed;
}

async function resetUsers(openid, scope) {
  const patch = {
    onboarded: false,
    activeBookId: '',
    purpose: '',
    preferences: [],
    updatedAt: db.serverDate()
  };

  if (scope !== 'all') {
    await db.collection('users').doc(openid).update({ data: patch }).catch(() => null);
    return 1;
  }

  let updated = 0;
  for (let offset = 0; ; offset += RESET_BATCH_SIZE) {
    const result = await db.collection('users')
      .skip(offset)
      .limit(RESET_BATCH_SIZE)
      .get();
    const rows = result.data || [];
    if (!rows.length) break;

    await Promise.all(rows.map(row => (
      db.collection('users').doc(row._id).update({ data: patch }).catch(() => null)
    )));
    updated += rows.length;

    if (rows.length < RESET_BATCH_SIZE) break;
  }

  return updated;
}

async function resetProgress(openid, event) {
  if (event.confirm !== 'RESET_USER_WORD_PROGRESS') {
    return fail('CONFIRM_REQUIRED', 'Missing confirm token.');
  }

  const scope = event.scope === 'all' ? 'all' : 'currentUser';
  if (scope !== 'all' && !openid) {
    return fail('AUTH_REQUIRED', '缺少用户身份，请从小程序端调用。');
  }
  const removedByCollection = {};
  for (const collectionName of RESET_PROGRESS_COLLECTIONS) {
    removedByCollection[collectionName] = await removeRows(collectionName, openid, scope).catch(() => 0);
  }
  const removed = Object.values(removedByCollection).reduce((sum, value) => sum + value, 0);

  const resetUserProfile = event.resetUserProfile === true;
  const usersUpdated = resetUserProfile ? await resetUsers(openid, scope) : 0;

  return ok({
    scope,
    removed,
    removedByCollection,
    resetUserProfile,
    usersUpdated
  });
}

async function resetTodayProgress(openid, event) {
  if (event.confirm !== 'RESET_TODAY_LEARNING') {
    return fail('CONFIRM_REQUIRED', 'Missing confirm token.');
  }

  const dateKey = String(event.dateKey || getDateKeyAsiaShanghai()).trim().slice(0, 10);
  const wordbookId = String(event.wordbookId || event.bookId || '').trim().slice(0, 80);
  await ensureLearnSessionCollection();
  const seen = new Set();
  let updated = 0;

  async function clearRowsByField(field) {
    while (true) {
      const result = await db.collection('user_word_progress')
        .where({ userId: openid, [field]: dateKey })
        .limit(RESET_BATCH_SIZE)
        .get();
      const rows = result.data || [];
      if (!rows.length) break;

      await Promise.all(rows.map((row) => {
        if (seen.has(row._id)) return Promise.resolve();
        seen.add(row._id);
        updated += 1;
        return db.collection('user_word_progress').doc(row._id).update({
          data: {
            dailyDoneDateKey: '',
            dailyWrongDateKey: '',
            dailyRecoveryCorrectCount: 0,
            clientUpdatedAt: Date.now(),
            updatedAt: db.serverDate()
          }
        });
      }));

      if (rows.length < RESET_BATCH_SIZE) break;
    }
  }

  await clearRowsByField('dailyDoneDateKey');
  await clearRowsByField('dailyWrongDateKey');

  let sessionsCleared = 0;
  while (true) {
    const result = await db.collection('user_learn_sessions')
      .where({ userId: openid, dateKey, cleared: false })
      .limit(RESET_BATCH_SIZE)
      .get()
      .catch(() => ({ data: [] }));
    const rows = result.data || [];
    if (!rows.length) break;
    const clearedAt = Date.now();
    await Promise.all(rows.map(row => db.collection('user_learn_sessions').doc(row._id).update({
      data: {
        session: null,
        cleared: true,
        clientUpdatedAt: clearedAt,
        updatedAt: db.serverDate()
      }
    })));
    sessionsCleared += rows.length;
    if (rows.length < RESET_BATCH_SIZE) break;
  }

  let activityRowsCleared = 0;
  await ensureLearningActivityCollection();
  if (wordbookId) {
    const activityId = `${openid}:${wordbookId}:${dateKey}`;
    activityRowsCleared = await db.collection('user_learning_activity').doc(activityId).remove()
      .then(result => numberOrDefault(result && result.stats && result.stats.removed, 0))
      .catch(() => 0);
  } else {
    const activityResult = await db.collection('user_learning_activity')
      .where({ userId: openid, dateKey })
      .limit(RESET_BATCH_SIZE)
      .get()
      .catch(() => ({ data: [] }));
    const activityRows = activityResult.data || [];
    await Promise.all(activityRows.map(row => (
      db.collection('user_learning_activity').doc(row._id).remove().catch(() => null)
    )));
    activityRowsCleared = activityRows.length;
  }

  return ok({ dateKey, updated, sessionsCleared, activityRowsCleared });
}

// action: 'today' | 'review' | 'submit' | 'listProgress' | 'learningHistory' | 'getSession' | 'saveSession' | 'clearSession' | 'listFavorites' | 'updateWordState' | 'resetTodayProgress' | 'resetProgress'
exports.main = async (event, context) => {
  const { OPENID } = cloud.getWXContext();
  const { action } = event;

  try {
    if (action === 'resetProgress' && event.scope === 'all') {
      return await resetProgress(OPENID, event);
    }

    if (!OPENID) {
      return fail('AUTH_REQUIRED', '缺少用户身份，请从小程序端调用。');
    }

    if (action === 'today') {
      return ok({ words: [] });
    }

    if (action === 'listProgress') {
      return await listProgress(OPENID, event);
    }

    if (action === 'learningHistory') {
      return await learningHistory(OPENID, event);
    }

    if (action === 'review') {
      return await review(OPENID, event);
    }

    if (action === 'listFavorites') {
      return await listFavorites(OPENID, event);
    }

    if (action === 'submit') {
      return await submit(OPENID, event);
    }

    if (action === 'getSession') {
      return await getLearnSession(OPENID, event);
    }

    if (action === 'saveSession') {
      return await saveLearnSession(OPENID, event);
    }

    if (action === 'clearSession') {
      return await clearLearnSession(OPENID, event);
    }

    if (action === 'updateWordState') {
      return await updateWordState(OPENID, event);
    }

    if (action === 'resetProgress') {
      return await resetProgress(OPENID, event);
    }

    if (action === 'resetTodayProgress') {
      return await resetTodayProgress(OPENID, event);
    }

    return fail('UNKNOWN_ACTION', `Unknown action: ${action || ''}`);
  } catch (err) {
    console.error('[learn-submit]', err);
    return fail('INTERNAL_ERROR', err.message || 'Internal server error.');
  }
};
