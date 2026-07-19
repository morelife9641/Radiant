import { APP_VERSION, DAILY_GOAL_OPTIONS, normalizeDailyGoal } from '../../config/index';
import { learnService } from '../../services/learn';
import { userService } from '../../services/user';
import { getDateKeyAsiaShanghai } from '../../utils/date';
import {
  clearProfilePending,
  getUserProfileFromCache,
  hydrateProfileCache,
  markProfilePending
} from '../../utils/profile-cache';

function getNavTopPx() {
  const app = getApp();
  const g = app && app.globalData ? app.globalData : {};
  return Math.ceil(g.navBarHeightPx || ((g.statusBarHeight || 44) + 48)) + 8;
}

function resetTodayLearningStorage() {
  const dateKey = getDateKeyAsiaShanghai();
  const resetAt = Date.now();
  const storageInfo = wx.getStorageInfoSync() || {};
  const keys = Array.isArray(storageInfo.keys) ? storageInfo.keys : [];
  const sessionSuffix = `.${dateKey}`;

  wx.setStorageSync('learnReset.today', { dateKey, resetAt });

  keys.forEach((key) => {
    if (
      (
        key.endsWith(sessionSuffix)
        && (
          key.startsWith('today.')
          || key.startsWith('todayDone.')
          || key.startsWith('learnSession.')
          || key.startsWith('learnSessionClear.')
        )
      )
      || /^learnHistory\..+\.(daily|review)$/.test(key)
      || key.startsWith('progressSync.v2.')
      || key.startsWith('progressOutbox.')
    ) {
      wx.removeStorageSync(key);
      return;
    }

    if (!key.startsWith('progress.')) return;
    const progress = wx.getStorageSync(key) || {};
    let changed = false;
    Object.keys(progress).forEach((wordKey) => {
      const item = progress[wordKey];
      if (!item || typeof item !== 'object') return;
      let touchedToday = false;
      if (item.dailyDoneDateKey === dateKey) {
        item.dailyDoneDateKey = '';
        changed = true;
        touchedToday = true;
      }
      if (item.dailyWrongDateKey === dateKey) {
        item.dailyWrongDateKey = '';
        changed = true;
        touchedToday = true;
      }
      if (touchedToday && item.dailyRecoveryCorrectCount) {
        item.dailyRecoveryCorrectCount = 0;
        changed = true;
      }
      if (item._todayDone) {
        item._todayDone = false;
        changed = true;
      }
    });
    if (changed) wx.setStorageSync(key, progress);
  });
}

function resetLearningStorage() {
  const storageInfo = wx.getStorageInfoSync() || {};
  const keys = Array.isArray(storageInfo.keys) ? storageInfo.keys : [];
  wx.setStorageSync('learnReset.today', { dateKey: getDateKeyAsiaShanghai(), resetAt: Date.now() });

  keys.forEach((key) => {
    if (
      key.startsWith('progress.')
      || key.startsWith('progressOutbox.')
      || key.startsWith('today.')
      || key.startsWith('todayDone.')
      || key.startsWith('learnSession.')
      || key.startsWith('learnSessionClear.')
      || key.startsWith('learnHistory.')
      || key.startsWith('progressSync.')
    ) {
      wx.removeStorageSync(key);
    }
  });
}

function getSyncErrorMessage(result, error) {
  if (error && error.errMsg) return error.errMsg;
  if (error && error.message) return error.message;
  if (result && result.message) {
    return result.code ? `${result.code}: ${result.message}` : result.message;
  }
  return '未收到云端成功响应，请确认 user-sync 已部署到当前云环境。';
}

function showProfileSyncResult(success, result, error) {
  if (success) {
    wx.showToast({ title: '已保存并同步', icon: 'success' });
    return;
  }

  wx.showModal({
    title: '云端同步失败',
    content: `${getSyncErrorMessage(result, error)}\n\n本次设置已暂存在本机，联网后会自动重试。清除缓存前请先确保云端同步成功。`,
    showCancel: false,
    confirmText: '知道了'
  });
}

Page({
  data: {
    nickname: '同学',
    dailyGoal: 10,
    enableSpellingQuestions: false,
    version: APP_VERSION,
    contactEmail: '1391256837@qq.com',
    navTopPx: 96,
    actionLoading: false,
    actionLoadingTitle: ''
  },

  async onShow() {
    const profile = await getUserProfileFromCache({ force: true });
    this.setData({
      nickname: profile.nickname || '同学',
      dailyGoal: normalizeDailyGoal(profile.dailyGoal),
      enableSpellingQuestions: profile.enableSpellingQuestions === true,
      navTopPx: getNavTopPx()
    });
  },

  onBack() {
    const pages = getCurrentPages();
    if (pages.length > 1) {
      wx.navigateBack({ delta: 1 });
    } else {
      wx.reLaunch({ url: '/pages/home/index' });
    }
  },

  onChangeNickname() {
    wx.showModal({
      title: '修改称呼',
      editable: true,
      placeholderText: '比如：同学',
      content: this.data.nickname,
      success: async (res) => {
        if (!res.confirm) return;
        const nickname = String(res.content || '').trim().slice(0, 12) || '同学';
        wx.setStorageSync('settings.nickname', nickname);
        this.setData({ nickname });
        let syncError = null;
        const result = await userService.updateProfile({ nickname }).catch((err) => {
          syncError = err;
          console.warn('[settings] sync nickname failed', err);
          return null;
        });
        const synced = Boolean(
          result
          && result.ok
          && result.profile
          && result.profile.nickname === nickname
        );
        if (synced) {
          clearProfilePending(['nickname']);
          hydrateProfileCache(result.profile);
        } else {
          if (result && result.ok) {
            syncError = new Error('云端返回的称呼与本次设置不一致，请重新部署 user-sync。');
          } else if (result) {
            console.warn('[settings] sync nickname rejected', result.code, result.message);
          }
          markProfilePending({ nickname });
        }
        showProfileSyncResult(synced, result, syncError);
      }
    });
  },

  onChangeDailyGoal() {
    wx.showActionSheet({
      itemList: DAILY_GOAL_OPTIONS.map(value => `${value} 个 / 天`),
      success: async (res) => {
        const dailyGoal = DAILY_GOAL_OPTIONS[res.tapIndex];
        wx.setStorageSync('settings.dailyGoal', dailyGoal);
        this.setData({ dailyGoal });
        let syncError = null;
        const result = await userService.updateProfile({ dailyGoal }).catch((err) => {
          syncError = err;
          console.warn('[settings] sync daily goal failed', err);
          return null;
        });
        const synced = Boolean(
          result
          && result.ok
          && result.profile
          && normalizeDailyGoal(result.profile.dailyGoal) === dailyGoal
        );
        if (synced) {
          clearProfilePending(['dailyGoal']);
          hydrateProfileCache(result.profile);
        } else {
          if (result && result.ok) {
            syncError = new Error('云端返回的每日目标与本次设置不一致，请重新部署 user-sync。');
          } else if (result) {
            console.warn('[settings] sync daily goal rejected', result.code, result.message);
          }
          markProfilePending({ dailyGoal });
        }
        showProfileSyncResult(synced, result, syncError);
      }
    });
  },

  async onToggleSpellingQuestions(e) {
    const enableSpellingQuestions = Boolean(e.detail && e.detail.value);
    wx.setStorageSync('settings.enableSpellingQuestions', enableSpellingQuestions);
    this.setData({ enableSpellingQuestions });

    let syncError = null;
    const result = await userService.updateProfile({ enableSpellingQuestions }).catch((err) => {
      syncError = err;
      console.warn('[settings] sync spelling preference failed', err);
      return null;
    });
    const synced = Boolean(
      result
      && result.ok
      && result.profile
      && result.profile.enableSpellingQuestions === enableSpellingQuestions
    );
    if (synced) {
      clearProfilePending(['enableSpellingQuestions']);
      hydrateProfileCache(result.profile);
    } else {
      if (result && result.ok) {
        syncError = new Error('云端返回的拼写题设置与本次选择不一致，请重新部署 user-sync。');
      } else if (result) {
        console.warn('[settings] sync spelling preference rejected', result.code, result.message);
      }
      markProfilePending({ enableSpellingQuestions });
    }
    showProfileSyncResult(synced, result, syncError);
  },

  onResetTodayLearning() {
    wx.showModal({
      title: '重置今日学习？',
      content: '会清空今天的答题队列、结算记录和今日完成标记，不会删除收藏和长期学习进度。',
      confirmText: '重置',
      confirmColor: '#D93025',
      success: async (res) => {
        if (!res.confirm) return;
        this.setData({ actionLoading: true, actionLoadingTitle: '正在重置今日学习' });
        try {
          resetTodayLearningStorage();
          await learnService.resetTodayProgress().catch((err) => {
            console.warn('[settings] reset today progress cloud sync failed', err);
            return null;
          });
          resetTodayLearningStorage();
        } finally {
          this.setData({ actionLoading: false, actionLoadingTitle: '' });
        }
        wx.showToast({ title: '今日学习已重置', icon: 'success' });
        setTimeout(() => wx.reLaunch({ url: '/pages/home/index' }), 450);
      }
    });
  },

  onResetLearningProgress() {
    wx.showModal({
      title: '清空学习进度？',
      content: '会删除云端和本地的单词学习进度、复习队列、今日记录和答题历史，不会清除昵称、每日目标和收藏入口设置。',
      confirmText: '清空',
      confirmColor: '#D93025',
      success: async (res) => {
        if (!res.confirm) return;
        this.setData({ actionLoading: true, actionLoadingTitle: '正在清空学习进度' });
        let result = null;
        try {
          result = await learnService.resetProgress().catch((err) => {
            console.warn('[settings] reset progress failed', err);
            return null;
          });
          resetLearningStorage();
        } finally {
          this.setData({ actionLoading: false, actionLoadingTitle: '' });
        }
        if (!result || !result.ok) {
          wx.showToast({ title: '云端清空失败，本地已清理', icon: 'none' });
          return;
        }
        wx.showToast({ title: '学习进度已清空', icon: 'success' });
        setTimeout(() => wx.reLaunch({ url: '/pages/home/index' }), 450);
      }
    });
  },

  onAbout() {
    wx.showModal({
      title: 'Radiant.AI',
      content: `v${APP_VERSION}\nLight up your English.`,
      showCancel: false
    });
  },

  onPrivacy() {
    wx.showModal({
      title: '数据与隐私',
      content: 'Radiant 会保存你的微信侧账号标识、称呼、学习偏好、所选词书和单词学习进度，用于跨设备同步学习。数据不会用于广告投放。你可以在本页清除账号与学习数据。',
      showCancel: false
    });
  },

  onContactDeveloper() {
    wx.setClipboardData({
      data: this.data.contactEmail,
      success: () => {
        wx.showToast({ title: '邮箱已复制', icon: 'success' });
      }
    });
  },

  onDeleteAccountData() {
    wx.showModal({
      title: '确认清除全部数据？',
      content: '这会永久删除云端账号资料和全部单词学习进度，且无法恢复。',
      confirmText: '确认清除',
      confirmColor: '#D93025',
      success: async (res) => {
        if (!res.confirm) return;
        this.setData({ actionLoading: true, actionLoadingTitle: '正在清除账号数据' });
        const result = await userService.deleteAccountData().catch(() => null);
        if (!result || !result.ok) {
          this.setData({ actionLoading: false, actionLoadingTitle: '' });
          wx.showToast({ title: '清除失败，请稍后重试', icon: 'none' });
          return;
        }
        wx.clearStorageSync();
        wx.reLaunch({ url: '/pages/home/index' });
      }
    });
  }
});
