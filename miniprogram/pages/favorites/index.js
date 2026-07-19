import { learnService } from '../../services/learn';
import { getWordsByWordsAsync } from '../../utils/wordbook-loader';
import { playWord } from '../../utils/audio';

const DEFAULT_WORDBOOK_ID = 'ielts_content_words';
const PROGRESS_KEY = (bookId) => `progress.${bookId}`;
const ACTION_OPEN_PX = 86;
const ACTION_TRIGGER_PX = 42;

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
  const month = date.getMonth() + 1;
  const day = date.getDate();
  const hour = String(date.getHours()).padStart(2, '0');
  const minute = String(date.getMinutes()).padStart(2, '0');
  return `${month}月${day}日 ${hour}:${minute}`;
}

function formatStatus(status) {
  const map = {
    new: '未开始',
    learning: '学习中',
    reviewing: '待巩固',
    difficult: '重点复习',
    mastered: '已掌握',
    ignored: '已删除'
  };
  return map[status] || '学习中';
}

function formatProgressInfo(progress = {}) {
  const correct = Number(progress.correctCount || 0);
  const wrong = Number(progress.wrongCount || 0);
  const statusText = formatStatus(progress.status || '');
  if (!correct && !wrong) return statusText;
  return `${statusText} · ${correct} 对 / ${wrong} 错`;
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

function pickObjectText(item = {}) {
  if (!item || typeof item !== 'object') return '';
  const main = firstText([
    item.text,
    item.phrase,
    item.collocation,
    item.exampleEn,
    item.example_en,
    item.sentence,
    item.en
  ]);
  const sub = firstText([
    item.translationZh,
    item.translation_zh,
    item.exampleZh,
    item.example_zh,
    item.zh
  ]);
  if (main && sub) return `${main} · ${sub}`;
  return main || sub;
}

function findArrayText(arr = []) {
  if (!Array.isArray(arr)) return '';
  for (const item of arr) {
    const text = typeof item === 'string' ? item : pickObjectText(item);
    if (text) return text;
  }
  return '';
}

function formatExtraText(item = {}) {
  const sense = Array.isArray(item.senses) && item.senses[0] ? item.senses[0] : {};
  const content = item.learningContent || item.learning_content || {};
  const synonyms = Array.isArray(sense.synonyms) ? sense.synonyms : [];
  const extra = firstText([
    findArrayText(content.collocations),
    findArrayText(item.collocations),
    findArrayText(sense.collocations),
    findArrayText(content.examples),
    findArrayText(item.examples),
    findArrayText(sense.examples),
    pickObjectText(sense.gaming_link),
    sense.exampleEn,
    sense.example_en,
    synonyms[0] && (synonyms[0].exampleEn || synonyms[0].example_en),
    sense.definitionEn,
    sense.definition_en,
    sense.definition,
    sense.meaningEn,
    sense.meaning_en,
    sense.collinsEn,
    sense.collins_definition && sense.collins_definition.en
  ]);
  return trimInlineText(extra);
}

function normalizeFavoriteItem(item = {}) {
  const progress = item.progress || {};
  return {
    ...item,
    wordId: item.wordId || item._id || progress.wordId || '',
    word: item.word || item.normalized || progress.word || progress.normalized || '',
    normalized: item.normalized || progress.normalized || item.word || '',
    phoneticText: formatPhonetic(item.phonetic),
    translationText: formatTranslation(item),
    extraText: formatExtraText(item),
    favoriteTimeText: formatFavoriteTime(progress.favoritedAt || item.favoritedAt),
    infoText: formatProgressInfo(progress),
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
    navTopPx: 96
  },

  _hasLoaded: false,

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
      this.setData({
        items: cloudRes.items.map(normalizeFavoriteItem),
        loading: false
      });
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

    this.setData({ items, loading: false });
    this._hasLoaded = true;
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
