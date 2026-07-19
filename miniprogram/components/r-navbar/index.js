const app = getApp();

Component({
  options: { styleIsolation: 'shared' },
  properties: {
    title: { type: String, value: '' },
    showBack: { type: Boolean, value: true },
    transparent: { type: Boolean, value: false }
  },
  data: {
    statusBarHeight: 44,
    navBarHeightPx: 88,
    actualHeightPx: 88,
    hasContent: true
  },
  attached() {
    const g = app && app.globalData ? app.globalData : {};
    const hasContent = Boolean(this.properties.title || this.properties.showBack);
    const statusBarHeight = g.statusBarHeight || 44;
    const navBarHeightPx = g.navBarHeightPx || 88;
    this.setData({
      statusBarHeight,
      navBarHeightPx,
      actualHeightPx: hasContent ? navBarHeightPx : statusBarHeight + 8,
      hasContent
    });
  },
  methods: {
    onBack() {
      const pages = getCurrentPages();
      if (pages.length > 1) {
        wx.navigateBack({ delta: 1 });
      } else {
        wx.reLaunch({ url: '/pages/home/index' });
      }
    }
  }
});
