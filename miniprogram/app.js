import { CLOUD_ENV } from './config/index';
import { visualService } from './services/visual';
import { hydrateProfileCache, refreshProfileCache } from './utils/profile-cache';

const DEFAULT_WORDBOOK_ID = 'ielts_content_words';

App({
  globalData: {
    userInfo: null,
    statusBarHeight: 44,    // px
    navBarHeight: 88        // rpx，胶囊按钮区域统一 88rpx
  },

  onLaunch() {
    if (!wx.cloud) {
      console.error('请使用 2.2.3 或以上的基础库');
      return;
    }
    wx.cloud.init({
      env: CLOUD_ENV,
      traceUser: true
    });

    visualService.refreshDevelopmentCache();
    this.measureChrome();
    setTimeout(() => this.routeFirstScreen(), 0);
  },

  measureChrome() {
    try {
      const sys = wx.getWindowInfo ? wx.getWindowInfo() : wx.getSystemInfoSync();
      const statusBarHeight = sys.statusBarHeight || 20;
      // 胶囊按钮区域（仅微信客户端有）
      let menuTop = statusBarHeight + 4;
      let menuHeight = 32;
      if (wx.getMenuButtonBoundingClientRect) {
        const m = wx.getMenuButtonBoundingClientRect();
        if (m && m.height) {
          menuTop = m.top;
          menuHeight = m.height;
        }
      }
      // navBarHeight 包含: status bar + 上下间距 + 胶囊高度
      const navBarHeightPx = (menuTop - statusBarHeight) * 2 + menuHeight + statusBarHeight;
      this.globalData.statusBarHeight = statusBarHeight;
      this.globalData.navBarHeightPx = navBarHeightPx;
    } catch (e) {
      console.warn('measureChrome failed', e);
    }
  },

  hydrateProfileCache(profile) {
    hydrateProfileCache(profile);
  },

  async refreshProfileCache() {
    return refreshProfileCache({ force: true });
  },

  async routeFirstScreen() {
    this.refreshProfileCache();
  }
});
