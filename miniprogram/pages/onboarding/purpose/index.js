Page({
  data: {
    options: [
      { key: 'gaming', emoji: '🎮', title: '游戏交流', desc: '学游戏术语、和队友开麦、看懂英文社区' },
      { key: 'exam',   emoji: '📘', title: '备考',     desc: '四六级 / 雅思 / 托福 / 考研' }
    ],
    selected: ''
  },

  onSelect(e) {
    this.setData({ selected: e.currentTarget.dataset.key });
  },

  onNext() {
    if (!this.data.selected) return;
    wx.setStorageSync('onboarding.purpose', this.data.selected);
    wx.setStorageSync('onboarding.wordbook', 'ielts_content_words');
    if (this.data.selected === 'gaming') {
      wx.navigateTo({ url: '/pages/onboarding/interest/index' });
    } else {
      wx.setStorageSync('onboarded', true);
      wx.reLaunch({ url: '/pages/home/index' });
    }
  }
});
