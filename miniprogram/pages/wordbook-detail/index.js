import { getMetaAsync, getWordsPage } from '../../utils/wordbook-loader';

const PAGE_LIMIT = 100;
const PREFETCH_DISTANCE = 1200;
const SCROLL_THROTTLE_MS = 180;

Page({
  data: {
    bookId: '',
    book: null,
    displayWords: [],
    total: 0,
    cursor: '',
    sortMode: 'order',
    loading: false,
    finished: false
  },

  _words: [],
  _loadingNext: false,
  _lastScrollCheckAt: 0,
  _loadVersion: 0,

  async onLoad(query) {
    const bookId = query.bookId || '';
    if (!bookId) {
      wx.showToast({ title: '缺少词书', icon: 'none' });
      setTimeout(() => wx.navigateBack(), 1000);
      return;
    }

    const book = await getMetaAsync(bookId).catch(() => null);

    if (!book) {
      wx.showToast({ title: '词书未找到', icon: 'none' });
      setTimeout(() => wx.navigateBack(), 1000);
      return;
    }

    wx.setNavigationBarTitle({ title: book.name || '词书详情' });
    this.setData({
      bookId,
      book,
      displayWords: [],
      total: book.totalWords || 0,
      cursor: '',
      sortMode: 'order',
      finished: false
    });
    this._words = [];
    this._loadVersion += 1;
    this.loadNext({ prefetchAfter: true });
  },

  async loadNext(options = {}) {
    if (this._loadingNext || this.data.finished) return;
    const version = this._loadVersion;
    const silent = Boolean(options.silent);
    this._loadingNext = true;
    if (!silent) this.setData({ loading: true });

    const page = await getWordsPage(this.data.bookId, {
      limit: PAGE_LIMIT,
      cursor: this.data.cursor,
      sort: this.data.sortMode
    }).catch(() => null);

    if (version !== this._loadVersion) {
      this._loadingNext = false;
      return;
    }

    if (!page) {
      this._loadingNext = false;
      if (!silent) this.setData({ loading: false });
      wx.showToast({ title: '单词加载失败', icon: 'none' });
      return;
    }

    this._words = this._words.concat(page.items || []);
    this.setData({
      displayWords: this._words,
      total: page.total || this.data.total,
      cursor: page.cursor || '',
      finished: !page.cursor,
      loading: false
    });
    this._loadingNext = false;

    if (options.prefetchAfter && page.cursor) {
      setTimeout(() => this.loadNext({ silent: true }), 120);
    }
  },

  onSwitchSort(e) {
    const sortMode = e.currentTarget.dataset.mode || 'order';
    if (sortMode === this.data.sortMode) return;
    this._words = [];
    this._loadVersion += 1;
    this._loadingNext = false;
    this.setData({
      sortMode,
      displayWords: [],
      cursor: '',
      loading: false,
      finished: false
    });
    this.loadNext({ prefetchAfter: true });
  },

  onReachBottom() {
    this.loadNext();
  },

  onScrollToLower() {
    this.loadNext({ silent: true });
  },

  onListScroll(e) {
    const now = Date.now();
    if (now - this._lastScrollCheckAt < SCROLL_THROTTLE_MS) return;
    this._lastScrollCheckAt = now;

    const detail = e.detail || {};
    const distance = Number(detail.scrollHeight || 0) - Number(detail.scrollTop || 0) - Number(detail.clientHeight || 0);
    if (distance > 0 && distance < PREFETCH_DISTANCE) {
      this.loadNext({ silent: true });
    }
  },

  onOpenWord(e) {
    const { word } = e.currentTarget.dataset;
    if (!word) return;
    wx.navigateTo({
      url: `/pages/word-detail/index?bookId=${this.data.bookId}&word=${encodeURIComponent(word)}`
    });
  },

  onOpenSearch() {
    wx.navigateTo({
      url: `/pages/search/index?bookId=${this.data.bookId}`
    });
  }
});
