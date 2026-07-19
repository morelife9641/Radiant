import { getMetaAsync, searchWordsAsync } from '../../utils/wordbook-loader';

const DEFAULT_WORDBOOK_ID = 'ielts_content_words';
const SEARCH_DELAY = 180;

function getNavTopPx() {
  const app = getApp();
  const g = app && app.globalData ? app.globalData : {};
  return Math.ceil(g.navBarHeightPx || ((g.statusBarHeight || 44) + 48)) + 8;
}

Page({
  data: {
    bookId: '',
    bookName: '',
    keyword: '',
    results: [],
    loading: false,
    searched: false,
    navTopPx: 96
  },

  _timer: null,
  _searchVersion: 0,

  async onLoad(query) {
    this.setData({ navTopPx: getNavTopPx() });
    const bookId = query.bookId || DEFAULT_WORDBOOK_ID;
    const keyword = decodeURIComponent(query.q || '');
    const book = await getMetaAsync(bookId).catch(() => null);

    wx.setNavigationBarTitle({ title: '搜索单词' });
    this.setData({
      bookId,
      bookName: book ? book.name : '当前词书',
      keyword
    });

    if (keyword) this.search(keyword);
  },

  onInput(e) {
    const keyword = e.detail.value || '';
    this.setData({ keyword });
    clearTimeout(this._timer);
    this._timer = setTimeout(() => this.search(keyword), SEARCH_DELAY);
  },

  onConfirm(e) {
    const keyword = e.detail.value || this.data.keyword;
    clearTimeout(this._timer);
    this.search(keyword);
  },

  onClear() {
    clearTimeout(this._timer);
    this.setData({ keyword: '', results: [], loading: false, searched: false });
  },

  onBack() {
    wx.navigateBack({
      fail: () => wx.reLaunch({ url: '/pages/home/index' })
    });
  },

  async search(rawKeyword) {
    const keyword = String(rawKeyword || '').trim();
    const version = this._searchVersion + 1;
    this._searchVersion = version;

    if (!keyword) {
      this.setData({ results: [], loading: false, searched: false });
      return;
    }

    this.setData({ loading: true, searched: true });
    const results = await searchWordsAsync(this.data.bookId, keyword, { limit: 30 }).catch(() => []);
    if (version !== this._searchVersion) return;

    this.setData({ results, loading: false });
  },

  onOpenWord(e) {
    const { word } = e.currentTarget.dataset;
    if (!word) return;
    wx.navigateTo({
      url: `/pages/word-detail/index?bookId=${this.data.bookId}&word=${encodeURIComponent(word)}`
    });
  }
});
