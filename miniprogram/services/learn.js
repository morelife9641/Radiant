import { callFn } from '../utils/request';

export const learnService = {
  fetchToday(wordbookId) {
    return callFn('learn-submit', { action: 'today', wordbookId });
  },
  listProgress(wordbookId, { cursor = '', limit = 100 } = {}) {
    return callFn('learn-submit', { action: 'listProgress', wordbookId, cursor, limit });
  },
  async listAllProgress(wordbookId, { pageSize = 500, maxPages = 20 } = {}) {
    const records = [];
    let cursor = '';

    for (let page = 0; page < maxPages; page += 1) {
      const res = await this.listProgress(wordbookId, { cursor, limit: pageSize });
      if (!res || !res.ok) return res;
      records.push(...(res.records || []));
      cursor = res.cursor || '';
      if (!cursor) return { ok: true, records };
    }

    return { ok: false, code: 'PROGRESS_PAGE_LIMIT', message: '进度数据分页超过安全上限。', records };
  },
  learningHistory(wordbookId, { days = 30 } = {}) {
    return callFn('learn-submit', { action: 'learningHistory', wordbookId, days });
  },
  review({ limit = 50 } = {}) {
    return callFn('learn-submit', { action: 'review', limit });
  },
  listFavorites(wordbookId, { cursor = '', limit = 100 } = {}) {
    return callFn('learn-submit', { action: 'listFavorites', wordbookId, cursor, limit });
  },
  async listAllFavorites(wordbookId, { pageSize = 100, maxPages = 50 } = {}) {
    const items = [];
    let cursor = '';

    for (let page = 0; page < maxPages; page += 1) {
      const res = await this.listFavorites(wordbookId, { cursor, limit: pageSize });
      if (!res || !res.ok) return res;
      items.push(...(res.items || []));
      cursor = String(res.cursor || '');
      if (!cursor) return { ok: true, items };
    }

    return {
      ok: false,
      code: 'FAVORITES_PAGE_LIMIT',
      message: '收藏数量超过安全加载上限。',
      items
    };
  },
  submit(records) {
    return callFn('learn-submit', { action: 'submit', records });
  },
  submitOne(record) {
    return callFn('learn-submit', { action: 'submit', record });
  },
  getSession(wordbookId, mode, dateKey) {
    return callFn('learn-submit', { action: 'getSession', wordbookId, mode, dateKey });
  },
  saveSession(wordbookId, mode, dateKey, session, clientUpdatedAt) {
    return callFn('learn-submit', {
      action: 'saveSession',
      wordbookId,
      mode,
      dateKey,
      session,
      clientUpdatedAt
    });
  },
  clearSession(wordbookId, mode, dateKey, clientUpdatedAt, completedHistory = null) {
    return callFn('learn-submit', {
      action: 'clearSession',
      wordbookId,
      mode,
      dateKey,
      clientUpdatedAt,
      completedHistory
    });
  },
  updateWordState(record) {
    return callFn('learn-submit', { action: 'updateWordState', ...record });
  },
  resetTodayProgress(wordbookId = '') {
    return callFn('learn-submit', {
      action: 'resetTodayProgress',
      wordbookId,
      confirm: 'RESET_TODAY_LEARNING'
    });
  },
  resetProgress({ resetUserProfile = false } = {}) {
    return callFn('learn-submit', {
      action: 'resetProgress',
      confirm: 'RESET_USER_WORD_PROGRESS',
      resetUserProfile
    });
  }
};
