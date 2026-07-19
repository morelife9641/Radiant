import { normalizeDailyGoal } from '../config/index';
import { userService } from '../services/user';

const PROFILE_SYNC_KEY = 'settings.profileSyncedAt';
const PROFILE_PENDING_KEY = 'settings.profilePending';
const PROFILE_SYNC_TTL = 5 * 60 * 1000;
const SPELLING_QUESTIONS_KEY = 'settings.enableSpellingQuestions';

function hasCachedDailyGoal() {
  const value = wx.getStorageSync('settings.dailyGoal');
  return value !== undefined && value !== null && value !== '';
}

export function hydrateProfileCache(profile) {
  if (!profile) return null;

  const pending = wx.getStorageSync(PROFILE_PENDING_KEY) || null;
  if (pending && pending.dailyGoal) {
    wx.setStorageSync('settings.dailyGoal', normalizeDailyGoal(pending.dailyGoal));
  } else if (profile.dailyGoal) {
    wx.setStorageSync('settings.dailyGoal', normalizeDailyGoal(profile.dailyGoal));
  }

  if (pending && pending.nickname) {
    wx.setStorageSync('settings.nickname', pending.nickname);
  } else if (profile.nickname) {
    wx.setStorageSync('settings.nickname', profile.nickname);
  }

  if (pending && typeof pending.enableSpellingQuestions === 'boolean') {
    wx.setStorageSync(SPELLING_QUESTIONS_KEY, pending.enableSpellingQuestions);
  } else {
    wx.setStorageSync(SPELLING_QUESTIONS_KEY, profile.enableSpellingQuestions === true);
  }
  wx.setStorageSync(PROFILE_SYNC_KEY, Date.now());
  return profile;
}

export function markProfilePending(patch = {}) {
  const current = wx.getStorageSync(PROFILE_PENDING_KEY) || {};
  const pending = {
    ...current,
    ...patch,
    updatedAt: Date.now()
  };
  wx.setStorageSync(PROFILE_PENDING_KEY, pending);
  return pending;
}

export function clearProfilePending(fields = []) {
  const pending = wx.getStorageSync(PROFILE_PENDING_KEY) || null;
  if (!pending) return;

  if (!fields.length) {
    wx.removeStorageSync(PROFILE_PENDING_KEY);
    return;
  }

  const next = { ...pending };
  fields.forEach((field) => delete next[field]);
  delete next.updatedAt;
  if (Object.keys(next).length) {
    next.updatedAt = Date.now();
    wx.setStorageSync(PROFILE_PENDING_KEY, next);
  } else {
    wx.removeStorageSync(PROFILE_PENDING_KEY);
  }
}

async function flushPendingProfile() {
  const pending = wx.getStorageSync(PROFILE_PENDING_KEY) || null;
  if (!pending) return null;

  const payload = {};
  if (pending.nickname) payload.nickname = pending.nickname;
  if (pending.dailyGoal) payload.dailyGoal = normalizeDailyGoal(pending.dailyGoal);
  if (typeof pending.enableSpellingQuestions === 'boolean') {
    payload.enableSpellingQuestions = pending.enableSpellingQuestions;
  }
  if (!Object.keys(payload).length) {
    wx.removeStorageSync(PROFILE_PENDING_KEY);
    return null;
  }

  const res = await userService.updateProfile(payload).catch((err) => {
    console.warn('[profile-cache] flush pending failed', err);
    return null;
  });
  const profile = res && res.profile ? res.profile : null;
  const synced = Boolean(
    res
    && res.ok
    && profile
    && (!Object.prototype.hasOwnProperty.call(payload, 'nickname') || profile.nickname === payload.nickname)
    && (!Object.prototype.hasOwnProperty.call(payload, 'dailyGoal') || normalizeDailyGoal(profile.dailyGoal) === payload.dailyGoal)
    && (!Object.prototype.hasOwnProperty.call(payload, 'enableSpellingQuestions')
      || profile.enableSpellingQuestions === payload.enableSpellingQuestions)
  );
  if (synced) {
    wx.removeStorageSync(PROFILE_PENDING_KEY);
    return hydrateProfileCache(profile);
  }
  if (res) {
    console.warn('[profile-cache] flush pending rejected or profile mismatch', res.code, res.message);
  }
  return null;
}

export async function refreshProfileCache(options = {}) {
  const force = Boolean(options.force);
  const lastSyncedAt = Number(wx.getStorageSync(PROFILE_SYNC_KEY) || 0);
  const freshEnough = Date.now() - lastSyncedAt < PROFILE_SYNC_TTL;
  const pending = wx.getStorageSync(PROFILE_PENDING_KEY) || null;

  if (pending) {
    const flushed = await flushPendingProfile();
    if (!flushed) {
      return {
        nickname: wx.getStorageSync('settings.nickname') || '同学',
        dailyGoal: normalizeDailyGoal(wx.getStorageSync('settings.dailyGoal')),
        enableSpellingQuestions: wx.getStorageSync(SPELLING_QUESTIONS_KEY) === true
      };
    }
  }

  if (!force && hasCachedDailyGoal() && freshEnough) {
    return {
      nickname: wx.getStorageSync('settings.nickname') || '同学',
      dailyGoal: normalizeDailyGoal(wx.getStorageSync('settings.dailyGoal')),
      enableSpellingQuestions: wx.getStorageSync(SPELLING_QUESTIONS_KEY) === true
    };
  }

  const res = await userService.getProfile().catch((err) => {
    console.warn('[profile-cache] refresh failed', err);
    return null;
  });
  if (res && !res.ok) {
    console.warn('[profile-cache] refresh rejected', res.code, res.message);
  }
  const profile = res && res.ok ? res.profile : null;
  return hydrateProfileCache(profile);
}

export async function getUserDailyGoal(options = {}) {
  await refreshProfileCache(options);
  return normalizeDailyGoal(wx.getStorageSync('settings.dailyGoal'));
}

export async function getUserProfileFromCache(options = {}) {
  await refreshProfileCache(options);
  return {
    nickname: wx.getStorageSync('settings.nickname') || '同学',
    dailyGoal: normalizeDailyGoal(wx.getStorageSync('settings.dailyGoal')),
    enableSpellingQuestions: wx.getStorageSync(SPELLING_QUESTIONS_KEY) === true
  };
}

export async function getUserLearningPreferences(options = {}) {
  const profile = await getUserProfileFromCache(options);
  return {
    dailyGoal: normalizeDailyGoal(profile.dailyGoal),
    enableSpellingQuestions: profile.enableSpellingQuestions === true
  };
}
