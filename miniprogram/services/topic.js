import { callFn } from '../utils/request';

const CACHE_VERSION = 'v2';
const CACHE_TTL = 7 * 24 * 60 * 60 * 1000;
const memoryCache = {};

function cacheKey(wordId, options = {}) {
  const topicIds = Array.isArray(options.topicIds) ? options.topicIds.join(',') : String(options.topicIds || '');
  const limit = options.limit || '';
  return `topic.examples.${CACHE_VERSION}.${wordId}.${topicIds}.${limit}`;
}

function readCache(key) {
  let stored = null;
  try {
    stored = wx.getStorageSync(key);
  } catch (err) {
    stored = null;
  }
  const cached = memoryCache[key] || stored;
  if (!cached || Date.now() - Number(cached.cachedAt || 0) > CACHE_TTL) return null;
  memoryCache[key] = cached;
  return cached.data;
}

function writeCache(key, data) {
  const cached = { cachedAt: Date.now(), data };
  memoryCache[key] = cached;
  try {
    wx.setStorageSync(key, cached);
  } catch (err) {
    // Memory cache is enough for the current session.
  }
}

export const topicService = {
  async wordExamples(wordId, options = {}) {
    const key = cacheKey(wordId, options);
    const cached = readCache(key);
    if (cached) return cached;

    const res = await callFn('topic-fetch', {
      action: 'wordExamples',
      wordId,
      ...options
    });
    if (res && res.ok) writeCache(key, res);
    return res;
  }
};
