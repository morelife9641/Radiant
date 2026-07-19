import { listCloudWordbooks } from '../../utils/wordbook-loader';
import { userService } from '../../services/user';

function normalizeKey(value) {
  return String(value || '').trim().toLowerCase();
}

function isKnownProgress(progress) {
  return progress
    && progress.status !== 'ignored'
    && (Number(progress.correctCount || 0) > 0 || progress.status === 'mastered');
}

function decorate(book) {
  const sourceCover = normalizeCover(book.cover);
  const totalWords = Number(book.totalWords || 0);
  const knownWords = countKnownWords(book.id);

  return {
    ...book,
    name: book.name || book.title,
    letter: book.letter || sourceCover.letter || (book.name || book.title || '').slice(0, 1),
    level: book.level || book.cefrLevel || '',
    cover: sourceCover,
    coverColor: book.coverColor || sourceCover.color || '#1A1A1A',
    coverImage: book.coverImage || sourceCover.image || '',
    totalWords,
    knownWords,
    progressText: `已认识 ${knownWords}/${totalWords}`
  };
}

function normalizeCover(cover) {
  if (!cover) return {};
  return typeof cover === 'string' ? { color: cover } : cover;
}

function countKnownWords(bookId) {
  const progress = wx.getStorageSync(`progress.${bookId}`) || {};
  const known = new Set();
  Object.keys(progress).forEach((word) => {
    const item = progress[word];
    if (!isKnownProgress(item)) return;
    known.add(normalizeKey(item.wordId || item.normalized || item.word || word));
  });
  return known.size;
}

async function loadBooks(options = {}) {
  const cloudBooks = await listCloudWordbooks(undefined, options).catch(() => []);
  return cloudBooks.map(decorate);
}

Page({
  data: {
    books: [],
    activeId: ''
  },

  _loadedOnce: false,
  _skipNextShow: false,
  _lastLoadedAt: 0,

  async onLoad() {
    const activeId = wx.getStorageSync('onboarding.wordbook') || '';
    const books = await loadBooks();
    this._loadedOnce = true;
    this._skipNextShow = true;
    this._lastLoadedAt = Date.now();
    this.setData({
      books,
      activeId
    });
  },

  async onShow() {
    if (this._skipNextShow) {
      this._skipNextShow = false;
      return;
    }
    if (!this._loadedOnce) return;
    const now = Date.now();
    if (now - this._lastLoadedAt < 60 * 1000) {
      this.setData({ activeId: wx.getStorageSync('onboarding.wordbook') || '' });
      return;
    }
    const books = await loadBooks({ refresh: true });
    this._lastLoadedAt = now;
    this.setData({ books });
  },

  onCoverError(e) {
    const id = e.currentTarget.dataset.id;
    const books = this.data.books.map((book) => (
      book.id === id ? { ...book, coverImage: '' } : book
    ));
    this.setData({ books });
  },

  onOpenBook(e) {
    const id = e.currentTarget.dataset.id;
    const book = this.data.books.find(b => b.id === id);
    if (!book) {
      wx.showToast({ title: '词书不存在', icon: 'none' });
      return;
    }
    wx.navigateTo({ url: `/pages/wordbook-detail/index?bookId=${id}` });
  },

  async onActivate(e) {
    const id = e.currentTarget.dataset.id;
    const book = this.data.books.find(b => b.id === id);
    if (!book) {
      wx.showToast({ title: '词书不存在', icon: 'none' });
      return;
    }
    if (id === this.data.activeId) {
      wx.navigateBack();
      return;
    }
    wx.setStorageSync('onboarding.wordbook', id);
    wx.setStorageSync('onboarded', true);
    await userService.updateProfile({
      activeBookId: id,
      onboarded: true
    }).catch(() => null);
    this.setData({ activeId: id });
    wx.showToast({ title: '已切换', icon: 'success' });
  }
});
