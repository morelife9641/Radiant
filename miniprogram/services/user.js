import { callFn } from '../utils/request';

export const userService = {
  getProfile() {
    return callFn('user-sync', { action: 'get' });
  },
  updateProfile(payload = {}) {
    return callFn('user-sync', { action: 'update', ...payload });
  },
  sync(payload) {
    return callFn('user-sync', { action: 'sync', ...payload });
  },
  deleteAccountData() {
    return callFn('user-sync', { action: 'deleteAccountData' });
  }
};
