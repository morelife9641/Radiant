import { getMetaAsync, getWordByWordAsync, getWordsByWordsAsync, getWordsPage } from '../../utils/wordbook-loader';
import { playFeedbackSound, playWord, stopAudio } from '../../utils/audio';
import { learnService } from '../../services/learn';
import { normalizeDailyGoal } from '../../config/index';
import { QUESTION_TYPES, buildQuestion } from '../../utils/question-builder';
import { markProgressSynced, mergeProgressRecords, shouldSyncProgress } from '../../utils/progress-store';
import {
  getDateKeyAsiaShanghai,
  getReviewDueAtAsiaShanghai,
  isReviewDueToday
} from '../../utils/date';
import { getUserLearningPreferences } from '../../utils/profile-cache';

const PROGRESS_KEY = (bookId) => `progress.${bookId}`;
const DEFAULT_WORDBOOK_ID = 'ielts_content_words';
const TODAY_KEY = (bookId) => `today.${bookId}.${getDateKeyAsiaShanghai()}`;
const TODAY_DONE_KEY = (bookId) => `todayDone.${bookId}.${getDateKeyAsiaShanghai()}`;
const LEARN_HISTORY_KEY = (bookId, mode) => `learnHistory.${bookId}.${mode || 'daily'}`;
const LEARN_SESSION_PREFIX = (bookId, mode) => `learnSession.${bookId}.${mode || 'daily'}.`;
const LEARN_SESSION_KEY = (bookId, mode) => `learnSession.${bookId}.${mode || 'daily'}.${getDateKeyAsiaShanghai()}`;
const LEARN_SESSION_CLEAR_KEY = (bookId, mode) => `learnSessionClear.${bookId}.${mode || 'daily'}.${getDateKeyAsiaShanghai()}`;
const LEARN_SESSION_SCHEMA_VERSION = 3;
const PROGRESS_OUTBOX_KEY = (bookId) => `progressOutbox.v1.${bookId}`;
const CORRECT_INTERVAL_DAYS = [1, 3, 7, 15, 30];
const DAILY_RECOVERY_REQUIRED = 3;
const RETRY_DELAY_QUESTIONS = 3;
const MAX_PROGRESS_SUBMIT_RECORDS = 20;
const progressFlushPromises = {};

function getNavTopPx() {
  const app = getApp();
  const g = app && app.globalData ? app.globalData : {};
  return Math.ceil(g.navBarHeightPx || ((g.statusBarHeight || 44) + 48)) + 8;
}

function loadProgress(bookId) {
  return wx.getStorageSync(PROGRESS_KEY(bookId)) || {};
}

function saveProgress(bookId, progress) {
  wx.setStorageSync(PROGRESS_KEY(bookId), progress);
}

function getWordKey(word) {
  return normalizeDoneKey(word && (word.normalized || word.word));
}

function getWordId(word) {
  return word && (word.wordId || word._id || word.id || '');
}

function getRetryQuestionType(retryCount, enableSpellingQuestions = false) {
  if (retryCount <= 1) return QUESTION_TYPES.WORD_TO_ZH;
  if (retryCount === 2) return QUESTION_TYPES.SENSE_TO_WORD;
  return enableSpellingQuestions ? QUESTION_TYPES.SPELLING : QUESTION_TYPES.DEFINITION_TO_WORD;
}

function normalizeDoneKey(value) {
  return String(value || '').trim().toLowerCase();
}

function createLearnQueueId(bookId, mode) {
  return [
    getDateKeyAsiaShanghai(),
    mode || 'daily',
    String(bookId || '').slice(0, 24),
    Date.now().toString(36),
    Math.random().toString(36).slice(2, 8)
  ].join(':');
}

function loadTodayDoneSet(bookId) {
  const values = wx.getStorageSync(TODAY_DONE_KEY(bookId)) || [];
  return new Set((Array.isArray(values) ? values : []).map(normalizeDoneKey).filter(Boolean));
}

function saveTodayDoneSet(bookId, doneSet) {
  wx.setStorageSync(TODAY_DONE_KEY(bookId), Array.from(doneSet).filter(Boolean));
}

function normalizeCount(value) {
  const count = Number(value);
  return Number.isFinite(count) ? Math.max(0, Math.round(count)) : 0;
}

function normalizeTargetTotal(targetTotal, knownCount = 0, fallback = 1) {
  const target = normalizeCount(targetTotal);
  const known = normalizeCount(knownCount);
  const base = target || normalizeCount(fallback) || 1;
  return Math.max(1, known, base);
}

function formatDailyProgress(knownCount, targetTotal) {
  const known = normalizeCount(knownCount);
  const target = normalizeTargetTotal(targetTotal, known);
  return {
    known,
    target,
    progressPercent: Math.min(100, Math.round((known / target) * 100)),
    barProgressText: `${known}/${target}`
  };
}

function formatQueueProgress(completedCount, totalCount, displayTotalCount) {
  const total = normalizeCount(displayTotalCount || totalCount);
  const completed = Math.min(normalizeCount(completedCount), total);
  return {
    completed,
    total,
    progressPercent: total ? Math.min(100, Math.round((completed / total) * 100)) : 0,
    barProgressText: `${completed}/${total}`
  };
}

function formatLearnProgress(mode, sessionKnown, sessionTarget, dailyBase = 0, dailyGoal = 0, dailySessionKnown = sessionKnown) {
  if (mode === 'daily') {
    return formatDailyProgress(
      normalizeCount(dailyBase) + normalizeCount(dailySessionKnown),
      normalizeDailyGoal(dailyGoal)
    );
  }
  return formatQueueProgress(sessionKnown, sessionTarget);
}

function getOrbLevel(progressPercent) {
  const percent = Number(progressPercent || 0);
  if (percent >= 100) return '100';
  if (percent >= 80) return '80';
  if (percent >= 60) return '60';
  if (percent >= 40) return '40';
  if (percent >= 20) return '20';
  return '0';
}

function getAnswerSummary(word = {}) {
  const sense = Array.isArray(word.senses) && word.senses[0] ? word.senses[0] : {};
  return String(word.translation || word.translationZh || sense.translation || sense.translationZh || '').trim();
}

function buildAnswerHistoryItem(word, result) {
  return {
    key: getGroupPassKey(word),
    word: word && word.word ? word.word : '',
    summary: getAnswerSummary(word),
    result,
    resultText: result === 'known' ? '正确' : '再记一下',
    correct: result === 'known'
  };
}

function appendFirstAnswerHistory(history = [], word, result) {
  const item = buildAnswerHistoryItem(word, result);
  const key = item.key || normalizeDoneKey(item.word);
  const exists = (Array.isArray(history) ? history : []).some((record) => {
    const recordKey = record && (record.key || normalizeDoneKey(record.word));
    return recordKey && recordKey === key;
  });
  return exists ? history : history.concat(item);
}

async function rebuildTodayAnswerHistory(bookId, progress = {}) {
  const dateKey = getDateKeyAsiaShanghai();
  const rows = Object.entries(progress)
    .map(([key, value]) => ({ key, value: value || {} }))
    .filter(({ value }) => {
      const belongsToBook = !value.bookId
        || value.bookId === bookId
        || (Array.isArray(value.bookIds) && value.bookIds.includes(bookId));
      return belongsToBook
        && !isIgnoredProgress(value)
        && (value.dailyDoneDateKey === dateKey || value.dailyWrongDateKey === dateKey);
    })
    .sort((a, b) => normalizeCount(a.value.clientUpdatedAt || a.value.updatedAt)
      - normalizeCount(b.value.clientUpdatedAt || b.value.updatedAt));
  if (!rows.length) return { answerHistory: [], stats: { known: 0, unknown: 0 } };

  const normalizedWords = rows.map(({ key, value }) => value.normalized || value.word || key);
  const loadedWords = [];
  for (let index = 0; index < normalizedWords.length; index += 50) {
    const chunkWords = await getWordsByWordsAsync(bookId, normalizedWords.slice(index, index + 50)).catch(() => []);
    loadedWords.push(...chunkWords);
  }
  const wordMap = new Map(loadedWords.map(word => [getWordKey(word), word]));
  const answerHistory = rows.map(({ key, value }) => {
    const normalized = normalizeDoneKey(value.normalized || value.word || key);
    const word = wordMap.get(normalized) || {
      wordId: value.wordId || '',
      _id: value.wordId || '',
      word: value.word || normalized,
      normalized
    };
    return buildAnswerHistoryItem(word, value.dailyWrongDateKey === dateKey ? 'unknown' : 'known');
  });
  return {
    answerHistory,
    stats: {
      known: rows.filter(({ value }) => value.dailyDoneDateKey === dateKey).length,
      unknown: rows.filter(({ value }) => value.dailyWrongDateKey === dateKey).length
    }
  };
}

function getCorrectAnswerText(question = {}) {
  const answer = question.answer || {};
  if (answer.text) return answer.text;
  if (answer.value) return answer.value;
  const correctChoice = (question.choices || []).find(choice => choice && choice.correct);
  return correctChoice ? (correctChoice.text || '') : '';
}

function loadLastAnswerHistory(bookId, mode) {
  const value = wx.getStorageSync(LEARN_HISTORY_KEY(bookId, mode)) || {};
  return {
    answerHistory: Array.isArray(value.answerHistory) ? value.answerHistory : [],
    stats: value.stats || { known: 0, unknown: 0 }
  };
}

function saveLastAnswerHistory(bookId, mode, answerHistory = [], stats = {}) {
  if (!bookId || !answerHistory.length) return;
  wx.setStorageSync(LEARN_HISTORY_KEY(bookId, mode), {
    answerHistory,
    stats,
    savedAt: Date.now()
  });
}

function clearLastAnswerHistory(bookId, mode) {
  if (!bookId) return;
  wx.removeStorageSync(LEARN_HISTORY_KEY(bookId, mode));
}

function normalizeCompletedHistory(value = {}) {
  if (!value || typeof value !== 'object' || Array.isArray(value)) return null;
  const answerHistory = Array.isArray(value.answerHistory) ? value.answerHistory : [];
  if (!answerHistory.length) return null;
  return {
    answerHistory,
    stats: value.stats || { known: 0, unknown: 0 },
    completedAt: normalizeCount(value.completedAt) || Date.now()
  };
}

function createCompletedHistory(answerHistory = [], stats = {}) {
  return normalizeCompletedHistory({ answerHistory, stats, completedAt: Date.now() });
}

function cacheCompletedHistory(bookId, mode, remoteHistory) {
  const remote = normalizeCompletedHistory(remoteHistory);
  if (!remote) return;
  const local = loadLastAnswerHistory(bookId, mode);
  const answerHistory = mergeSessionAnswerHistory(local.answerHistory, remote.answerHistory);
  const stats = {
    known: Math.max(normalizeCount(local.stats && local.stats.known), normalizeCount(remote.stats && remote.stats.known)),
    unknown: Math.max(normalizeCount(local.stats && local.stats.unknown), normalizeCount(remote.stats && remote.stats.unknown))
  };
  saveLastAnswerHistory(bookId, mode, answerHistory, stats);
}

function loadLearnSession(bookId, mode) {
  const value = wx.getStorageSync(LEARN_SESSION_KEY(bookId, mode)) || null;
  if (!value || value.dateKey !== getDateKeyAsiaShanghai()) return null;
  if (value.bookId !== bookId || value.mode !== mode) return null;
  if (value.schemaVersion !== LEARN_SESSION_SCHEMA_VERSION) return null;
  if (!Array.isArray(value.words) || !value.words.length) return null;
  return hydrateLearnSession(value);
}

function getLearnSessionTime(session) {
  return normalizeCount(session && (session.savedAt || session.clientUpdatedAt));
}

function compactLearnWord(word) {
  if (!word) return null;
  const sense = Array.isArray(word.senses) && word.senses[0] ? word.senses[0] : null;
  const compactSense = sense ? {
    senseId: sense.senseId || '',
    pos: sense.pos || '',
    translation: sense.translation || ''
  } : null;
  return {
    wordId: word.wordId || word._id || word.id || '',
    _id: word._id || word.wordId || word.id || '',
    id: word.id || word.wordId || word._id || '',
    bookId: word.bookId || '',
    word: word.word || '',
    normalized: word.normalized || normalizeDoneKey(word.word),
    type: word.type || 'word',
    phonetic: word.phonetic || '',
    senses: compactSense ? [compactSense] : [],
    audio: word.audio || null,
    audioPolicy: word.audioPolicy || null,
    coreSense: word.coreSense && typeof word.coreSense === 'object' ? word.coreSense : null,
    shortDefinitionEn: word.shortDefinitionEn || word.short_definition_en || '',
    shortDefinitionZh: word.shortDefinitionZh || word.short_definition_zh || '',
    _learnSource: word._learnSource || '',
    _learnRetryType: word._learnRetryType || '',
    _learnRecoveryStep: normalizeCount(word._learnRecoveryStep),
    _learnRecoveryPassed: normalizeCount(word._learnRecoveryPassed)
  };
}

function compactLearnSession(session = {}) {
  const compact = { ...session };
  delete compact.choicePool;
  compact.words = Array.isArray(session.words) ? session.words.map(compactLearnWord).filter(Boolean) : [];
  compact.currentWord = compactLearnWord(session.currentWord);
  if (compact.pendingNextState) {
    compact.pendingNextState = { ...compact.pendingNextState };
    delete compact.pendingNextState.words;
    compact.pendingNextState.currentWord = compactLearnWord(compact.pendingNextState.currentWord);
  }
  return compact;
}

function hydrateLearnSession(session = {}) {
  const questionWords = [
    ...(Array.isArray(session.words) ? session.words : []),
    ...(Array.isArray(session.choicePool) ? session.choicePool : [])
  ];
  const hydrated = {
    ...session,
    currentQuestion: normalizeCachedQuestion(session.currentQuestion, questionWords)
  };
  if (hydrated.pendingNextState && !hydrated.pendingNextState.words) {
    hydrated.pendingNextState = {
      ...hydrated.pendingNextState,
      words: Array.isArray(hydrated.words) ? hydrated.words : [],
      currentQuestion: normalizeCachedQuestion(hydrated.pendingNextState.currentQuestion, questionWords)
    };
  } else if (hydrated.pendingNextState) {
    hydrated.pendingNextState = {
      ...hydrated.pendingNextState,
      currentQuestion: normalizeCachedQuestion(hydrated.pendingNextState.currentQuestion, questionWords)
    };
  }
  return hydrated;
}

function mergeSessionNumberMaps(first = {}, second = {}) {
  const merged = { ...first };
  Object.keys(second || {}).forEach((key) => {
    merged[key] = Math.max(normalizeCount(merged[key]), normalizeCount(second[key]));
  });
  return merged;
}

function mergeSessionAnswerHistory(first = [], second = []) {
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

function mergeSessionWords(primary = [], secondary = []) {
  const merged = [];
  const seen = new Set();
  [...(primary || []), ...(secondary || [])].forEach((word) => {
    const key = getGroupPassKey(word);
    if (!key || seen.has(key)) return;
    seen.add(key);
    merged.push(word);
  });
  return merged;
}

function getCurrentQueuePassedKeys(words = [], passedKeys = []) {
  const queueKeys = new Set((Array.isArray(words) ? words : []).map(getGroupPassKey).filter(Boolean));
  return new Set((Array.isArray(passedKeys) ? passedKeys : Array.from(passedKeys || []))
    .filter(key => queueKeys.has(key)));
}

function getNextSessionIndex(words = [], passedKeys, preferredIndex = 0) {
  if (!words.length) return 0;
  const start = Math.min(normalizeCount(preferredIndex), words.length - 1);
  for (let offset = 0; offset < words.length; offset += 1) {
    const index = (start + offset) % words.length;
    if (!passedKeys.has(getGroupPassKey(words[index]))) return index;
  }
  return start;
}

function mergeLearnSessions(local, remote) {
  const localTime = getLearnSessionTime(local);
  const remoteTime = getLearnSessionTime(remote);
  const preferred = remoteTime >= localTime ? remote : local;
  const secondary = preferred === remote ? local : remote;
  const preferredQueueId = String(preferred.queueId || '');
  const secondaryQueueId = String(secondary.queueId || '');
  if (preferredQueueId !== secondaryQueueId && (preferredQueueId || secondaryQueueId)) {
    return { ...preferred, savedAt: Date.now() };
  }
  const mergedPassedKeys = [
    ...(Array.isArray(preferred.groupPassedKeys) ? preferred.groupPassedKeys : []),
    ...(Array.isArray(secondary.groupPassedKeys) ? secondary.groupPassedKeys : [])
  ].filter(Boolean);
  const words = mergeSessionWords(preferred.words, secondary.words);
  const groupPassedKeys = getCurrentQueuePassedKeys(words, mergedPassedKeys);
  const index = getNextSessionIndex(words, groupPassedKeys, preferred.index);
  const currentWord = words[index] || null;
  const keepsCurrentQuestion = getGroupPassKey(preferred.currentWord) === getGroupPassKey(currentWord);
  const stats = {
    ...(preferred.stats || {}),
    known: groupPassedKeys.size,
    unknown: Math.max(normalizeCount(preferred.stats && preferred.stats.unknown), normalizeCount(secondary.stats && secondary.stats.unknown))
  };

  return {
    ...preferred,
    words,
    index,
    total: words.length,
    targetTotal: Math.max(normalizeCount(preferred.targetTotal), normalizeCount(secondary.targetTotal), words.length),
    currentWord,
    currentQuestion: keepsCurrentQuestion ? preferred.currentQuestion : null,
    answered: keepsCurrentQuestion ? Boolean(preferred.answered) : false,
    pendingNextState: keepsCurrentQuestion ? preferred.pendingNextState : null,
    groupPassedKeys: Array.from(groupPassedKeys),
    groupRecoveryCount: mergeSessionNumberMaps(preferred.groupRecoveryCount, secondary.groupRecoveryCount),
    todayRetryCount: mergeSessionNumberMaps(preferred.todayRetryCount, secondary.todayRetryCount),
    answerHistory: mergeSessionAnswerHistory(preferred.answerHistory, secondary.answerHistory),
    stats,
    dailyProgressBase: Math.max(normalizeCount(preferred.dailyProgressBase), normalizeCount(secondary.dailyProgressBase)),
    dailyQueueKnown: countDailyQueuePassedWords(words, groupPassedKeys),
    savedAt: Date.now()
  };
}

function getCoreSenseZh(word) {
  const coreSense = word && word.coreSense && typeof word.coreSense === 'object'
    ? word.coreSense
    : {};
  return String(
    coreSense.zh
    || (word && (word.shortDefinitionZh || word.short_definition_zh))
    || ''
  ).trim();
}

function normalizeCachedQuestion(question, words = []) {
  if (!question) return question;

  let normalizedQuestion = question;
  if (question.type === QUESTION_TYPES.DEFINITION_TO_WORD) {
    const prompt = question.prompt || {};
    const text = String(prompt.text || '').replace(/\\n/g, '\n')
      .split(/\r?\n/)
      .map(item => item.trim())
      .find(Boolean) || '';
    normalizedQuestion = {
      ...normalizedQuestion,
      prompt: {
        ...prompt,
        text
      }
    };
  }

  if (question.type !== QUESTION_TYPES.SENSE_TO_WORD && question.type !== QUESTION_TYPES.DEFINITION_TO_WORD) {
    return normalizedQuestion;
  }

  const wordMap = new Map(
    (Array.isArray(words) ? words : [])
      .filter(Boolean)
      .map(word => [String(getWordId(word) || '').trim(), word])
      .filter(([wordId]) => wordId)
  );
  const choices = (question.choices || []).map(choice => {
    const word = wordMap.get(String(choice.wordId || choice.value || '').trim());
    const translationText = getCoreSenseZh(word);
    return translationText && translationText !== choice.translationText
      ? { ...choice, translationText }
      : choice;
  });

  return { ...normalizedQuestion, choices };
}

function syncLearnSessionToCloud(bookId, mode, session) {
  const dateKey = getDateKeyAsiaShanghai();
  const savedAt = getLearnSessionTime(session) || Date.now();
  wx.removeStorageSync(LEARN_SESSION_CLEAR_KEY(bookId, mode));
  learnService.saveSession(bookId, mode, dateKey, compactLearnSession(session), savedAt)
    .catch(err => console.warn('[learn] sync session failed', err));
}

function normalizePendingSessionClear(value) {
  if (value && typeof value === 'object') {
    return {
      clearedAt: normalizeCount(value.clearedAt),
      completedHistory: normalizeCompletedHistory(value.completedHistory)
    };
  }
  return { clearedAt: normalizeCount(value), completedHistory: null };
}

function pushLearnSessionClear(bookId, mode, pendingValue) {
  const clearKey = LEARN_SESSION_CLEAR_KEY(bookId, mode);
  const pending = normalizePendingSessionClear(pendingValue);
  if (!pending.clearedAt) return Promise.resolve(null);
  wx.setStorageSync(clearKey, pending);
  return learnService.clearSession(
    bookId,
    mode,
    getDateKeyAsiaShanghai(),
    pending.clearedAt,
    pending.completedHistory
  )
    .then((res) => {
      const stored = normalizePendingSessionClear(wx.getStorageSync(clearKey));
      if (res && res.ok && stored.clearedAt <= pending.clearedAt) {
        wx.removeStorageSync(clearKey);
      }
      return res;
    })
    .catch((err) => {
      console.warn('[learn] clear session sync failed', err);
      return null;
    });
}

async function loadMergedLearnSession(bookId, mode) {
  const clearKey = LEARN_SESSION_CLEAR_KEY(bookId, mode);
  const pendingClear = normalizePendingSessionClear(wx.getStorageSync(clearKey));
  if (pendingClear.clearedAt) {
    await pushLearnSessionClear(bookId, mode, pendingClear);
    if (normalizePendingSessionClear(wx.getStorageSync(clearKey)).clearedAt) return null;
  }

  const local = loadLearnSession(bookId, mode);
  const res = await learnService.getSession(bookId, mode, getDateKeyAsiaShanghai()).catch((err) => {
    console.warn('[learn] load cloud session failed', err);
    return null;
  });
  if (!res || !res.ok) return local;
  cacheCompletedHistory(bookId, mode, res.completedHistory);

  const localTime = getLearnSessionTime(local);
  const clearedAt = Number(res.clearedAt || 0);
  if (clearedAt && clearedAt >= localTime) {
    wx.removeStorageSync(LEARN_SESSION_KEY(bookId, mode));
    return null;
  }

  const remote = res.session && hydrateLearnSession(res.session);
  const remoteValid = remote
    && remote.bookId === bookId
    && remote.mode === mode
    && remote.schemaVersion === LEARN_SESSION_SCHEMA_VERSION
    && remote.dateKey === getDateKeyAsiaShanghai()
    && Array.isArray(remote.words)
    && remote.words.length;
  if (!remoteValid) {
    if (local) syncLearnSessionToCloud(bookId, mode, local);
    return local;
  }

  if (local && remote) {
    const merged = mergeLearnSessions(local, remote);
    saveLearnSession(bookId, mode, merged, { syncCloud: true });
    return merged;
  }

  const remoteTime = getLearnSessionTime(remote);
  if (!local || remoteTime > localTime) {
    saveLearnSession(bookId, mode, remote, { syncCloud: false });
    return remote;
  }
  if (localTime > remoteTime) syncLearnSessionToCloud(bookId, mode, local);
  return local;
}

function loadPreviousLearnSession(bookId, mode) {
  if (!bookId || mode !== 'daily') return null;
  let keys = [];
  try {
    keys = (wx.getStorageInfoSync && wx.getStorageInfoSync().keys) || [];
  } catch (err) {
    console.warn('[learn] read storage keys failed', err);
    return null;
  }

  const today = getDateKeyAsiaShanghai();
  const prefix = LEARN_SESSION_PREFIX(bookId, mode);
  const sessions = keys
    .filter(key => key.startsWith(prefix) && key !== LEARN_SESSION_KEY(bookId, mode))
    .map((key) => {
      const value = wx.getStorageSync(key) || null;
      return value ? { key, value } : null;
    })
    .filter(Boolean)
    .filter(({ value }) => {
      return value
        && value.bookId === bookId
        && value.mode === mode
        && value.schemaVersion === LEARN_SESSION_SCHEMA_VERSION
        && value.dateKey
        && value.dateKey < today
        && !value.finished
        && Array.isArray(value.words)
        && value.words.length;
    })
    .sort((a, b) => {
      const dateCompare = String(b.value.dateKey).localeCompare(String(a.value.dateKey));
      if (dateCompare) return dateCompare;
      return normalizeCount(b.value.savedAt) - normalizeCount(a.value.savedAt);
    });
  return sessions[0] ? sessions[0].value : null;
}

function saveLearnSession(bookId, mode, session, options = {}) {
  if (!bookId || !session || session.finished || !session.currentWord) {
    clearLearnSession(bookId, mode, options);
    return null;
  }
  const savedSession = {
    ...session,
    bookId,
    mode,
    schemaVersion: LEARN_SESSION_SCHEMA_VERSION,
    dateKey: getDateKeyAsiaShanghai(),
    savedAt: getLearnSessionTime(session) || Date.now()
  };
  wx.setStorageSync(LEARN_SESSION_KEY(bookId, mode), savedSession);
  if (options.syncCloud !== false) syncLearnSessionToCloud(bookId, mode, savedSession);
  return savedSession;
}

function clearLearnSession(bookId, mode, options = {}) {
  if (!bookId) return;
  wx.removeStorageSync(LEARN_SESSION_KEY(bookId, mode));
  if (options.syncCloud !== false) {
    pushLearnSessionClear(bookId, mode, {
      clearedAt: Number(options.clientUpdatedAt || Date.now()),
      completedHistory: normalizeCompletedHistory(options.completedHistory)
    });
  }
}

function markTodayDone(bookId, word) {
  const key = normalizeDoneKey(getWordKey(word) || (word && word.word));
  if (!key) return;
  const doneSet = loadTodayDoneSet(bookId);
  doneSet.add(key);
  saveTodayDoneSet(bookId, doneSet);
}

function getDailyPassState(prev = {}, result, mode, now = Date.now()) {
  const dateKey = getDateKeyAsiaShanghai(now);
  const wasAlreadyDone = prev.dailyDoneDateKey === dateKey;
  if (mode !== 'daily') {
    return {
      passedToday: false,
      dailyDoneDateKey: prev.dailyDoneDateKey || '',
      dailyWrongDateKey: prev.dailyWrongDateKey || '',
      dailyRecoveryCorrectCount: normalizeCount(prev.dailyRecoveryCorrectCount)
    };
  }

  if (wasAlreadyDone) {
    return {
      passedToday: true,
      dailyDoneDateKey: dateKey,
      dailyWrongDateKey: prev.dailyWrongDateKey || '',
      dailyRecoveryCorrectCount: normalizeCount(prev.dailyRecoveryCorrectCount)
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
    const dailyRecoveryCorrectCount = normalizeCount(prev.dailyRecoveryCorrectCount) + 1;
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
    dailyRecoveryCorrectCount: normalizeCount(prev.dailyRecoveryCorrectCount)
  };
}

function unmarkTodayDone(bookId, word) {
  const key = normalizeDoneKey(getWordKey(word) || (word && word.word));
  if (!key) return;
  const doneSet = loadTodayDoneSet(bookId);
  if (!doneSet.delete(key)) return;
  saveTodayDoneSet(bookId, doneSet);
}

function isDoneToday(bookId, word, progress) {
  const key = normalizeDoneKey(getWordKey(word) || (word && word.word));
  if (!key) return false;
  const doneSet = loadTodayDoneSet(bookId);
  if (doneSet.has(key)) return true;
  const item = progress && progress[key];
  return Boolean(item && !isIgnoredProgress(item) && item.dailyDoneDateKey === getDateKeyAsiaShanghai());
}

function isIgnoredProgress(progress) {
  return progress && progress.status === 'ignored';
}

function getWordProgress(progress, word) {
  const key = getWordKey(word);
  return key ? (progress[key] || {}) : {};
}

function isReviewSourceWord(word) {
  return word && word._learnSource === 'review';
}

function withLearnSource(word, source) {
  return word ? { ...word, _learnSource: source } : word;
}

function getQueueWordIdentity(word) {
  return String(getWordId(word) || getWordKey(word) || '').trim().toLowerCase();
}

function getGroupPassKey(word) {
  return getQueueWordIdentity(word);
}

function countDailyQueuePassedWords(words = [], passedKeys = []) {
  const passed = passedKeys instanceof Set ? passedKeys : new Set(Array.isArray(passedKeys) ? passedKeys : []);
  const seen = new Set();
  return (Array.isArray(words) ? words : []).reduce((count, word) => {
    const key = getGroupPassKey(word);
    if (!key || seen.has(key) || isReviewSourceWord(word) || !passed.has(key)) return count;
    seen.add(key);
    return count + 1;
  }, 0);
}

function getSessionCarryoverWords(session, progress, bookId, limit) {
  if (!session || !Array.isArray(session.words) || !limit) return [];
  const passedKeys = new Set(Array.isArray(session.groupPassedKeys) ? session.groupPassedKeys : []);
  const startIndex = Math.min(normalizeCount(session.index), session.words.length);
  const orderedWords = session.words.slice(startIndex).concat(session.words.slice(0, startIndex));
  const seen = new Set();
  const result = [];

  for (const word of orderedWords) {
    const passKey = getGroupPassKey(word);
    const wordKey = getWordKey(word);
    if (!passKey || seen.has(passKey) || passedKeys.has(passKey)) continue;
    if (isReviewSourceWord(word)) continue;
    const p = wordKey ? progress[wordKey] : null;
    if (isIgnoredProgress(p) || isDoneToday(bookId, word, progress)) continue;
    seen.add(passKey);
    result.push(withLearnSource({
      ...word,
      _learnRetryType: '',
      _learnRecoveryStep: 0,
      _learnRecoveryPassed: 0
    }, 'carryover'));
    if (result.length >= limit) break;
  }

  return result;
}

function isDueReviewProgress(progress) {
  return Boolean(progress
    && isReviewDueToday(progress.nextReviewAt)
    && progress.status !== 'mastered'
    && !isIgnoredProgress(progress));
}

function hasProgressRecord(progress) {
  return Boolean(progress && typeof progress === 'object' && Object.keys(progress).length);
}

function isReviewWordDue(word, localProgress) {
  const local = getWordProgress(localProgress, word);
  if (hasProgressRecord(local)) return isDueReviewProgress(local);
  const remote = word && word.progress;
  return isDueReviewProgress(remote);
}

function countTodayDone(bookId, progress) {
  const todayWords = wx.getStorageSync(TODAY_KEY(bookId)) || [];
  const dateKey = getDateKeyAsiaShanghai();
  const doneWords = loadTodayDoneSet(bookId);

  todayWords.forEach((word) => {
    const key = normalizeDoneKey(word);
    const item = progress[key];
    if (item && !isIgnoredProgress(item) && item.dailyDoneDateKey === dateKey) {
      doneWords.add(key);
    }
  });

  for (const key of Object.keys(progress)) {
    const item = progress[key];
    const normalizedKey = normalizeDoneKey(key);
    if (!normalizedKey) continue;
    const belongsToBook = item && (
      !item.bookId
      || item.bookId === bookId
      || (Array.isArray(item.bookIds) && item.bookIds.includes(bookId))
    );
    if (belongsToBook && !isIgnoredProgress(item) && item.dailyDoneDateKey === dateKey) {
      doneWords.add(normalizedKey);
    }
  }

  return doneWords.size;
}

function getNextProgress(prev = {}, result, now = Date.now()) {
  let {
    easiness = 2.5,
    correctCount = 0,
    wrongCount = 0,
    streakCorrect = 0
  } = prev;

  let interval = normalizeCount(prev.interval);
  let nextReviewAt = prev.nextReviewAt || 0;
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

  return {
    easiness,
    interval,
    nextReviewAt,
    correctCount,
    wrongCount,
    streakCorrect,
    status
  };
}

async function loadMergedProgress(bookId, options = {}) {
  const local = loadProgress(bookId);
  if (!options.force && !shouldSyncProgress(bookId)) return local;
  const res = await learnService.listAllProgress(bookId).catch(() => null);
  const records = res && res.ok && Array.isArray(res.records) ? res.records : [];
  console.info('[learn] progress res', {
    ok: res ? res.ok : null,
    code: res && res.code,
    records: records.length,
    localRecords: Object.keys(local).length
  });
  if (!res || !res.ok) return local;
  markProgressSynced(bookId);
  if (!records.length) return local;

  const merged = mergeProgressRecords(local, records);

  saveProgress(bookId, merged);
  return merged;
}

function pickTodayWords(allWords, progress, dailyGoal, bookId) {
  // 优先选还没学过的
  const fresh = [];
  const learning = [];
  for (const w of allWords) {
    const p = progress[getWordKey(w)];
    if (isIgnoredProgress(p)) continue;
    if (isDueReviewProgress(p)) continue;
    if (bookId && isDoneToday(bookId, w, progress)) continue;
    if (!p) fresh.push(w);
    else if (p.status !== 'mastered') learning.push(w);
    if (fresh.length >= dailyGoal) break;
  }
  const picked = fresh.slice(0, dailyGoal);
  if (picked.length < dailyGoal) {
    picked.push(...learning.slice(0, dailyGoal - picked.length));
  }
  return picked;
}

function pickReviewWords(allWords, progress) {
  const due = [];
  for (const w of allWords) {
    const p = progress[getWordKey(w)];
    if (p && isReviewDueToday(p.nextReviewAt) && p.status !== 'mastered' && !isIgnoredProgress(p)) {
      due.push(w);
    }
  }
  return due;
}

function pickReviewWordKeys(progress, limit = 50) {
  const seen = new Set();
  const rows = Object.keys(progress)
    .filter((word) => {
      const p = progress[word];
      return p && isReviewDueToday(p.nextReviewAt) && p.status !== 'mastered' && !isIgnoredProgress(p);
    })
    .sort((a, b) => {
      const pa = progress[a] || {};
      const pb = progress[b] || {};
      return (pa.nextReviewAt || 0) - (pb.nextReviewAt || 0);
    });

  const picked = [];
  for (const word of rows) {
    const p = progress[word] || {};
    const id = String(p.wordId || p.normalized || p.word || word || '').trim().toLowerCase();
    if (!id || seen.has(id)) continue;
    seen.add(id);
    picked.push(word);
    if (picked.length >= limit) break;
  }
  return picked;
}

async function loadReviewWords(bookId, progress) {
  const res = await learnService.review({ limit: 50 }).catch(() => null);
  const dueWords = pickReviewWordKeys(progress);
  const localResults = dueWords.length
    ? await Promise.all(dueWords.map(word => getWordByWordAsync(bookId, word).catch(() => null)))
    : [];
  const cloudItems = res && res.ok && Array.isArray(res.items)
    ? res.items.filter(item => !isIgnoredProgress(item.progress))
    : [];

  const seen = new Set();
  const result = [...cloudItems, ...localResults]
    .filter(Boolean)
    .filter(word => isReviewWordDue(word, progress))
    .sort((a, b) => {
      const pa = getWordProgress(progress, a);
      const pb = getWordProgress(progress, b);
      return (pa.nextReviewAt || (a.progress && a.progress.nextReviewAt) || 0)
        - (pb.nextReviewAt || (b.progress && b.progress.nextReviewAt) || 0);
    })
    .filter((word) => {
      const id = getQueueWordIdentity(word);
      if (!id || seen.has(id)) return false;
      seen.add(id);
      return true;
    })
    .slice(0, 50);
  console.info('[learn] review res', {
    ok: res ? res.ok : null,
    code: res && res.code,
    cloudItems: cloudItems.length,
    localDueKeys: dueWords.length,
    queuedReviewCount: result.length,
    sample: result.slice(0, 5).map(word => ({
      word: word.word,
      wordId: getWordId(word),
      nextReviewAt: (getWordProgress(progress, word) || {}).nextReviewAt || (word.progress && word.progress.nextReviewAt) || 0
    }))
  });
  return result;
}

async function loadCandidateWords(bookId, progress, dailyGoal, mode) {
  const allWords = [];
  let cursor = '';

  for (let pageIndex = 0; pageIndex < 40; pageIndex += 1) {
    const page = await getWordsPage(bookId, { limit: 100, cursor });
    allWords.push(...page.items);

    const picked = mode === 'review'
      ? pickReviewWords(allWords, progress)
      : pickTodayWords(allWords, progress, dailyGoal, bookId);

    if (mode === 'daily' && picked.length >= dailyGoal) {
      return { words: picked, allWords };
    }

    cursor = page.cursor;
    if (!cursor) {
      return { words: picked, allWords };
    }
  }

  const picked = mode === 'review'
    ? pickReviewWords(allWords, progress)
    : pickTodayWords(allWords, progress, dailyGoal, bookId);

  return { words: picked, allWords };
}

function buildCurrentQuestion(word, distractorPool, mode, progress, forceType = '', enableSpellingQuestions = false, questionIndex = 0) {
  if (!word) return null;
  const questionMode = isReviewSourceWord(word) ? 'review' : mode;
  const requestedType = forceType || word._learnRetryType || '';
  const type = !enableSpellingQuestions && requestedType === QUESTION_TYPES.SPELLING ? '' : requestedType;
  const question = buildQuestion(word, distractorPool, {
    mode: questionMode,
    progress,
    type,
    enableSpellingQuestions,
    questionIndex
  });
  if (word._learnRecoveryStep) {
    question.meta = {
      ...(question.meta || {}),
      recoveryStep: word._learnRecoveryStep,
      recoveryPassed: normalizeCount(word._learnRecoveryPassed),
      recoveryTotal: DAILY_RECOVERY_REQUIRED
    };
  }
  return question;
}

function withRecoveryQuestionMeta(question, recoveryPassed) {
  if (!question || !question.meta || !question.meta.recoveryStep) return question;
  return {
    ...question,
    meta: {
      ...question.meta,
      recoveryPassed: Math.min(DAILY_RECOVERY_REQUIRED, normalizeCount(recoveryPassed))
    }
  };
}

function buildProgressCloudRecord(bookId, word, progress, result, answer = {}, advanceSrs = true) {
  return {
    bookId,
    wordId: getWordId(word) || progress.wordId,
    word: word.word,
    normalized: word.normalized || progress.normalized || word.word,
    result,
    lastResult: result,
    easiness: progress.easiness,
    interval: progress.interval,
    nextReviewAt: progress.nextReviewAt,
    correctCount: progress.correctCount,
    wrongCount: progress.wrongCount,
    streakCorrect: progress.streakCorrect,
    status: progress.status === 'ignored' ? 'ignored' : undefined,
    dailyDoneDateKey: progress.dailyDoneDateKey || '',
    dailyWrongDateKey: progress.dailyWrongDateKey || '',
    dailyRecoveryCorrectCount: progress.dailyRecoveryCorrectCount || 0,
    questionType: answer.type || '',
    questionId: answer.questionId || '',
    answerValue: answer.value || '',
    answerText: answer.answerText || '',
    correct: Boolean(answer.correct),
    favorite: progress.favorite,
    favoritedAt: progress.favoritedAt,
    ignoredAt: progress.ignoredAt,
    mode: progress.mode,
    advanceSrs,
    clientUpdatedAt: progress.clientUpdatedAt || progress.updatedAt
  };
}

function queueProgressCloudRecord(bookId, record) {
  const identity = String(record.wordId || record.normalized || '').trim().toLowerCase();
  if (!bookId || !identity) return;
  const outbox = wx.getStorageSync(PROGRESS_OUTBOX_KEY(bookId)) || {};
  const baseKey = `${identity}:${normalizeCount(record.clientUpdatedAt)}`;
  let key = baseKey;
  let suffix = 1;
  while (outbox[key]) {
    if (JSON.stringify(outbox[key]) === JSON.stringify(record)) return;
    key = `${baseKey}:${suffix}`;
    suffix += 1;
  }
  outbox[key] = record;
  wx.setStorageSync(PROGRESS_OUTBOX_KEY(bookId), outbox);
}

async function flushProgressOutbox(bookId) {
  if (!bookId) return false;
  if (progressFlushPromises[bookId]) return progressFlushPromises[bookId];

  progressFlushPromises[bookId] = (async () => {
    let flushedAny = false;
    while (true) {
      const outbox = wx.getStorageSync(PROGRESS_OUTBOX_KEY(bookId)) || {};
      const entries = Object.entries(outbox)
        .sort((a, b) => normalizeCount(a[1].clientUpdatedAt) - normalizeCount(b[1].clientUpdatedAt))
        .slice(0, MAX_PROGRESS_SUBMIT_RECORDS);
      if (!entries.length) break;

      const records = entries.map(([, record]) => record);
      const res = await learnService.submit(records).catch((err) => {
        console.warn('[learn] flush progress outbox failed', err);
        return null;
      });
      if (!res || !res.ok || !Array.isArray(res.results)) break;

      const current = wx.getStorageSync(PROGRESS_OUTBOX_KEY(bookId)) || {};
      let removed = 0;
      res.results.forEach((result, index) => {
        if (!result || !result.ok) return;
        const [key, sent] = entries[index] || [];
        const latest = key && current[key];
        if (latest && normalizeCount(latest.clientUpdatedAt) <= normalizeCount(sent.clientUpdatedAt)) {
          delete current[key];
          removed += 1;
        }
      });
      wx.setStorageSync(PROGRESS_OUTBOX_KEY(bookId), current);
      flushedAny = flushedAny || removed > 0;
      if (!removed) break;
    }
    return flushedAny;
  })().finally(() => {
    delete progressFlushPromises[bookId];
  });

  return progressFlushPromises[bookId];
}

function syncProgressToCloud(bookId, word, progress, result, answer = {}, advanceSrs = true) {
  queueProgressCloudRecord(bookId, buildProgressCloudRecord(bookId, word, progress, result, answer, advanceSrs));
  flushProgressOutbox(bookId);
}

function syncWordStateToCloud(bookId, word, progress) {
  return learnService.updateWordState({
    bookId,
    wordId: getWordId(word) || progress.wordId,
    word: word.word,
    normalized: word.normalized || progress.normalized || word.word,
    favorite: progress.favorite,
    favoritedAt: progress.favoritedAt,
    status: progress.status === 'ignored' ? 'ignored' : undefined,
    ignoredAt: progress.ignoredAt,
    clientUpdatedAt: progress.clientUpdatedAt || progress.updatedAt
  }).catch((err) => {
    console.warn('[learn] sync word state failed', err);
  });
}

Page({
  data: {
    mode: 'daily',
    bookId: '',
    bookName: '',
    queueId: '',
    words: [],
    index: 0,
    total: 0,
    targetTotal: 0,
    dailyGoal: 0,
    dailyProgressBase: 0,
    dailyQueueKnown: 0,
    currentWord: null,
    currentQuestion: null,
    combo: 0,
    progressPercent: 0,
    orbLevel: '0',
    barProgressText: '0/0',
    isFavorite: false,
    isIgnored: false,
    finished: false,
    answered: false,
    answerResult: '',
    answerRevealed: false,
    answerValue: '',
    answerText: '',
    answerCorrect: false,
    answerHistory: [],
    stats: { known: 0, unknown: 0 },
    navTopPx: 96,
    forceQuestionType: '',
    enableSpellingQuestions: false,
    isLoading: true
  },

  _choicePool: [],
  _advanceTimer: null,
  _todayRetryCount: {},
  _groupPassedKeys: new Set(),
  _groupRecoveryCount: {},
  _pendingNextState: null,
  _advanceAfterDetail: false,
  _detailOpen: false,
  _nextModeAfterReview: '',
  _hiddenAt: 0,

  async onLoad(query) {
    const mode = query.mode || 'daily';
    const bookId = DEFAULT_WORDBOOK_ID;
    const forceQuestionType = String(query.forceType || query.questionType || '').trim();
    this._nextModeAfterReview = query.next === 'daily' ? 'daily' : '';
    this.setData({ bookId, mode, forceQuestionType, navTopPx: getNavTopPx() });
    await this.loadMode(mode, bookId);
  },

  onShow() {
    if (this._advanceAfterDetail) {
      this._advanceAfterDetail = false;
      this._detailOpen = false;
      this._hiddenAt = 0;
      if (this.data.answered && this._pendingNextState) this.onNext();
      return;
    }
    if (this._detailOpen) {
      this._detailOpen = false;
      this._hiddenAt = 0;
      return;
    }
    if (this._hiddenAt && Date.now() - this._hiddenAt >= 1500 && this.data.bookId && !this.data.isLoading) {
      this._hiddenAt = 0;
      this.loadMode(this.data.mode, this.data.bookId);
    }
  },

  async loadMode(mode, bookId = this.data.bookId) {
    this.setData({
      isLoading: true,
      finished: false,
      currentWord: null,
      currentQuestion: null,
      queueId: '',
      total: 0,
      answered: false,
      answerRevealed: false,
      answerValue: '',
      answerText: '',
      answerCorrect: false,
      answerHistory: []
    });

    try {
      const localSessionAtStart = loadLearnSession(bookId, mode);
      const queueWarmupPromise = mode === 'daily' && !localSessionAtStart
        ? getWordsPage(bookId, { limit: 100 }).catch(() => null)
        : Promise.resolve(null);
      const outboxPromise = flushProgressOutbox(bookId);
      const [meta, progress, learningPreferences, savedSession] = await Promise.all([
        getMetaAsync(bookId).catch(() => null),
        loadMergedProgress(bookId, { force: true }),
        getUserLearningPreferences(),
        loadMergedLearnSession(bookId, mode),
        outboxPromise
      ]);
      if (!meta) {
        this.setData({ isLoading: false });
        wx.showToast({ title: '词书未找到', icon: 'none' });
        setTimeout(() => wx.navigateBack(), 1200);
        return;
      }
      const dailyGoal = learningPreferences.dailyGoal;
      const enableSpellingQuestions = learningPreferences.enableSpellingQuestions === true;

      let todayDone = mode === 'daily' ? countTodayDone(bookId, progress) : 0;
      const savedSessionTarget = savedSession
        ? (normalizeCount(savedSession.targetTotal) || normalizeCount(savedSession.total) || (savedSession.words || []).length)
        : 0;
      const savedSessionHasReviewWords = mode === 'daily'
        && savedSession
        && Array.isArray(savedSession.words)
        && savedSession.words.some(isReviewSourceWord);
      const shouldDropDailySession = mode === 'daily' && savedSession && (
        todayDone >= dailyGoal
        || savedSessionTarget > dailyGoal
        || savedSessionHasReviewWords
      );
      if (shouldDropDailySession) {
        console.info('[learn] drop stale session', {
          todayDone,
          dailyGoal,
          sessionTargetTotal: savedSessionTarget,
          sessionWords: Array.isArray(savedSession.words) ? savedSession.words.length : 0
        });
        const completedHistory = createCompletedHistory(savedSession.answerHistory, savedSession.stats);
        if (completedHistory) saveLastAnswerHistory(bookId, mode, completedHistory.answerHistory, completedHistory.stats);
        clearLearnSession(bookId, mode, { completedHistory });
      }
      const session = shouldDropDailySession ? null : savedSession;
      if (session) {
        console.info('[learn] resume session', {
          mode,
          words: Array.isArray(session.words) ? session.words.length : 0,
          index: normalizeCount(session.index),
          targetTotal: normalizeCount(session.targetTotal) || normalizeCount(session.total) || (session.words || []).length,
          known: session.stats && session.stats.known,
          unknown: session.stats && session.stats.unknown,
          retryOrExtraWords: Math.max(
            0,
            (Array.isArray(session.words) ? session.words.length : 0)
              - (normalizeCount(session.targetTotal) || normalizeCount(session.total) || 0)
          )
        });
        this._choicePool = Array.isArray(session.choicePool)
          ? [...session.words, ...session.choicePool]
          : session.words;
        this._todayRetryCount = session.todayRetryCount || {};
        this._groupPassedKeys = getCurrentQueuePassedKeys(session.words, session.groupPassedKeys);
        this._groupRecoveryCount = session.groupRecoveryCount || {};
        this._pendingNextState = session.pendingNextState || null;
        const currentWord = session.words[session.index || 0] || session.currentWord || null;
        const currentProgress = getWordProgress(progress, currentWord);
        const savedQuestionWordId = session.currentQuestion && (session.currentQuestion.wordId || session.currentQuestion.word);
        const shouldRebuildSavedQuestion = !enableSpellingQuestions
          && session.currentQuestion
          && session.currentQuestion.type === QUESTION_TYPES.SPELLING;
        const rebuiltQuestion = buildCurrentQuestion(
          currentWord,
          this._choicePool,
          mode,
          currentProgress,
          this.data.forceQuestionType,
          enableSpellingQuestions,
          session.index || 0
        );
        const savedQuestionMatchesCurrentWord = getQueueWordIdentity(currentWord) === String(savedQuestionWordId || '').trim().toLowerCase();
        const shouldRefreshSavedQuestionType = !session.answered
          && savedQuestionMatchesCurrentWord
          && session.currentQuestion
          && rebuiltQuestion
          && session.currentQuestion.type !== rebuiltQuestion.type;
        const currentQuestion = !shouldRebuildSavedQuestion
          && !shouldRefreshSavedQuestionType
          && savedQuestionMatchesCurrentWord
          ? session.currentQuestion
          : rebuiltQuestion;
        const stats = {
          ...(session.stats || {}),
          known: this._groupPassedKeys.size,
          unknown: normalizeCount(session.stats && session.stats.unknown)
        };
        const sessionTargetTotal = normalizeCount(session.targetTotal) || normalizeCount(session.total) || session.words.length || dailyGoal;
        const dailyProgressBase = mode === 'daily'
          ? normalizeCount(session.dailyProgressBase !== undefined
            ? session.dailyProgressBase
            : Math.max(0, todayDone - normalizeCount(stats.known)))
          : 0;
        const dailyQueueKnown = mode === 'daily'
          ? normalizeCount(session.dailyQueueKnown !== undefined
            ? session.dailyQueueKnown
            : countDailyQueuePassedWords(session.words, this._groupPassedKeys))
          : 0;
        const sessionFinished = stats.known >= sessionTargetTotal;
        const learnProgress = formatLearnProgress(
          mode,
          stats.known,
          sessionTargetTotal,
          dailyProgressBase,
          dailyGoal,
          dailyQueueKnown
        );

        this.setData({
          mode,
          bookId,
          bookName: meta.name,
          queueId: session.queueId || '',
          words: session.words,
          index: normalizeCount(session.index),
          total: normalizeCount(session.total) || session.words.length,
          targetTotal: sessionTargetTotal,
          dailyGoal,
          enableSpellingQuestions,
          dailyProgressBase,
          dailyQueueKnown,
          currentWord: sessionFinished ? null : currentWord,
          currentQuestion: sessionFinished ? null : currentQuestion,
          combo: normalizeCount(session.combo),
          progressPercent: learnProgress.progressPercent,
          orbLevel: getOrbLevel(learnProgress.progressPercent),
          barProgressText: learnProgress.barProgressText,
          finished: sessionFinished,
          answered: sessionFinished ? false : Boolean(session.answered),
          answerResult: session.answerResult || '',
          answerRevealed: Boolean(session.answerRevealed),
          answerValue: session.answerValue || '',
          answerText: session.answerText || '',
          answerCorrect: Boolean(session.answerCorrect),
          isFavorite: Boolean(currentProgress.favorite),
          isIgnored: isIgnoredProgress(currentProgress),
          stats,
          answerHistory: Array.isArray(session.answerHistory) ? session.answerHistory : [],
          isLoading: false
        });
        if (sessionFinished) {
          saveLastAnswerHistory(bookId, mode, session.answerHistory || [], stats);
          clearLearnSession(bookId, mode, {
            completedHistory: createCompletedHistory(session.answerHistory, stats)
          });
        }
        return;
      }

      let words;
      let queueDebug = {
        mode,
        dailyGoal,
        todayDone,
        dueReviewCount: 0,
        dailyWordsCount: 0,
        total: 0,
        fromSession: false
      };
      if (mode !== 'review') {
        await queueWarmupPromise;
        const remainingGoal = Math.max(0, dailyGoal - todayDone);
        const previousSession = loadPreviousLearnSession(bookId, mode);
        const carryoverWords = getSessionCarryoverWords(previousSession, progress, bookId, remainingGoal)
          .filter(Boolean);
        const carryoverKeys = new Set(carryoverWords.map(getWordKey).filter(Boolean));
        const carryoverIdentityKeys = new Set(carryoverWords.map(getQueueWordIdentity).filter(Boolean));
        const remainingAfterCarryover = Math.max(0, remainingGoal - carryoverWords.length);
        const dailyRemainingGoal = remainingAfterCarryover;
        // 同一天内复用同一批 today 词
        const todayKey = TODAY_KEY(bookId);
        const cached = wx.getStorageSync(todayKey);
        let dailyWords = [];
        let dailyChoicePool = [];
        if (dailyRemainingGoal > 0 && cached && cached.length) {
          todayDone = countTodayDone(bookId, progress);
          const cachedWords = await getWordsByWordsAsync(bookId, cached);
          dailyWords = cachedWords.filter(w => {
            if (carryoverKeys.has(getWordKey(w)) || carryoverIdentityKeys.has(getQueueWordIdentity(w))) return false;
            const p = progress[getWordKey(w)];
            return !isDoneToday(bookId, w, progress) && !isIgnoredProgress(p);
          }).slice(0, dailyRemainingGoal).map(word => withLearnSource(word, 'daily'));

          const page = await getWordsPage(bookId, { limit: 100 }).catch(() => null);
          dailyChoicePool = [...cachedWords, ...((page && page.items) || [])];

          if (dailyWords.length < dailyRemainingGoal) {
            const needed = dailyRemainingGoal - dailyWords.length;
            const cachedSet = new Set(cached.map(value => String(value || '').toLowerCase()));
            const candidateGoal = needed + cachedSet.size + carryoverKeys.size;
            const result = await loadCandidateWords(bookId, progress, candidateGoal, mode);
            const additions = result.words
              .filter(w => {
                const wordKey = getWordKey(w);
                const identityKey = getQueueWordIdentity(w);
                return !cachedSet.has(wordKey)
                  && !carryoverKeys.has(wordKey)
                  && !carryoverIdentityKeys.has(identityKey);
              })
              .slice(0, needed);
            dailyWords.push(...additions.map(word => withLearnSource(word, 'daily')));
            dailyChoicePool = [...dailyChoicePool, ...result.allWords];
            wx.setStorageSync(todayKey, cached.concat(additions.map(w => w.word)));
          }
        } else if (dailyRemainingGoal > 0) {
          const candidateGoal = dailyRemainingGoal + carryoverKeys.size;
          const result = dailyRemainingGoal
            ? await loadCandidateWords(bookId, progress, candidateGoal, mode)
            : { words: [], allWords: [] };
          dailyWords = result.words
            .filter(word => {
              const wordKey = getWordKey(word);
              const identityKey = getQueueWordIdentity(word);
              return !carryoverKeys.has(wordKey)
                && !carryoverIdentityKeys.has(identityKey);
            })
            .slice(0, dailyRemainingGoal)
            .map(word => withLearnSource(word, 'daily'));
          dailyChoicePool = result.allWords;
          wx.setStorageSync(todayKey, dailyWords.map(w => w.word));
        } else {
          dailyChoicePool = [];
        }
        words = [...carryoverWords, ...dailyWords];
        const cachedTodayWords = Array.isArray(wx.getStorageSync(todayKey)) ? wx.getStorageSync(todayKey) : [];
        const cachedTodaySet = new Set(cachedTodayWords.map(value => String(value || '').toLowerCase()));
        const todayAdditions = words
          .filter(word => !isReviewSourceWord(word))
          .map(word => word && word.word)
          .filter(word => word && !cachedTodaySet.has(String(word).toLowerCase()));
        if (todayAdditions.length) wx.setStorageSync(todayKey, cachedTodayWords.concat(todayAdditions));
        queueDebug = {
          ...queueDebug,
          carryoverCount: carryoverWords.length,
          carryoverDateKey: previousSession && previousSession.dateKey,
          dueReviewCount: 0,
          dailyWordsCount: dailyWords.length,
          remainingGoal,
          total: words.length
        };
        this._choicePool = [...carryoverWords, ...dailyChoicePool];
      } else {
        words = (await loadReviewWords(bookId, progress)).map(word => withLearnSource(word, 'review'));
        queueDebug = {
          ...queueDebug,
          dueReviewCount: words.length,
          dailyWordsCount: 0,
          total: words.length
        };
        const page = await getWordsPage(bookId, { limit: 100 }).catch(() => null);
        this._choicePool = [...words, ...((page && page.items) || [])];
      }
      console.info('[learn] queue built', queueDebug);

      this._todayRetryCount = {};
      this._groupPassedKeys = new Set();
      this._groupRecoveryCount = {};
      this._pendingNextState = null;
      const currentWord = words[0] || null;
      const currentProgress = getWordProgress(progress, currentWord);
      const currentQuestion = buildCurrentQuestion(
        currentWord,
        this._choicePool,
        mode,
        currentProgress,
        this.data.forceQuestionType,
        enableSpellingQuestions,
        0
      );
      const displayTotal = mode === 'daily' ? Math.max(1, words.length) : words.length;
      const sessionTargetTotal = mode === 'daily' ? words.length : displayTotal;
      const learnProgress = formatLearnProgress(mode, 0, sessionTargetTotal, todayDone, dailyGoal, 0);
      let savedHistory = currentWord ? { answerHistory: [], stats: null } : loadLastAnswerHistory(bookId, mode);
      if (!currentWord && mode === 'daily' && !savedHistory.answerHistory.length) {
        savedHistory = await rebuildTodayAnswerHistory(bookId, progress);
        if (savedHistory.answerHistory.length) {
          saveLastAnswerHistory(bookId, mode, savedHistory.answerHistory, savedHistory.stats);
        }
      }

      const nextData = {
        mode,
        bookId,
        bookName: meta.name,
        queueId: createLearnQueueId(bookId, mode),
        words,
        index: 0,
        total: words.length,
        targetTotal: sessionTargetTotal,
        dailyGoal,
        enableSpellingQuestions,
        dailyProgressBase: mode === 'daily' ? todayDone : 0,
        dailyQueueKnown: 0,
        currentWord,
        currentQuestion,
        combo: 0,
        progressPercent: learnProgress.progressPercent,
        orbLevel: getOrbLevel(learnProgress.progressPercent),
        barProgressText: learnProgress.barProgressText,
        finished: words.length === 0,
        answered: false,
        answerResult: '',
        answerRevealed: false,
        answerValue: '',
        answerText: '',
        answerCorrect: false,
        isFavorite: Boolean(currentProgress.favorite),
        isIgnored: isIgnoredProgress(currentProgress),
        stats: savedHistory.stats || { known: 0, unknown: 0 },
        answerHistory: savedHistory.answerHistory || [],
        isLoading: false
      };
      this.setData(nextData);
      if (currentWord) {
        this.saveCurrentSession(nextData);
      } else if (mode === 'review' && this._nextModeAfterReview === 'daily') {
        this._nextModeAfterReview = '';
        await this.loadMode('daily', bookId);
      } else {
        clearLearnSession(bookId, mode, {
          completedHistory: createCompletedHistory(nextData.answerHistory, nextData.stats)
        });
      }
    } catch (err) {
      this.setData({ isLoading: false });
      console.error('[learn] load wordbook failed', err);
      wx.showToast({ title: '词书加载失败', icon: 'none' });
    }
  },

  onSwitchMode(e) {
    const mode = e.currentTarget.dataset.mode || 'daily';
    if (mode === this.data.mode) return;
    stopAudio();
    this.loadMode(mode);
  },

  onPlay() {
    const w = this.data.currentWord;
    if (!w) return;
    playWord(w.word);
  },

  saveCurrentSession(extra = {}) {
    const data = {
      ...this.data,
      ...extra
    };
    saveLearnSession(data.bookId, data.mode, {
      queueId: data.queueId,
      words: data.words,
      index: data.index,
      total: data.total,
      targetTotal: data.targetTotal,
      dailyGoal: data.dailyGoal,
      dailyProgressBase: data.dailyProgressBase,
      dailyQueueKnown: data.dailyQueueKnown,
      currentWord: data.currentWord,
      currentQuestion: data.currentQuestion,
      combo: data.combo,
      progressPercent: data.progressPercent,
      orbLevel: data.orbLevel,
      barProgressText: data.barProgressText,
      isFavorite: data.isFavorite,
      isIgnored: data.isIgnored,
      finished: data.finished,
      answered: data.answered,
      answerResult: data.answerResult,
      answerRevealed: data.answerRevealed,
      answerValue: data.answerValue,
      answerText: data.answerText,
      answerCorrect: data.answerCorrect,
      answerHistory: data.answerHistory,
      stats: data.stats,
      choicePool: this._choicePool,
      todayRetryCount: this._todayRetryCount,
      groupPassedKeys: Array.from(this._groupPassedKeys),
      groupRecoveryCount: this._groupRecoveryCount,
      pendingNextState: this._pendingNextState
    });
  },

  onAnswer(e) {
    const answer = e.detail || {};
    const { result } = answer;
    const word = this.data.currentWord;
    if (!word || this.data.answered) return;

    const nextCombo = result === 'known' ? this.data.combo + 1 : 0;
    playFeedbackSound(result === 'known' ? 'correct' : 'wrong', { combo: nextCombo });

    // 更新 SRS 进度
    const progress = loadProgress(this.data.bookId);
    const key = getWordKey(word);
    const wordId = getWordId(word);
    if (!key) return;
    const passKey = getGroupPassKey(word);
    const answerMode = isReviewSourceWord(word) ? 'review' : 'daily';
    const isDailyQueueItem = answerMode === 'daily';
    const prev = progress[key] || { easiness: 2.5, interval: 0, correctCount: 0, wrongCount: 0, streakCorrect: 0 };
    const now = Date.now();
    const dailyPassState = getDailyPassState(prev, result, isDailyQueueItem ? 'daily' : 'review', now);
    const passedToday = isDailyQueueItem && dailyPassState.passedToday;
    const dateKey = getDateKeyAsiaShanghai(now);
    const shouldAdvanceSrs = !isDailyQueueItem || (result === 'known'
      ? dailyPassState.passedToday && prev.dailyDoneDateKey !== dateKey
      : prev.dailyWrongDateKey !== dateKey);
    const nextProgress = shouldAdvanceSrs
      ? getNextProgress(prev, result, now)
      : {
        easiness: prev.easiness === undefined ? 2.5 : prev.easiness,
        interval: normalizeCount(prev.interval),
        nextReviewAt: prev.nextReviewAt || 0,
        correctCount: normalizeCount(prev.correctCount),
        wrongCount: normalizeCount(prev.wrongCount),
        streakCorrect: normalizeCount(prev.streakCorrect),
        status: prev.status || 'learning'
      };
    const hadRecovery = Object.prototype.hasOwnProperty.call(this._groupRecoveryCount, passKey)
      || Boolean(word._learnRecoveryStep)
      || prev.dailyWrongDateKey === dateKey;
    let recoveryCount = hadRecovery
      ? normalizeCount(this._groupRecoveryCount[passKey] !== undefined
        ? this._groupRecoveryCount[passKey]
        : (word._learnRecoveryPassed !== undefined ? word._learnRecoveryPassed : prev.dailyRecoveryCorrectCount))
      : 0;
    let passedThisAnswer = false;

    if (passKey && !this._groupPassedKeys.has(passKey)) {
      if (result === 'known') {
        if (hadRecovery) {
          recoveryCount += 1;
          this._groupRecoveryCount[passKey] = recoveryCount;
          passedThisAnswer = recoveryCount >= DAILY_RECOVERY_REQUIRED;
        } else {
          passedThisAnswer = true;
        }
      } else {
        this._groupRecoveryCount[passKey] = 0;
      }

      if (passedThisAnswer) {
        this._groupPassedKeys.add(passKey);
        delete this._groupRecoveryCount[passKey];
      }
    }

    progress[key] = {
      ...nextProgress,
      lastResult: result,
      wordId,
      normalized: key,
      favorite: Boolean(prev.favorite),
      favoritedAt: prev.favoritedAt || null,
      ignoredAt: prev.ignoredAt || null,
      dailyDoneDateKey: dailyPassState.dailyDoneDateKey,
      dailyWrongDateKey: dailyPassState.dailyWrongDateKey,
      dailyRecoveryCorrectCount: dailyPassState.dailyRecoveryCorrectCount,
      mode: answerMode,
      _todayDone: passedToday,
      clientUpdatedAt: now,
      updatedAt: now
    };
    saveProgress(this.data.bookId, progress);
    if (passedToday) {
      markTodayDone(this.data.bookId, word);
    }
    syncProgressToCloud(this.data.bookId, word, progress[key], result, answer, shouldAdvanceSrs);

    // 连击 / 统计
    const stats = { ...this.data.stats };
    const historyBeforeAnswer = Array.isArray(this.data.answerHistory) ? this.data.answerHistory : [];
    const alreadyInHistory = historyBeforeAnswer.some((record) => {
      const recordKey = record && (record.key || normalizeDoneKey(record.word));
      return recordKey && recordKey === passKey;
    });
    if (result === 'unknown' && !alreadyInHistory) stats.unknown = (stats.unknown || 0) + 1;
    if (passedThisAnswer) {
      stats.known = this._groupPassedKeys.size;
    }
    const dailyQueueKnown = this.data.dailyQueueKnown + (passedThisAnswer && isDailyQueueItem ? 1 : 0);
    const combo = nextCombo;
    const answerHistory = appendFirstAnswerHistory(historyBeforeAnswer, word, result);
    const currentQuestionWithRecovery = withRecoveryQuestionMeta(
      this.data.currentQuestion,
      result === 'known' ? recoveryCount : 0
    );

    let words = this.data.words;
    let total = this.data.total;
    const retryKey = wordId || passKey;
    const shouldRetryToday = Boolean(retryKey && passKey && !this._groupPassedKeys.has(passKey));
    if (shouldRetryToday) {
      const retryCount = (this._todayRetryCount[retryKey] || 0) + 1;
      this._todayRetryCount[retryKey] = retryCount;
      const insertAt = Math.min(this.data.index + RETRY_DELAY_QUESTIONS + 1, words.length);
      words = words.slice();
      words.splice(insertAt, 0, {
        ...word,
        _learnRetryType: getRetryQuestionType(retryCount, this.data.enableSpellingQuestions),
        _learnRecoveryStep: Math.min(recoveryCount + 1, DAILY_RECOVERY_REQUIRED),
        _learnRecoveryPassed: recoveryCount
      });
      total = words.length;
    }

    const next = this.data.index + 1;
    const currentWord = words[next] || null;
    const currentProgress = getWordProgress(progress, currentWord);
    const currentQuestion = buildCurrentQuestion(
      currentWord,
      this._choicePool,
      this.data.mode,
      currentProgress,
      this.data.forceQuestionType,
      this.data.enableSpellingQuestions,
      next
    );
    const targetTotal = Math.max(1, this.data.targetTotal || total || 1);
    const learnProgress = formatLearnProgress(
      this.data.mode,
      stats.known,
      targetTotal,
      this.data.dailyProgressBase,
      this.data.dailyGoal,
      dailyQueueKnown
    );
    const progressPercent = learnProgress.progressPercent;
    const barProgressText = learnProgress.barProgressText;
    const finished = !currentWord || stats.known >= targetTotal;
    const nextCurrentWord = finished ? null : currentWord;
    const nextCurrentQuestion = finished ? null : currentQuestion;

    this._pendingNextState = {
      index: next,
      words,
      total,
      targetTotal,
      currentWord: nextCurrentWord,
      currentQuestion: nextCurrentQuestion,
      isFavorite: Boolean(currentProgress.favorite),
      isIgnored: isIgnoredProgress(currentProgress),
      combo,
      progressPercent,
      orbLevel: getOrbLevel(progressPercent),
      barProgressText,
      finished,
      stats,
      dailyQueueKnown,
      answerHistory
    };

    const answeredState = {
      combo,
      stats,
      answerHistory,
      progressPercent,
      orbLevel: getOrbLevel(progressPercent),
      barProgressText,
      dailyQueueKnown,
      answered: true,
      answerRevealed: Boolean(answer.revealed || answer.value === '__reveal_answer__'),
      answerValue: answer.value || '',
      answerText: answer.answerText || '',
      answerCorrect: Boolean(answer.correct),
      answerResult: result,
      currentQuestion: currentQuestionWithRecovery
    };
    this.setData(answeredState);
    this.saveCurrentSession(answeredState);
  },

  onRevealAnswer() {
    const word = this.data.currentWord;
    const question = this.data.currentQuestion || {};
    if (!word || this.data.answered || this.data.finished) return;

    this.setData({ answerRevealed: true });
    this.onAnswer({
      detail: {
        questionId: question.id || '',
        wordId: question.wordId || getWordId(word),
        senseId: question.senseId || '',
        type: question.type || 'word_to_zh',
        result: 'unknown',
        correct: false,
        revealed: true,
        value: '__reveal_answer__',
        answerText: getCorrectAnswerText(question)
      }
    });
    setTimeout(() => playWord(word.word), 180);
  },

  async onNext() {
    if (!this._pendingNextState) return;
    const nextState = this._pendingNextState;
    this._pendingNextState = null;

    if (nextState.finished) {
      // 标记今日打卡
      const today = new Date().toDateString();
      wx.setStorageSync('lastCheckInDate', today);
      const streak = wx.getStorageSync('streakDays') || 0;
      wx.setStorageSync('streakDays', streak + 1);
      saveLastAnswerHistory(this.data.bookId, this.data.mode, nextState.answerHistory, nextState.stats);
      clearLearnSession(this.data.bookId, this.data.mode, {
        completedHistory: createCompletedHistory(nextState.answerHistory, nextState.stats)
      });

      if (this.data.mode === 'review' && this._nextModeAfterReview === 'daily') {
        this._nextModeAfterReview = '';
        await this.loadMode('daily', this.data.bookId);
        return;
      }
    }

    const nextData = {
      ...nextState,
      answered: false,
      answerRevealed: false,
      answerValue: '',
      answerText: '',
      answerCorrect: false,
      answerResult: ''
    };
    this.setData(nextData);
    if (!nextState.finished) this.saveCurrentSession(nextData);
  },

  async onToggleFavorite() {
    const word = this.data.currentWord;
    if (!word) return;
    const progress = loadProgress(this.data.bookId);
    const key = getWordKey(word);
    if (!key) return;

    const now = Date.now();
    const prev = progress[key] || {};
    const favorite = !this.data.isFavorite;
    progress[key] = {
      ...prev,
      wordId: getWordId(word) || prev.wordId,
      normalized: key,
      word: word.word || prev.word || key,
      favorite,
      favoritedAt: favorite ? now : null,
      clientUpdatedAt: now,
      updatedAt: now
    };
    saveProgress(this.data.bookId, progress);
    this.setData({ isFavorite: favorite });
    wx.showToast({ title: favorite ? '已收藏' : '已取消收藏', icon: 'none' });
    const res = await syncWordStateToCloud(this.data.bookId, word, progress[key]);
    if (!res || !res.ok) {
      console.warn('[learn] favorite sync failed', res);
      wx.showToast({ title: '收藏已本地保存，同步稍后重试', icon: 'none' });
    }
  },

  onIgnoreCurrent() {
    const word = this.data.currentWord;
    if (!word) return;

    wx.showModal({
      title: '不再学习这个词？',
      content: '它会从学习和复习队列中移除，收藏状态不受影响。',
      confirmText: '移除',
      confirmColor: '#D93025',
      success: (res) => {
        if (!res.confirm) return;
        this.markWordIgnored(word);
        this.removeCurrentWordFromQueue();
      }
    });
  },

  markWordIgnored(word) {
    const progress = loadProgress(this.data.bookId);
    const key = getWordKey(word);
    if (!key) return;

    const now = Date.now();
    const prev = progress[key] || {};
    progress[key] = {
      ...prev,
      wordId: getWordId(word) || prev.wordId,
      normalized: key,
      word: word.word || prev.word || key,
      status: 'ignored',
      ignoredAt: now,
      clientUpdatedAt: now,
      updatedAt: now
    };
    saveProgress(this.data.bookId, progress);
    unmarkTodayDone(this.data.bookId, word);
    syncWordStateToCloud(this.data.bookId, word, progress[key]);
  },

  removeCurrentWordFromQueue() {
    const words = this.data.words.slice();
    const index = this.data.index;
    const removedWord = words[index] || null;
    const removedPassKey = getGroupPassKey(removedWord);
    const wasPassed = removedPassKey && this._groupPassedKeys.has(removedPassKey);
    words.splice(index, 1);
    const total = words.length;
    const currentWord = words[index] || null;
    const finished = !currentWord;
    const targetTotal = Math.max(0, (this.data.targetTotal || Math.max(1, total)) - (wasPassed ? 0 : 1));
    const learnProgress = formatLearnProgress(
      this.data.mode,
      this.data.stats.known,
      Math.max(1, targetTotal),
      this.data.dailyProgressBase,
      this.data.dailyGoal,
      this.data.dailyQueueKnown
    );
    const progressPercent = learnProgress.progressPercent;
    const barProgressText = learnProgress.barProgressText;
    const progress = loadProgress(this.data.bookId);
    const currentProgress = getWordProgress(progress, currentWord);

    this._pendingNextState = null;
    const nextData = {
      words,
      total,
      targetTotal: Math.max(1, targetTotal),
      currentWord,
      currentQuestion: buildCurrentQuestion(
        currentWord,
        this._choicePool,
        this.data.mode,
        currentProgress,
        this.data.forceQuestionType,
        this.data.enableSpellingQuestions,
        index
      ),
      progressPercent,
      orbLevel: getOrbLevel(progressPercent),
      barProgressText,
      finished,
      answered: false,
      answerRevealed: false,
      answerValue: '',
      answerText: '',
      answerCorrect: false,
      answerResult: '',
      isFavorite: Boolean(currentProgress.favorite),
      isIgnored: isIgnoredProgress(currentProgress)
    };
    this.setData(nextData);
    if (finished) {
      clearLearnSession(this.data.bookId, this.data.mode, {
        completedHistory: createCompletedHistory(nextData.answerHistory, nextData.stats)
      });
    } else {
      this.saveCurrentSession(nextData);
    }
  },

  onOpenDetail() {
    const w = this.data.currentWord;
    if (!w) return;
    const fromLearn = this.data.answered ? 1 : 0;
    const questionMeta = (this.data.currentQuestion && this.data.currentQuestion.meta) || {};
    const recoveryQuery = questionMeta.recoveryStep
      ? `&recoveryStep=${encodeURIComponent(questionMeta.recoveryStep)}&recoveryPassed=${encodeURIComponent(questionMeta.recoveryPassed || 0)}&recoveryTotal=${encodeURIComponent(questionMeta.recoveryTotal || DAILY_RECOVERY_REQUIRED)}`
      : '';
    this._detailOpen = true;
    wx.navigateTo({
      url: `/pages/word-detail/index?bookId=${this.data.bookId}&word=${encodeURIComponent(w.word)}&fromLearn=${fromLearn}&orbLevel=${this.data.orbLevel || '0'}${recoveryQuery}`,
      fail: () => {
        this._detailOpen = false;
      }
    });
  },

  async onLearnMore() {
    if (this.data.mode !== 'daily' || this.data.isLoading) return;

    this.setData({
      isLoading: true,
      finished: false,
      currentWord: null,
      currentQuestion: null,
      answered: false,
      answerRevealed: false,
      answerValue: '',
      answerText: '',
      answerCorrect: false
    });
    try {
      const learningPreferences = await getUserLearningPreferences();
      const groupSize = learningPreferences.dailyGoal;
      const enableSpellingQuestions = learningPreferences.enableSpellingQuestions === true;
      await flushProgressOutbox(this.data.bookId);
      const progress = await loadMergedProgress(this.data.bookId, { force: true });
      const result = await loadCandidateWords(this.data.bookId, progress, groupSize, 'daily');
      const words = (result.words || []).slice(0, groupSize);
      if (!words.length) {
        let savedHistory = loadLastAnswerHistory(this.data.bookId, 'daily');
        if (!savedHistory.answerHistory.length) {
          savedHistory = await rebuildTodayAnswerHistory(this.data.bookId, progress);
          if (savedHistory.answerHistory.length) {
            saveLastAnswerHistory(this.data.bookId, 'daily', savedHistory.answerHistory, savedHistory.stats);
          }
        }
        clearLearnSession(this.data.bookId, 'daily', {
          completedHistory: createCompletedHistory(savedHistory.answerHistory, savedHistory.stats)
        });
        this.setData({
          isLoading: false,
          finished: true,
          currentWord: null,
          currentQuestion: null,
          total: 0,
          answerRevealed: false,
          answerValue: '',
          answerText: '',
          answerCorrect: false,
          answerHistory: savedHistory.answerHistory,
          stats: savedHistory.stats
        });
        wx.showToast({ title: '暂时没有更多新词', icon: 'none' });
        return;
      }

      const todayKey = TODAY_KEY(this.data.bookId);
      const cached = wx.getStorageSync(todayKey);
      const cachedWords = Array.isArray(cached) ? cached : [];
      const cachedSet = new Set(cachedWords.map(value => String(value || '').toLowerCase()));
      const additions = words
        .map(word => word.word)
        .filter(word => word && !cachedSet.has(String(word).toLowerCase()));
      if (additions.length) wx.setStorageSync(todayKey, cachedWords.concat(additions));

      this._choicePool = [
        ...this._choicePool,
        ...words,
        ...((result && result.allWords) || [])
      ];
      this._todayRetryCount = {};
      this._groupPassedKeys = new Set();
      this._groupRecoveryCount = {};
      this._pendingNextState = null;
      clearLastAnswerHistory(this.data.bookId, 'daily');
      clearLearnSession(this.data.bookId, 'daily');

      const currentWord = words[0] || null;
      const currentProgress = getWordProgress(progress, currentWord);
      const groupStats = { known: 0, unknown: 0 };
      const targetTotal = Math.max(1, words.length);
      const learnProgress = formatLearnProgress('daily', 0, targetTotal, 0, groupSize, 0);

      const nextData = {
        queueId: createLearnQueueId(this.data.bookId, 'daily'),
        words,
        index: 0,
        total: words.length,
        targetTotal,
        dailyGoal: groupSize,
        enableSpellingQuestions,
        dailyProgressBase: 0,
        dailyQueueKnown: 0,
        currentWord,
        currentQuestion: buildCurrentQuestion(
          currentWord,
          this._choicePool,
          'daily',
          currentProgress,
          this.data.forceQuestionType,
          enableSpellingQuestions,
          0
        ),
        progressPercent: learnProgress.progressPercent,
        orbLevel: getOrbLevel(learnProgress.progressPercent),
        barProgressText: learnProgress.barProgressText,
        finished: false,
        answered: false,
        answerResult: '',
        answerRevealed: false,
        answerValue: '',
        answerText: '',
        answerCorrect: false,
        stats: groupStats,
        isFavorite: Boolean(currentProgress.favorite),
        isIgnored: isIgnoredProgress(currentProgress),
        answerHistory: [],
        isLoading: false
      };
      this.setData(nextData);
      this.saveCurrentSession(nextData);
    } catch (err) {
      console.error('[learn] load more failed', err);
      this.setData({ isLoading: false, finished: true });
      wx.showToast({ title: '加练加载失败', icon: 'none' });
    }
  },

  onBack() {
    const pages = getCurrentPages ? getCurrentPages() : [];
    if (pages.length > 1) {
      wx.navigateBack();
      return;
    }
    wx.reLaunch({ url: '/pages/home/index' });
  },

  onUnload() {
    clearTimeout(this._advanceTimer);
    if (this.data.currentWord && !this.data.finished) this.saveCurrentSession();
    stopAudio();
  },

  onHide() {
    this._hiddenAt = Date.now();
    if (this.data.currentWord && !this.data.finished) this.saveCurrentSession();
    stopAudio();
  }
});
