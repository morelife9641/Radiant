const app = getApp();

Page({
  data: {
    statusBarHeight: 44,
    role: { name: 'Sarah', scene: 'Dota 队友 · 英文开黑' },
    messages: [
      { id: '1', role: 'assistant', content: 'Hey, ready to push mid? Let me know if you need a smoke.', suggestion: '' }
    ],
    draft: '',
    anchor: ''
  },

  onLoad() {
    const g = (app && app.globalData) || {};
    this.setData({ statusBarHeight: g.statusBarHeight || 44 });
  },

  onShow() {
    if (typeof this.getTabBar === 'function' && this.getTabBar()) {
      this.getTabBar().setData({ selected: 1 });
    }
  },

  onInput(e) {
    this.setData({ draft: e.detail.value });
  },

  onSend() {
    const text = this.data.draft.trim();
    if (!text) return;
    const id = String(Date.now());
    const messages = this.data.messages.concat([{ id, role: 'user', content: text }]);
    this.setData({ messages, draft: '', anchor: `m-${id}` });

    // TODO: aiService.chat -> 追加 assistant 消息
    setTimeout(() => {
      const aid = String(Date.now() + 1);
      const next = this.data.messages.concat([{
        id: aid,
        role: 'assistant',
        content: 'Sounds good. I’ll buy a smoke and rotate.',
        suggestion: 'Cool, I’ll grab a smoke and rotate to mid.'
      }]);
      this.setData({ messages: next, anchor: `m-${aid}` });
    }, 600);
  },

  onApplySuggestion(e) {
    this.setData({ draft: e.detail.text });
  },

  onChangeRole() {
    wx.showActionSheet({
      itemList: ['切换角色', '清空对话'],
      success: (res) => {
        if (res.tapIndex === 1) {
          this.setData({ messages: [] });
        }
      }
    });
  }
});
