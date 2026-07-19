Page({
  data: {
    nickname: '同学',
    avatarLetter: 'R',
    streakDays: 0
  },

  onShow() {
    if (typeof this.getTabBar === 'function' && this.getTabBar()) {
      this.getTabBar().setData({ selected: 2 });
    }
  },

  onSearch() { wx.navigateTo({ url: '/pages/search/index' }); },
  onWordbookList() { wx.navigateTo({ url: '/pages/wordbook-list/index' }); },
  onMastered() { wx.showToast({ title: '待开发', icon: 'none' }); },
  onWrongbook() { wx.showToast({ title: '待开发', icon: 'none' }); },
  onSettings() { wx.navigateTo({ url: '/pages/settings/index' }); }
});
