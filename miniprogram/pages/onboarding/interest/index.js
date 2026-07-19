import { userService } from '../../../services/user';

Page({
  data: {
    options: [
      { key: 'dota2',    emoji: '🎲', label: 'Dota 2' },
      { key: 'valorant', emoji: '🎯', label: 'Valorant' },
      { key: 'lol',      emoji: '⚔️', label: 'LoL' },
      { key: 'cs2',      emoji: '🔫', label: 'CS2' },
      { key: 'apex',     emoji: '🪂', label: 'Apex' },
      { key: 'genshin',  emoji: '✨', label: '原神' },
      { key: 'movies',   emoji: '🎬', label: '影视剧' }
    ],
    selected: {},
    selectedCount: 0
  },

  onToggle(e) {
    const key = e.currentTarget.dataset.key;
    const next = { ...this.data.selected };
    if (next[key]) delete next[key]; else next[key] = true;
    this.setData({
      selected: next,
      selectedCount: Object.keys(next).length
    });
  },

  async onDone() {
    if (this.data.selectedCount === 0) return;
    const interests = Object.keys(this.data.selected);
    wx.setStorageSync('onboarding.interests', interests);
    wx.setStorageSync('onboarding.wordbook', 'ielts_content_words');
    wx.setStorageSync('onboarded', true);
    await userService.updateProfile({
      preferences: interests,
      activeBookId: 'ielts_content_words',
      onboarded: true
    }).catch(() => null);
    wx.reLaunch({ url: '/pages/home/index' });
  }
});
