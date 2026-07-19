import { getMetaAsync, getWordByWordAsync, searchWordsAsync } from '../../utils/wordbook-loader';
import { visualService } from '../../services/visual';
import { wordbookService } from '../../services/wordbook';
import { normalizeDailyGoal } from '../../config/index';
import { learnService } from '../../services/learn';
import { markProgressSynced, mergeProgressRecords, shouldSyncProgress } from '../../utils/progress-store';
import { getDateKeyAsiaShanghai, isReviewDueToday } from '../../utils/date';
import { getUserProfileFromCache } from '../../utils/profile-cache';

const DEFAULT_WORDBOOK_ID = 'ielts_content_words';
const TODAY_DONE_KEY = (bookId) => `todayDone.${bookId}.${getDateKeyAsiaShanghai()}`;
const HOME_SHORT_DEFINITION_CACHE_KEY = (wordId) => `home.shortDefinition.v3.${wordId}`;
const HOME_BOOT_CACHE_KEY = 'home.bootSnapshot.v1';

function formatDate(d = new Date()) {
  const M = d.getMonth() + 1;
  const D = d.getDate();
  const week = ['周日','周一','周二','周三','周四','周五','周六'][d.getDay()];
  return `${M}月${D}日 · ${week}`;
}

function belongsToBook(progress, bookId) {
  if (!progress) return false;
  if (Array.isArray(progress.bookIds) && progress.bookIds.length) {
    return progress.bookIds.includes(bookId);
  }
  const legacyBookId = progress.bookId || progress.lastReviewedBookId;
  return !legacyBookId || legacyBookId === bookId;
}

function normalizeKey(value) {
  return String(value || '').trim().toLowerCase();
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

function loadTodayDoneSet(bookId) {
  const values = wx.getStorageSync(TODAY_DONE_KEY(bookId)) || [];
  return new Set((Array.isArray(values) ? values : []).map(normalizeKey).filter(Boolean));
}

function isLearnedProgress(progress) {
  return progress
    && progress.status !== 'ignored'
    && (progress.status === 'mastered' || Number(progress.correctCount || 0) > 0);
}

function loadAllLocalProgress() {
  const all = {};
  let keys = [];
  try {
    keys = (wx.getStorageInfoSync && wx.getStorageInfoSync().keys) || [];
  } catch (e) {
    keys = [];
  }

  keys
    .filter(key => /^progress\.[^.]+$/.test(key))
    .forEach((storageKey) => {
      const progress = wx.getStorageSync(storageKey) || {};
      Object.keys(progress).forEach((wordKey) => {
        const item = progress[wordKey] || {};
        const key = normalizeKey(item.wordId || item.normalized || item.word || wordKey);
        if (!key) return;
        if (!all[key]) all[key] = item;
        const normalized = normalizeKey(item.normalized || item.word || wordKey);
        if (normalized && !all[normalized]) all[normalized] = item;
      });
    });

  return all;
}

function normalizeHomeShortDefinition(item) {
  const source = item || {};
  const coreSense = source.coreSense && typeof source.coreSense === 'object'
    ? source.coreSense
    : {};
  return {
    text: String(
      coreSense.en
      || source.shortDefinitionEn
      || source.short_definition_en
      || ''
    ).trim(),
    translationZh: String(
      coreSense.zh
      || source.shortDefinitionZh
      || source.short_definition_zh
      || ''
    ).trim()
  };
}

function normalizeForMatch(value) {
  return String(value || '').trim().toLowerCase();
}

function exampleContainsWord(exampleText, word) {
  const text = normalizeForMatch(exampleText);
  const normalizedWord = normalizeForMatch(word);
  if (!text || !normalizedWord) return false;
  const escaped = normalizedWord.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  return new RegExp(`(^|[^a-z])${escaped}([^a-z]|$)`, 'i').test(text);
}

function wordIdFor(value) {
  const slug = String(value || '')
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '_')
    .replace(/^_+|_+$/g, '')
    .replace(/_+/g, '_');
  return slug ? `word_${slug}` : '';
}

function uniqueValues(values) {
  return Array.from(new Set(values.map(value => String(value || '').trim()).filter(Boolean)));
}

function hasVisualImage(visual) {
  return Boolean(visual && visual.image && visual.image.url);
}

function getLocalHomeCounters(bookId, dailyGoal) {
  const progress = wx.getStorageSync(`progress.${bookId}`) || {};
  const reviewKeys = new Set();
  const todayDoneKeys = loadTodayDoneSet(bookId);
  const dateKey = getDateKeyAsiaShanghai();

  Object.keys(progress).forEach((wordKey) => {
    const item = progress[wordKey] || {};
    if (!belongsToBook(item, bookId) || item.status === 'ignored') return;
    const identity = normalizeKey(item.wordId || item.normalized || item.word || wordKey);
    if (isReviewDueToday(item.nextReviewAt) && item.status !== 'mastered' && identity) {
      reviewKeys.add(identity);
    }
    if (item.dailyDoneDateKey === dateKey) {
      todayDoneKeys.add(normalizeKey(item.normalized || item.word || wordKey));
    }
  });

  const todayDone = todayDoneKeys.size;
  const goal = normalizeDailyGoal(dailyGoal);
  return {
    dailyGoal: goal,
    todayDone,
    reviewCount: reviewKeys.size,
    studyQueueCount: Math.max(0, goal - todayDone),
    progressPercent: Math.min(100, Math.round((todayDone / Math.max(1, goal)) * 100)),
    taskCompleted: todayDone >= goal
  };
}

Page({
  data: {
    nickname: '同学',
    dateText: formatDate(),
    activeBook: { id: '', name: '尚未选择', learned: 0, total: 0 },
    dailyVisual: null,
    homeExample: null,
    homeShortDefinitionRevealed: false,
    dailyGoal: 10,
    todayDone: 0,
    progressPercent: 0,
    orbLevel: '0',
    remainingDays: 0,
    remainingDaysText: '距离完成目标还有 0 天',
    reviewCount: 0,
    studyQueueCount: 0,
    streakDays: 0,
    combo: 0,
    taskCompleted: false,
    pullSearchVisible: false,
    pullSearchDistance: 0,
    pullSearchOffset: -86,
    pullSearchOpacity: 0,
    visualImageReady: false,
    isLoading: true
  },

  _hasRendered: false,
  _pullSearchOpening: false,
  _pullStartY: 0,
  _pullStartX: 0,
  _pullTracking: false,
  _homeExampleToken: '',
  _forceVisualRefresh: false,

  onLoad() {
    const cached = wx.getStorageSync(HOME_BOOT_CACHE_KEY) || null;
    if (!cached || !cached.activeBook || !cached.activeBook.id) return;

    const cachedVisualRes = visualService.getCachedDailyVisual();
    const dailyVisual = (cachedVisualRes && cachedVisualRes.visual) || cached.dailyVisual || null;
    const counters = getLocalHomeCounters(DEFAULT_WORDBOOK_ID, cached.dailyGoal);
    const remaining = counters.studyQueueCount;
    this._forceVisualRefresh = cached.dateKey !== getDateKeyAsiaShanghai();
    this._hasRendered = true;
    this.setData({
      ...cached,
      ...counters,
      dateText: formatDate(),
      dailyVisual,
      visualImageReady: !hasVisualImage(dailyVisual),
      orbLevel: getOrbLevel(counters.progressPercent),
      studyTitle: counters.taskCompleted ? '今日目标已达成' : `今日还差 ${remaining} 个`,
      learnButtonText: counters.taskCompleted ? '继续学' : '开始学习',
      isLoading: false
    });
    if (dailyVisual) this.loadHomeExample(dailyVisual, DEFAULT_WORDBOOK_ID);
  },

  onShow() {
    const forceVisual = this._forceVisualRefresh;
    this._forceVisualRefresh = false;
    this.refresh({ silent: this._hasRendered, forceVisual });
  },

  async refresh(options = {}) {
    const silent = Boolean(options.silent);
    const shouldRefreshVisual = Boolean(options.forceVisual) || !silent || !this.data.dailyVisual;
    if (!silent) this.setData({ isLoading: true, visualImageReady: false });
    try {
      const cachedVisualRes = visualService.getCachedDailyVisual();
      if (shouldRefreshVisual && cachedVisualRes && cachedVisualRes.visual) {
        this.setData({
          dailyVisual: cachedVisualRes.visual,
          visualImageReady: !hasVisualImage(cachedVisualRes.visual)
        });
        this.loadHomeExample(cachedVisualRes.visual, DEFAULT_WORDBOOK_ID);
      }
      const visualPromise = shouldRefreshVisual
        ? visualService.dailyVisual().catch(() => null)
        : Promise.resolve(null);

      const bookId = DEFAULT_WORDBOOK_ID;

      const localProgress = wx.getStorageSync(`progress.${bookId}`) || {};
      const syncProgress = silent || shouldSyncProgress(bookId);
      const [meta, visualRes, progressRes, userProfile] = await Promise.all([
        getMetaAsync(bookId, { refresh: !silent }).catch(() => null),
        visualPromise,
        syncProgress ? learnService.listAllProgress(bookId).catch(() => null) : Promise.resolve(null),
        getUserProfileFromCache({ force: !silent })
      ]);
      const dailyVisual = shouldRefreshVisual && visualRes && visualRes.ok ? visualRes.visual : null;
      if (dailyVisual) {
        this.setData({
          dailyVisual,
          visualImageReady: !hasVisualImage(dailyVisual)
        });
        this.loadHomeExample(dailyVisual, bookId);
      }
      const displayVisual = dailyVisual || this.data.dailyVisual;
      const cloudRecords = progressRes && progressRes.ok && Array.isArray(progressRes.records)
        ? progressRes.records
        : [];
      console.info('[home] progress res', {
        syncProgress,
        ok: progressRes ? progressRes.ok : null,
        code: progressRes && progressRes.code,
        records: cloudRecords.length,
        localRecords: Object.keys(localProgress).length
      });
      const progress = mergeProgressRecords(localProgress, cloudRecords);
      if (progressRes && progressRes.ok) {
        markProgressSynced(bookId);
        if (cloudRecords.length) wx.setStorageSync(`progress.${bookId}`, progress);
      }

      const allProgress = {
        ...loadAllLocalProgress(),
        ...progress
      };
      Object.keys(progress).forEach((wordKey) => {
        const item = progress[wordKey] || {};
        const key = normalizeKey(item.wordId || item.normalized || item.word || wordKey);
        const normalized = normalizeKey(item.normalized || item.word || wordKey);
        if (key) allProgress[key] = item;
        if (normalized) allProgress[normalized] = item;
      });

      let learned = 0;
      const fallbackLearnedKeys = new Set();
      const reviewKeys = new Set();
      for (const word of Object.keys(allProgress)) {
        const p = allProgress[word];
        if (!belongsToBook(p, bookId)) continue;
        if (isLearnedProgress(p)) {
          const learnedKey = normalizeKey(p.wordId || p.normalized || p.word || word);
          if (learnedKey && !fallbackLearnedKeys.has(learnedKey)) {
            fallbackLearnedKeys.add(learnedKey);
            learned += 1;
          }
        }
        if (isReviewDueToday(p.nextReviewAt) && p.status !== 'mastered' && p.status !== 'ignored') {
          const reviewKey = normalizeKey(p.wordId || p.normalized || p.word || word);
          if (reviewKey) reviewKeys.add(reviewKey);
        }
      }
      const reviewCount = reviewKeys.size;

      // 今日完成数
      const todayKey = `today.${bookId}.${getDateKeyAsiaShanghai()}`;
      const todayWords = wx.getStorageSync(todayKey) || [];
      const todayDoneWords = loadTodayDoneSet(bookId);
      for (const word of todayWords) {
        const key = normalizeKey(word);
        const p = progress[key];
        if (p && p.status !== 'ignored' && p.dailyDoneDateKey === getDateKeyAsiaShanghai()) {
          todayDoneWords.add(key);
        }
      }
      const dateKey = getDateKeyAsiaShanghai();
      for (const word of Object.keys(progress)) {
        const p = progress[word];
        if (belongsToBook(p, bookId) && p.status !== 'ignored' && p.dailyDoneDateKey === dateKey) {
          todayDoneWords.add(normalizeKey(word));
        }
      }
      const todayDone = todayDoneWords.size;

      const dailyGoal = normalizeDailyGoal(userProfile.dailyGoal);
      const nickname = userProfile.nickname || '同学';
      const streakDays = wx.getStorageSync('streakDays') || 0;
      const remaining = Math.max(0, dailyGoal - todayDone);
      const studyQueueCount = remaining;
      const totalWords = meta ? Number(meta.totalWords || 0) : 0;
      const remainingWords = Math.max(0, totalWords - learned);
      const effectiveDailyGoal = Math.max(1, Number(dailyGoal) || 1);
      const remainingDays = remainingWords ? Math.ceil(remainingWords / effectiveDailyGoal) : 0;
      const progressPercent = Math.min(100, Math.round((todayDone / effectiveDailyGoal) * 100));
      console.info('[home] study status', {
        reviewCount,
        dailyGoal,
        todayDone,
        remaining,
        studyQueueCount,
        progressPercent
      });
      this._hasRendered = true;
      const nextData = {
        nickname,
        activeBook: meta ? {
          id: bookId,
          name: meta.name,
          letter: meta.letter,
          coverColor: meta.coverColor,
          coverImage: meta.coverImage,
          learned,
          total: totalWords,
          progressText: `${learned}/${totalWords}`
        } : { id: '', name: '尚未选择', letter: '', coverColor: '#1A1A1A', coverImage: '', learned: 0, total: 0 },
        dailyVisual: displayVisual,
        visualImageReady: this.data.visualImageReady || !hasVisualImage(displayVisual),
        dailyGoal,
        todayDone,
        progressPercent,
        orbLevel: getOrbLevel(progressPercent),
        taskCompleted: todayDone >= dailyGoal,
        remainingDays,
        remainingDaysText: remainingDays ? `距离完成目标还有 ${remainingDays} 天` : '当前词书已完成',
        reviewCount,
        studyQueueCount,
        studyTitle: todayDone >= dailyGoal ? '今日目标已达成' : `今日还差 ${remaining} 个`,
        learnButtonText: todayDone >= dailyGoal ? '继续学' : '开始学习',
        streakDays,
        combo: 0,
        isLoading: false
      };
      this.setData(nextData);
      wx.setStorageSync(HOME_BOOT_CACHE_KEY, {
        dateKey: getDateKeyAsiaShanghai(),
        nickname: nextData.nickname,
        activeBook: nextData.activeBook,
        dailyVisual: nextData.dailyVisual,
        dailyGoal: nextData.dailyGoal,
        todayDone: nextData.todayDone,
        progressPercent: nextData.progressPercent,
        orbLevel: nextData.orbLevel,
        remainingDays: nextData.remainingDays,
        remainingDaysText: nextData.remainingDaysText,
        reviewCount: nextData.reviewCount,
        studyQueueCount: nextData.studyQueueCount,
        streakDays: nextData.streakDays,
        taskCompleted: nextData.taskCompleted,
        studyTitle: nextData.studyTitle,
        learnButtonText: nextData.learnButtonText
      });
    } catch (err) {
      console.error('[home] refresh failed', err);
      this._hasRendered = true;
      this.setData({ isLoading: false });
      wx.showToast({ title: '首页加载失败', icon: 'none' });
    }
  },

  onVisualImageLoad() {
    this.setData({ visualImageReady: true });
  },

  onVisualImageError() {
    this.setData({ visualImageReady: true });
  },

  onStartLearn() {
    if (!this.data.activeBook.id) {
      wx.showToast({ title: '请先选择词书', icon: 'none' });
      return;
    }
    const hasReview = Number(this.data.reviewCount || 0) > 0;
    wx.navigateTo({
      url: hasReview ? '/pages/learn/index?mode=review&next=daily' : '/pages/learn/index'
    });
  },

  onStartReview() {
    if (!this.data.activeBook.id) {
      wx.showToast({ title: '请先选择词书', icon: 'none' });
      return;
    }
    if (this.data.reviewCount <= 0) {
      wx.showToast({ title: '暂无待复习单词', icon: 'none' });
      return;
    }
    wx.navigateTo({ url: '/pages/learn/index?mode=review' });
  },

  async loadHomeExample(visual, bookId = DEFAULT_WORDBOOK_ID) {
    if (!visual) return;
    const token = `${visual.wordId || ''}:${visual.word || visual.normalized || ''}`;
    this._homeExampleToken = token;
    this.setData({ homeExample: null, homeShortDefinitionRevealed: false });

    const word = String(visual.word || visual.normalized || '').trim();
    const wordIds = uniqueValues([
      visual.wordId,
      visual.word_id,
      String(visual._id || '').startsWith('word_') ? visual._id : '',
      wordIdFor(word)
    ].concat(visual.wordIds || [], visual.word_ids || []));

    if (word && !wordIds.length) {
      const found = await getWordByWordAsync(bookId, word).catch(() => null);
      wordIds.push(...uniqueValues([found && (found.wordId || found._id)]));
    }
    if (word) {
      const results = await searchWordsAsync(bookId, word, { limit: 3 }).catch(() => []);
      wordIds.push(...uniqueValues(results.map(item => item && (item.wordId || item._id))));
    }

    for (const wordId of uniqueValues(wordIds)) {
      const cached = wx.getStorageSync(HOME_SHORT_DEFINITION_CACHE_KEY(wordId));
      if (cached && cached.text) {
        if (this._homeExampleToken !== token) return;
        this.setData({ homeExample: cached });
        return;
      }

      const res = await wordbookService.learningContent(wordId, {
        includeDraft: true,
        suggestionLimit: 0
      }).catch(() => null);
      const example = res && res.ok && res.learningContent
        ? normalizeHomeShortDefinition(res.learningContent)
        : null;
      if (!example || !example.text) continue;
      if (this._homeExampleToken !== token) return;

      wx.setStorageSync(HOME_SHORT_DEFINITION_CACHE_KEY(wordId), example);
      this.setData({ homeExample: example });
      return;
    }
  },

  onToggleHomeShortDefinition() {
    if (!this.data.homeExample || !this.data.homeExample.translationZh) return;
    this.setData({
      homeShortDefinitionRevealed: !this.data.homeShortDefinitionRevealed
    });
  },

  onSwitchBook() {
    wx.showToast({ title: '第一版暂不支持切换词书', icon: 'none' });
  },

  onOpenSearch() {
    const bookId = this.data.activeBook.id || DEFAULT_WORDBOOK_ID;
    wx.navigateTo({
      url: `/pages/search/index?bookId=${bookId}`,
      animationType: 'slide-in-top',
      animationDuration: 220
    });
  },

  onHomeTouchStart(e) {
    const touch = e.touches && e.touches[0];
    if (!touch || this.data.isLoading || this._pullSearchOpening) return;
    this._pullStartY = touch.clientY;
    this._pullStartX = touch.clientX;
    this._pullTracking = true;
  },

  onHomeTouchMove(e) {
    if (!this._pullTracking || this.data.isLoading || this._pullSearchOpening) return;
    const touch = e.touches && e.touches[0];
    if (!touch) return;

    const dy = touch.clientY - this._pullStartY;
    const dx = Math.abs(touch.clientX - this._pullStartX);
    if (dy <= 8 || dx > dy * 0.8) return;

    const distance = Math.min(96, Math.round(dy * 0.42));
    this.setData({
      pullSearchVisible: true,
      pullSearchDistance: distance,
      pullSearchOffset: distance - 86,
      pullSearchOpacity: Math.min(1, distance / 54)
    });
  },

  onHomeTouchEnd() {
    if (!this._pullTracking) return;
    this._pullTracking = false;

    const shouldOpen = this.data.pullSearchDistance >= 58;
    this.setData({
      pullSearchVisible: false,
      pullSearchDistance: 0,
      pullSearchOffset: -86,
      pullSearchOpacity: 0
    });

    if (!shouldOpen) return;
    if (this.data.isLoading || this._pullSearchOpening) return;
    this._pullSearchOpening = true;
    const bookId = this.data.activeBook.id || DEFAULT_WORDBOOK_ID;
    wx.navigateTo({
      url: `/pages/search/index?bookId=${bookId}`,
      animationType: 'slide-in-top',
      animationDuration: 220,
      complete: () => {
        setTimeout(() => {
          this._pullSearchOpening = false;
        }, 500);
      }
    });
  },

  onOpenFavorites() {
    const bookId = this.data.activeBook.id || DEFAULT_WORDBOOK_ID;
    wx.navigateTo({ url: `/pages/favorites/index?bookId=${bookId}` });
  },

  onOpenLearningHistory() {
    const bookId = this.data.activeBook.id || DEFAULT_WORDBOOK_ID;
    wx.navigateTo({ url: `/pages/learning-history/index?bookId=${bookId}` });
  },

  onOpenSettings() {
    wx.navigateTo({ url: '/pages/settings/index' });
  }
});
