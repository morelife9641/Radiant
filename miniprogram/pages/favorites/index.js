import { learnService } from '../../services/learn';
import { getWordsByWordsAsync } from '../../utils/wordbook-loader';
import { playWord } from '../../utils/audio';

const DEFAULT_WORDBOOK_ID = 'ielts_content_words';
const PROGRESS_KEY = (bookId) => `progress.${bookId}`;
const ACTION_OPEN_PX = 86;
const ACTION_TRIGGER_PX = 42;
const SORT_OPTIONS = ['最近收藏', 'A-Z 正序', 'A-Z 倒序'];

function getNavTopPx() {
  const app = getApp();
  const g = app && app.globalData ? app.globalData : {};
  return Math.ceil(g.navBarHeightPx || ((g.statusBarHeight || 44) + 48)) + 8;
}

function normalizeKey(value) {
  return String(value || '').trim().toLowerCase();
}

function formatPhonetic(phonetic) {
  if (!phonetic) return '';
  if (typeof phonetic === 'string') return phonetic;
  return String(phonetic.default || phonetic.us || phonetic.uk || '').trim();
}

function formatFavoriteTime(value) {
  const time = Number(value || 0);
  if (!time) return '时间未知';
  const date = new Date(time);
  const today = new Date();
  const startOfToday = new Date(today.getFullYear(), today.getMonth(), today.getDate()).getTime();
  const startOfFavoriteDay = new Date(date.getFullYear(), date.getMonth(), date.getDate()).getTime();
  const month = date.getMonth() + 1;
  const day = date.getDate();
  const hour = String(date.getHours()).padStart(2, '0');
  const minute = String(date.getMinutes()).padStart(2, '0');
  if (startOfFavoriteDay === startOfToday) return `今天 ${hour}:${minute}`;
  if (startOfFavoriteDay === startOfToday - 24 * 60 * 60 * 1000) return `昨天 ${hour}:${minute}`;
  return `${month}月${day}日 ${hour}:${minute}`;
}

function firstText(values) {
  for (const value of values) {
    if (typeof value === 'string' && value.trim()) return value.trim();
  }
  return '';
}

function trimInlineText(value) {
  return String(value || '')
    .replace(/\\n/g, '\n')
    .split(/\n+/)
    .map(line => line
      .replace(/^\s*(?:n|v|vi|vt|adj|adv|a|ad|prep|conj|pron|num|int|interj|phr|abbr|aux|modal|det|art|pl|sing|u|c|un|cn|ｎ|ｖ|ａｄｊ|ａｄｖ)\.?\s+/i, '')
      .trim())
    .filter(Boolean)
    .join(' · ')
    .replace(/\s+/g, ' ')
    .trim();
}

function formatTranslation(item = {}) {
  const sense = Array.isArray(item.senses) && item.senses[0] ? item.senses[0] : {};
  return firstText([
    item.translation,
    item.translationZh,
    sense.translation,
    sense.translationZh,
    sense.collinsZh,
    sense.collins_definition && sense.collins_definition.zh
  ]);
}

function formatPartOfSpeech(item = {}) {
  const sense = Array.isArray(item.senses) && item.senses[0] ? item.senses[0] : {};
  const pos = String(item.pos || sense.pos || '').trim();
  if (!pos) return '';
  return /[.]$/.test(pos) ? pos : `${pos}.`;
}

function sortFavoriteItems(items = [], sortIndex = 0) {
  const sorted = [...items];
  if (sortIndex === 1 || sortIndex === 2) {
    const direction = sortIndex === 1 ? 1 : -1;
    return sorted.sort((a, b) => direction * String(a.word || '').localeCompare(String(b.word || ''), 'en', { sensitivity: 'base' }));
  }
  return sorted.sort((a, b) => Number((b.progress || {}).favoritedAt || 0) - Number((a.progress || {}).favoritedAt || 0));
}

function formatDefinitionText(item = {}) {
  const sense = Array.isArray(item.senses) && item.senses[0] ? item.senses[0] : {};
  const content = item.learningContent || item.learning_content || {};
  const coreSense = content.coreSense && typeof content.coreSense === 'object'
    ? content.coreSense
    : {};
  const definition = firstText([
    coreSense.en,
    content.shortDefinitionEn,
    content.short_definition_en,
    item.shortDefinitionEn,
    item.short_definition_en,
    sense.definitionEn,
    sense.definition_en,
    sense.definition,
    sense.meaningEn,
    sense.meaning_en,
    sense.collinsEn,
    sense.collins_definition && sense.collins_definition.en
  ]);
  const normalized = trimInlineText(definition);
  if (!normalized) return '';

  // Keep the list concise by showing one complete core sentence, never a mixed example.
  const sentence = normalized.match(/^(.+?[.!?])(?:\s|$)/);
  return (sentence ? sentence[1] : normalized).trim();
}

function normalizeFavoriteItem(item = {}) {
  const progress = item.progress || {};
  return {
    ...item,
    wordId: item.wordId || item._id || progress.wordId || '',
    word: item.word || item.normalized || progress.word || progress.normalized || '',
    normalized: item.normalized || progress.normalized || item.word || '',
    phoneticText: formatPhonetic(item.phonetic),
    posText: formatPartOfSpeech(item),
    translationText: formatTranslation(item),
    definitionText: formatDefinitionText(item),
    favoriteTimeText: formatFavoriteTime(progress.favoritedAt || item.favoritedAt),
    actionWidth: 0,
    progress
  };
}

function loadProgress(bookId) {
  return wx.getStorageSync(PROGRESS_KEY(bookId)) || {};
}

function saveProgress(bookId, progress) {
  wx.setStorageSync(PROGRESS_KEY(bookId), progress);
}

function updateLocalFavorite(bookId, item, favorite) {
  const progress = loadProgress(bookId);
  const keys = Array.from(new Set([
    normalizeKey(item.normalized),
    normalizeKey(item.word),
    normalizeKey(item.wordId)
  ].filter(Boolean)));
  const key = keys.find(value => progress[value]) || normalizeKey(item.normalized || item.word);
  if (!key) return {};

  const now = Date.now();
  const prev = progress[key] || {};
  const next = {
    ...prev,
    wordId: item.wordId || prev.wordId || '',
    normalized: normalizeKey(item.normalized || item.word || key),
    word: item.word || prev.word || key,
    favorite,
    favoritedAt: favorite ? (prev.favoritedAt || now) : null,
    clientUpdatedAt: now,
    updatedAt: now
  };
  progress[key] = next;
  saveProgress(bookId, progress);
  return next;
}

function loadLocalFavoriteProgress() {
  let keys = [];
  try {
    keys = (wx.getStorageInfoSync && wx.getStorageInfoSync().keys) || [];
  } catch (e) {
    keys = [];
  }

  const byWord = {};
  keys
    .filter(key => /^progress\.[^.]+$/.test(key))
    .forEach((storageKey) => {
      const progress = wx.getStorageSync(storageKey) || {};
      Object.keys(progress).forEach((wordKey) => {
        const item = progress[wordKey] || {};
        if (!item.favorite) return;
        const key = normalizeKey(item.normalized || item.word || wordKey);
        if (!key) return;
        byWord[key] = {
          wordId: item.wordId || '',
          word: item.word || item.normalized || wordKey,
          normalized: key,
          progress: item
        };
      });
    });

  return Object.values(byWord)
    .sort((a, b) => Number((b.progress || {}).favoritedAt || 0) - Number((a.progress || {}).favoritedAt || 0));
}

Page({
  data: {
    bookId: DEFAULT_WORDBOOK_ID,
    items: [],
    loading: true,
    navTopPx: 96,
    sortOptions: SORT_OPTIONS,
    sortIndex: 0,
    sortLabel: SORT_OPTIONS[0]
  },

  _hasLoaded: false,
  _favoriteItems: [],

  onLoad(query) {
    const bookId = query.bookId || DEFAULT_WORDBOOK_ID;
    this.setData({ bookId, navTopPx: getNavTopPx() });
    this.loadFavorites();
  },

  onShow() {
    if (!this._hasLoaded) return;
    this.loadFavorites();
  },

  async loadFavorites() {
    this.setData({ loading: true });
    const cloudRes = await learnService.listFavorites(this.data.bookId, { limit: 100 }).catch(() => null);
    if (cloudRes && cloudRes.ok && Array.isArray(cloudRes.items) && cloudRes.items.length) {
      this.setFavoriteItems(cloudRes.items.map(normalizeFavoriteItem), false);
      this._hasLoaded = true;
      return;
    }

    const localItems = loadLocalFavoriteProgress();
    const words = await getWordsByWordsAsync(this.data.bookId, localItems.map(item => item.normalized || item.word)).catch(() => []);
    const wordMap = words.reduce((map, word) => {
      map[normalizeKey(word.normalized || word.word)] = word;
      return map;
    }, {});
    const items = localItems.map((item) => normalizeFavoriteItem({
      ...(wordMap[normalizeKey(item.normalized || item.word)] || {}),
      ...item
    }));

    this.setFavoriteItems(items, false);
    this._hasLoaded = true;
  },

  setFavoriteItems(items = [], loading = false) {
    this._favoriteItems = items;
    this.setData({
      items: sortFavoriteItems(items, this.data.sortIndex),
      loading
    });
  },

  onSortChange(e) {
    const sortIndex = Number(e.detail && e.detail.value);
    const nextIndex = Number.isInteger(sortIndex) && SORT_OPTIONS[sortIndex] ? sortIndex : 0;
    this.setData({
      sortIndex: nextIndex,
      sortLabel: SORT_OPTIONS[nextIndex],
      items: sortFavoriteItems(this._favoriteItems, nextIndex)
    });
  },

  onBack() {
    wx.navigateBack({
      fail: () => wx.reLaunch({ url: '/pages/home/index' })
    });
  },

  onOpenWord(e) {
    const { word } = e.currentTarget.dataset;
    if (!word) return;
    wx.navigateTo({
      url: `/pages/word-detail/index?bookId=${this.data.bookId}&word=${encodeURIComponent(word)}`
    });
  },

  onGoLearn() {
    wx.navigateTo({ url: '/pages/learn/index' });
  },

  onPlayWord(e) {
    const { word } = e.currentTarget.dataset;
    playWord(word);
  },

  onTouchStart(e) {
    const { index } = e.currentTarget.dataset;
    const touch = e.touches && e.touches[0];
    if (!touch) return;
    this.closeOtherActions(Number(index));
    this._swipe = {
      index: Number(index),
      startX: touch.clientX,
      baseWidth: Number((this.data.items[index] || {}).actionWidth || 0)
    };
  },

  onTouchMove(e) {
    if (!this._swipe) return;
    const touch = e.touches && e.touches[0];
    if (!touch) return;
    const dx = touch.clientX - this._swipe.startX;
    const nextWidth = Math.max(0, Math.min(ACTION_OPEN_PX, this._swipe.baseWidth - dx));
    this.setActionWidth(this._swipe.index, nextWidth);
  },

  onTouchEnd() {
    if (!this._swipe) return;
    const index = this._swipe.index;
    const item = this.data.items[index] || {};
    const nextWidth = Number(item.actionWidth || 0) >= ACTION_TRIGGER_PX ? ACTION_OPEN_PX : 0;
    this.setActionWidth(index, nextWidth);
    this._swipe = null;
  },

  setActionWidth(index, actionWidth) {
    if (!Number.isInteger(index) || index < 0) return;
    this.setData({ [`items[${index}].actionWidth`]: actionWidth });
  },

  closeOtherActions(activeIndex) {
    const updates = {};
    this.data.items.forEach((item, index) => {
      if (index !== activeIndex && Number(item.actionWidth || 0) > 0) {
        updates[`items[${index}].actionWidth`] = 0;
      }
    });
    if (Object.keys(updates).length) this.setData(updates);
  },

  async onCancelFavorite(e) {
    const { index } = e.currentTarget.dataset;
    const item = this.data.items[index];
    if (!item) return;

    const progress = updateLocalFavorite(this.data.bookId, item, false);
    wx.showToast({ title: '已取消收藏', icon: 'none' });
    await learnService.updateWordState({
      bookId: this.data.bookId,
      wordId: item.wordId || progress.wordId,
      word: item.word || progress.word,
      normalized: item.normalized || progress.normalized || item.word,
      favorite: false,
      favoritedAt: null,
      clientUpdatedAt: progress.clientUpdatedAt || Date.now()
    }).catch((err) => {
      console.warn('[favorites] cancel favorite sync failed', err);
    });
    this.loadFavorites();
  }
});
