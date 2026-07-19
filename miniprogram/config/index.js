export const APP_VERSION = '0.1.0';

export const CLOUD_ENV = 'cloud1-9gv9gsi8713fc91c';

export const FEATURE_FLAGS = {
  chatEnabled: false,
  voiceInput: false
};

export const LIMITS = {
  dailyChatTurns: 30,
  chatTokenPerTurn: 800
};

export const DAILY_GOAL_OPTIONS = [5, 10, 15, 20, 30, 50];
export const DEFAULT_DAILY_GOAL = 10;

export function normalizeDailyGoal(value) {
  const dailyGoal = Number(value);
  if (!Number.isFinite(dailyGoal)) return DEFAULT_DAILY_GOAL;
  return DAILY_GOAL_OPTIONS.includes(dailyGoal) ? dailyGoal : DEFAULT_DAILY_GOAL;
}
