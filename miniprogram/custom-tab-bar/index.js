Component({
  data: {
    hidden: true,
    selected: 0,
    list: [
      { pagePath: '/pages/home/index', text: '今日' },
      { pagePath: '/pages/chat/index', text: '对话' },
      { pagePath: '/pages/profile/index', text: '我的' }
    ]
  },
  methods: {
    switchTab(e) {
      const { index, path } = e.currentTarget.dataset;
      this.setData({ selected: index });
      wx.switchTab({ url: path });
    }
  }
});
