const cloud = require('wx-server-sdk');
cloud.init({ env: cloud.DYNAMIC_CURRENT_ENV });

const db = cloud.database();

const DEFAULT_PROFILE = {
  nickname: '同学',
  onboarded: false,
  activeBookId: '',
  purpose: '',
  preferences: [],
  dailyGoal: 10,
  enableSpellingQuestions: false
};

const DAILY_GOAL_OPTIONS = [5, 10, 15, 20, 30, 50];
const DEFAULT_DAILY_GOAL = 10;

function ok(data) {
  return { ok: true, ...data };
}

function fail(code, message) {
  return { ok: false, code, message };
}

function normalizeDailyGoal(value) {
  const dailyGoal = Number(value);
  if (!Number.isFinite(dailyGoal)) return undefined;
  return DAILY_GOAL_OPTIONS.includes(dailyGoal) ? dailyGoal : DEFAULT_DAILY_GOAL;
}

function pickProfilePatch(payload = {}) {
  const patch = {};

  if (typeof payload.nickname === 'string') {
    patch.nickname = payload.nickname.trim().slice(0, 12) || '同学';
  }
  if (typeof payload.onboarded === 'boolean') patch.onboarded = payload.onboarded;
  if (typeof payload.activeBookId === 'string') patch.activeBookId = payload.activeBookId.trim().slice(0, 80);
  if (typeof payload.purpose === 'string') patch.purpose = payload.purpose.trim().slice(0, 40);
  if (Array.isArray(payload.preferences)) {
    patch.preferences = Array.from(new Set(
      payload.preferences
        .map(value => String(value || '').trim().slice(0, 40))
        .filter(Boolean)
    )).slice(0, 10);
  }

  const dailyGoal = normalizeDailyGoal(payload.dailyGoal);
  if (dailyGoal !== undefined) patch.dailyGoal = dailyGoal;
  if (typeof payload.enableSpellingQuestions === 'boolean') {
    patch.enableSpellingQuestions = payload.enableSpellingQuestions;
  }

  return patch;
}

async function ensureProfile(openid) {
  const ref = db.collection('users').doc(openid);

  try {
    const result = await ref.get();
    if (result.data) return result.data;
  } catch (err) {
    // missing document, create below
  }

  const now = db.serverDate();
  const profile = {
    openid,
    accountId: openid,
    ...DEFAULT_PROFILE,
    createdAt: now,
    updatedAt: now
  };

  await ref.set({ data: profile });
  return {
    _id: openid,
    ...profile
  };
}

async function updateProfile(openid, payload) {
  await ensureProfile(openid);

  const patch = pickProfilePatch(payload);
  if (Object.keys(patch).length === 0) {
    return ensureProfile(openid);
  }

  await db.collection('users').doc(openid).update({
    data: {
      ...patch,
      updatedAt: db.serverDate()
    }
  });

  return ensureProfile(openid);
}

async function removeUserRows(collectionName, openid) {
  while (true) {
    const result = await db.collection(collectionName)
      .where({ userId: openid })
      .limit(100)
      .get();
    const rows = result.data || [];
    if (!rows.length) return;
    await Promise.all(rows.map(row => db.collection(collectionName).doc(row._id).remove()));
  }
}

async function deleteAccountData(openid) {
  await removeUserRows('user_word_progress', openid);
  await removeUserRows('user_book_progress', openid);
  await removeUserRows('user_learn_sessions', openid);
  await removeUserRows('user_learning_activity', openid);
  await db.collection('users').doc(openid).remove();
}

exports.main = async (event, context) => {
  const { OPENID } = cloud.getWXContext();
  const action = event.action || 'get';

  try {
    if (!OPENID) return fail('AUTH_REQUIRED', '缺少用户身份，请从小程序端调用。');

    if (action === 'get') {
      const profile = await ensureProfile(OPENID);
      return ok({ openid: OPENID, profile });
    }

    if (action === 'update' || action === 'sync') {
      const profile = await updateProfile(OPENID, event);
      return ok({ openid: OPENID, profile });
    }

    if (action === 'deleteAccountData') {
      await deleteAccountData(OPENID);
      return ok({ deleted: true });
    }

    return fail('UNKNOWN_ACTION', `Unknown action: ${action}`);
  } catch (err) {
    console.error('[user-sync]', err);
    return fail('INTERNAL_ERROR', err.message || 'Internal server error.');
  }
};
