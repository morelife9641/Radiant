import { listCloudWordbooks } from '../../../utils/wordbook-loader';
import { userService } from '../../../services/user';

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
  return Object.keys(progress).filter((word) => {
    const item = progress[word];
    return item && item.status !== 'ignored' && (item.correctCount > 0 || item.status === 'mastered');
  }).length;
}

async function loadBooks(options = {}) {
  const cloudBooks = await listCloudWordbooks(undefined, options).catch(() => []);
  return cloudBooks.map(decorate);
}

Page({
  data: {
    purpose: 'gaming',
    books: [],
    selected: ''
  },

  async onLoad(query) {
    const purpose = query.purpose || wx.getStorageSync('onboarding.purpose') || 'exam';
    const books = await loadBooks({ refresh: true });
    this.setData({ purpose, books });
  },

  onCoverError(e) {
    const id = e.currentTarget.dataset.id;
    const books = this.data.books.map((book) => (
      book.id === id ? { ...book, coverImage: '' } : book
    ));
    this.setData({ books });
  },

  onSelect(e) {
    const id = e.currentTarget.dataset.id;
    const book = this.data.books.find(b => b.id === id);
    if (!book) {
      wx.showToast({ title: '词书不存在', icon: 'none' });
      return;
    }
    this.setData({ selected: id });
  },

  async onNext() {
    if (!this.data.selected) return;
    wx.setStorageSync('onboarding.wordbook', this.data.selected);
    await userService.updateProfile({
      activeBookId: this.data.selected,
      purpose: this.data.purpose,
      onboarded: this.data.purpose !== 'gaming'
    }).catch(() => null);

    if (this.data.purpose === 'gaming') {
      wx.navigateTo({ url: '/pages/onboarding/interest/index' });
    } else {
      this.finish();
    }
  },

  finish() {
    wx.setStorageSync('onboarded', true);
    wx.reLaunch({ url: '/pages/home/index' });
  }
});
