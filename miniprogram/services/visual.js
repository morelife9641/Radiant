import { callFn } from '../utils/request';
import { getDateKeyAsiaShanghai } from '../utils/date';

const CACHE_KEY = (dateKey) => `dailyVisual.${dateKey}`;
const LATEST_CACHE_KEY = 'dailyVisual.latest';
const DEV_CACHE_BUST_KEY = 'dailyVisual.devCacheBust';
const DATED_CACHE_RE = /^dailyVisual\.\d{4}-\d{2}-\d{2}$/;

function normalizeString(value) {
  return String(value || '').trim();
}

function firstString(values) {
  for (const value of values) {
    const text = normalizeString(value);
    if (text) return text;
  }
  return '';
}

function isDevRuntime() {
  try {
    const account = wx.getAccountInfoSync && wx.getAccountInfoSync();
    const envVersion = account && account.miniProgram && account.miniProgram.envVersion;
    if (envVersion) return envVersion !== 'release';
  } catch (e) {
    // Ignore and try the devtools fallback below.
  }

  try {
    return typeof __wxConfig !== 'undefined' && __wxConfig.platform === 'devtools';
  } catch (e) {
    return false;
  }
}

function getDevCacheBust() {
  if (!isDevRuntime()) return '';
  return normalizeString(wx.getStorageSync(DEV_CACHE_BUST_KEY));
}

function appendQuery(url, key, value) {
  if (!url || !key || !value || !/^https?:\/\//i.test(url)) return url;
  const hashIndex = url.indexOf('#');
  const base = hashIndex >= 0 ? url.slice(0, hashIndex) : url;
  const hash = hashIndex >= 0 ? url.slice(hashIndex) : '';
  const joiner = base.includes('?') ? '&' : '?';
  return `${base}${joiner}${encodeURIComponent(key)}=${encodeURIComponent(value)}${hash}`;
}

function wordIdFor(value) {
  const slug = normalizeString(value)
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '_')
    .replace(/^_+|_+$/g, '')
    .replace(/_+/g, '_');
  return slug ? `word_${slug}` : '';
}

function normalizePhonetic(visual) {
  const phonetic = visual && (visual.phonetic || visual.pronunciation || visual.pron);
  if (phonetic && typeof phonetic === 'object') {
    return firstString([phonetic.default, phonetic.us, phonetic.uk, phonetic.value, phonetic.text]);
  }
  return normalizeString(phonetic);
}

function normalizeTranslation(visual) {
  const senses = visual && Array.isArray(visual.senses) ? visual.senses : [];
  const firstSense = senses[0] || {};
  return firstString([
    visual && visual.translationZh,
    visual && visual.translation,
    visual && visual.shortZh,
    visual && visual.meaningZh,
    visual && visual.definitionZh,
    firstSense.translation,
    firstSense.translationZh,
    firstSense.definitionZh
  ]);
}

function normalizeImage(visual) {
  const image = (visual && (visual.image || visual.cover || visual.background || visual.media)) || {};
  const firstImage = visual && Array.isArray(visual.images) ? (visual.images[0] || {}) : {};
  const url = firstString([
    image.url,
    image.src,
    image.cosUrl,
    image.fileUrl,
    image.tempFileURL,
    firstImage.url,
    firstImage.src,
    visual && visual.imageUrl,
    visual && visual.imageURL,
    visual && visual.coverUrl,
    visual && visual.coverURL,
    visual && visual.backgroundUrl,
    visual && visual.url,
    visual && visual.cosUrl
  ]);
  if (!url) return image;
  const cacheBust = getDevCacheBust();
  return {
    ...image,
    url: appendQuery(url, 'visualBust', cacheBust),
    localPath: firstString([image.localPath, image.path, firstImage.localPath, visual && visual.localPath]),
    width: Number(image.width || firstImage.width || (visual && visual.width) || 0),
    height: Number(image.height || firstImage.height || (visual && visual.height) || 0),
    format: firstString([image.format, firstImage.format, visual && visual.format])
  };
}

function normalizeVisual(visual) {
  if (!visual) return null;
  const word = firstString([visual.word, visual.title, visual.normalized, visual.text, visual.name]);
  const normalized = firstString([visual.normalized, word]).toLowerCase();
  const wordId = firstString([
    visual.wordId,
    visual.word_id,
    visual.id && String(visual.id).startsWith('word_') ? visual.id : '',
    visual._id && String(visual._id).startsWith('word_') ? visual._id : '',
    wordIdFor(normalized || word)
  ]);
  const wordIds = Array.from(new Set([
    wordId,
    visual.wordId,
    visual.word_id
  ].concat(visual.wordIds || [], visual.word_ids || []).map(normalizeString).filter(Boolean)));

  return {
    ...visual,
    wordId,
    wordIds,
    word: word || normalized,
    normalized,
    title: visual.title || word || normalized,
    phonetic: normalizePhonetic(visual),
    translationZh: normalizeTranslation(visual),
    image: normalizeImage(visual)
  };
}

function normalizeResponse(res) {
  if (!res || !res.ok) return res;
  return {
    ...res,
    visual: normalizeVisual(res.visual)
  };
}

function readDatedCache(dateKey) {
  const cached = wx.getStorageSync(CACHE_KEY(dateKey));
  return cached && cached.ok ? normalizeResponse(cached) : null;
}

function readLatestCache() {
  const cached = wx.getStorageSync(LATEST_CACHE_KEY);
  return cached && cached.ok ? normalizeResponse(cached) : null;
}

export const visualService = {
  isDevelopmentRefreshEnabled() {
    return isDevRuntime();
  },
  refreshDevelopmentCache() {
    if (!isDevRuntime()) return false;
    try {
      const keys = (wx.getStorageInfoSync && wx.getStorageInfoSync().keys) || [];
      keys
        .filter(key => DATED_CACHE_RE.test(key))
        .forEach(key => wx.removeStorageSync(key));
      wx.setStorageSync(DEV_CACHE_BUST_KEY, String(Date.now()));
    } catch (e) {
      wx.setStorageSync(DEV_CACHE_BUST_KEY, String(Date.now()));
    }
    return true;
  },
  getCachedDailyVisual(dateKey = getDateKeyAsiaShanghai()) {
    return readDatedCache(dateKey) || readLatestCache();
  },
  dailyVisual(options = {}) {
    const dateKey = options.dateKey || getDateKeyAsiaShanghai();
    const cached = !options.refresh && readDatedCache(dateKey);
    if (cached) return Promise.resolve(cached);
    const refreshSeed = isDevRuntime() ? getDevCacheBust() : '';

    return callFn('visual-fetch', {
      action: 'dailyVisual',
      ...options,
      refreshSeed,
      dateKey
    }).then((rawRes) => {
      const res = normalizeResponse(rawRes);
      if (res && res.ok) {
        wx.setStorageSync(CACHE_KEY(dateKey), res);
        wx.setStorageSync(LATEST_CACHE_KEY, res);
      }
      return res;
    });
  }
};
