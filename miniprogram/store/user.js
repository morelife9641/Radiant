import { observable, action } from 'mobx-miniprogram';

export const userStore = observable({
  profile: null,
  activeWordbookId: '',
  streakDays: 0,

  setProfile: action(function (profile) {
    this.profile = profile;
    this.activeWordbookId = profile?.activeWordbookId || '';
    this.streakDays = profile?.streakDays || 0;
  }),

  setActiveWordbook: action(function (id) {
    this.activeWordbookId = id;
  })
});
