import { learnService } from '../../services/learn';
import { mergeProgressRecords } from '../../utils/progress-store';
import { getDateKeyAsiaShanghai } from '../../utils/date';
import { getUserDailyGoal } from '../../utils/profile-cache';

const DEFAULT_WORDBOOK_ID = 'ielts_content_words';
const RANGE_OPTIONS = [
  { label: '7天', value: 7 },
  { label: '30天', value: 30 }
];
const DAY_MS = 24 * 60 * 60 * 1000;
const SHANGHAI_OFFSET_MS = 8 * 60 * 60 * 1000;
const WEEK_TEXT = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'];

function getNavTopPx() {
  const app = getApp();
  const globalData = app && app.globalData ? app.globalData : {};
  return Math.ceil(globalData.navBarHeightPx || ((globalData.statusBarHeight || 44) + 48)) + 8;
}

function normalizeCount(value) {
  const count = Number(value);
  return Number.isFinite(count) ? Math.max(0, Math.round(count)) : 0;
}

function dateKeyToTime(dateKey) {
  const parts = String(dateKey || '').split('-').map(Number);
  if (parts.length !== 3 || parts.some(value => !Number.isFinite(value))) return 0;
  return Date.UTC(parts[0], parts[1] - 1, parts[2]) - SHANGHAI_OFFSET_MS;
}

function shiftDateKey(dateKey, offset) {
  return getDateKeyAsiaShanghai(dateKeyToTime(dateKey) + offset * DAY_MS);
}

function buildDateKeys(days, endDateKey = getDateKeyAsiaShanghai()) {
  const result = [];
  for (let offset = days - 1; offset >= 0; offset -= 1) {
    result.push(shiftDateKey(endDateKey, -offset));
  }
  return result;
}

function formatShortDate(dateKey) {
  const [, month, day] = String(dateKey || '').split('-');
  return `${Number(month)}/${Number(day)}`;
}

function formatDateInfo(dateKey) {
  const timestamp = dateKeyToTime(dateKey);
  const date = new Date(timestamp + SHANGHAI_OFFSET_MS);
  const today = getDateKeyAsiaShanghai();
  const yesterday = shiftDateKey(today, -1);
  const relative = dateKey === today ? '今天' : (dateKey === yesterday ? '昨天' : '');
  const month = date.getUTCMonth() + 1;
  const day = date.getUTCDate();
  const weekText = WEEK_TEXT[date.getUTCDay()];
  return {
    dateText: relative ? `${relative} · ${month}月${day}日` : `${month}月${day}日 · ${weekText}`,
    dayText: `${month}月${day}日`,
    weekText: relative || weekText
  };
}

function listStorageKeys() {
  try {
    return (wx.getStorageInfoSync && wx.getStorageInfoSync().keys) || [];
  } catch (err) {
    return [];
  }
}

function createDay(dateKey) {
  return {
    dateKey,
    newLearned: 0,
    reviewAnswers: 0,
    correctAnswers: 0,
    wrongAnswers: 0,
    difficultWords: 0,
    attempts: 0
  };
}

function ensureDay(dayMap, dateKey) {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(String(dateKey || ''))) return null;
  if (!dayMap[dateKey]) dayMap[dateKey] = createDay(dateKey);
  return dayMap[dateKey];
}

function uniqueProgressRecords(progress = {}) {
  const seen = new Set();
  return Object.keys(progress).map(key => progress[key]).filter((item) => {
    if (!item || item.status === 'ignored') return false;
    const identity = String(item.wordId || item.normalized || item.word || '').trim().toLowerCase();
    if (!identity || seen.has(identity)) return false;
    seen.add(identity);
    return true;
  });
}

function mergeProgressHistory(dayMap, records) {
  const learnedByDate = {};
  const wrongByDate = {};
  records.forEach((record) => {
    const identity = String(record.wordId || record.normalized || record.word || '').trim().toLowerCase();
    if (record.dailyDoneDateKey) {
      if (!learnedByDate[record.dailyDoneDateKey]) learnedByDate[record.dailyDoneDateKey] = new Set();
      learnedByDate[record.dailyDoneDateKey].add(identity);
    }
    if (record.dailyWrongDateKey) {
      if (!wrongByDate[record.dailyWrongDateKey]) wrongByDate[record.dailyWrongDateKey] = new Set();
      wrongByDate[record.dailyWrongDateKey].add(identity);
    }
  });
  Object.keys(learnedByDate).forEach((dateKey) => {
    const day = ensureDay(dayMap, dateKey);
    if (day) day.newLearned = Math.max(day.newLearned, learnedByDate[dateKey].size);
  });
  Object.keys(wrongByDate).forEach((dateKey) => {
    const day = ensureDay(dayMap, dateKey);
    if (day) day.difficultWords = Math.max(day.difficultWords, wrongByDate[dateKey].size);
  });
}

function mergeLocalHistory(dayMap, bookId) {
  const escapedBookId = bookId.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const donePattern = new RegExp(`^todayDone\\.${escapedBookId}\\.(\\d{4}-\\d{2}-\\d{2})$`);
  const sessionPattern = new RegExp(`^learnSession\\.${escapedBookId}\\.(daily|review)\\.(\\d{4}-\\d{2}-\\d{2})$`);

  listStorageKeys().forEach((key) => {
    const doneMatch = key.match(donePattern);
    if (doneMatch) {
      const values = wx.getStorageSync(key) || [];
      const count = new Set((Array.isArray(values) ? values : []).map(value => String(value || '').toLowerCase()).filter(Boolean)).size;
      const day = ensureDay(dayMap, doneMatch[1]);
      if (day) day.newLearned = Math.max(day.newLearned, count);
      return;
    }

    const sessionMatch = key.match(sessionPattern);
    if (!sessionMatch) return;
    const session = wx.getStorageSync(key) || {};
    const stats = session.stats || {};
    const known = normalizeCount(stats.known);
    const wrong = normalizeCount(stats.unknown);
    const attempts = known + wrong;
    const day = ensureDay(dayMap, sessionMatch[2]);
    if (!day) return;
    day.attempts = Math.max(day.attempts, attempts);
    day.correctAnswers = Math.max(day.correctAnswers, known);
    day.wrongAnswers = Math.max(day.wrongAnswers, wrong);
    if (sessionMatch[1] === 'review') day.reviewAnswers = Math.max(day.reviewAnswers, attempts);
  });

  ['daily', 'review'].forEach((mode) => {
    const value = wx.getStorageSync(`learnHistory.${bookId}.${mode}`) || {};
    const dateKey = value.savedAt ? getDateKeyAsiaShanghai(value.savedAt) : '';
    const stats = value.stats || {};
    const known = normalizeCount(stats.known);
    const wrong = normalizeCount(stats.unknown);
    const attempts = known + wrong;
    const day = ensureDay(dayMap, dateKey);
    if (!day || !attempts) return;
    day.attempts = Math.max(day.attempts, attempts);
    day.correctAnswers = Math.max(day.correctAnswers, known);
    day.wrongAnswers = Math.max(day.wrongAnswers, wrong);
    if (mode === 'review') day.reviewAnswers = Math.max(day.reviewAnswers, attempts);
  });
}

function mergeCloudHistory(dayMap, days = []) {
  days.forEach((item) => {
    const day = ensureDay(dayMap, item.dateKey);
    if (!day) return;
    day.newLearned = Math.max(day.newLearned, normalizeCount(item.newLearned));
    day.reviewAnswers = Math.max(day.reviewAnswers, normalizeCount(item.reviewAnswers));
    day.correctAnswers = Math.max(day.correctAnswers, normalizeCount(item.correctAnswers));
    day.wrongAnswers = Math.max(day.wrongAnswers, normalizeCount(item.wrongAnswers));
    day.difficultWords = Math.max(day.difficultWords, normalizeCount(item.difficultWords));
    day.attempts = Math.max(day.attempts, normalizeCount(item.attempts));
  });
}

function decorateDay(day) {
  const info = formatDateInfo(day.dateKey);
  const activityCount = Math.max(day.attempts, day.newLearned + day.reviewAnswers);
  const detailParts = [];
  if (day.newLearned) detailParts.push(`新学 ${day.newLearned}`);
  if (day.reviewAnswers) detailParts.push(`复习 ${day.reviewAnswers}`);
  if (day.wrongAnswers || day.difficultWords) detailParts.push(`需巩固 ${Math.max(day.wrongAnswers, day.difficultWords)}`);
  return {
    ...day,
    ...info,
    activityCount,
    detailText: detailParts.length ? detailParts.join(' · ') : '这天还没有学习记录',
    recordTitle: day.newLearned && day.reviewAnswers
      ? '新学与复习'
      : (day.reviewAnswers ? '复习巩固' : '新词学习'),
    recordDetail: detailParts.join(' · ') || '完成了一次学习'
  };
}

function calculateStreaks(activeDateKeys) {
  const sorted = Array.from(new Set(activeDateKeys)).sort();
  if (!sorted.length) return { current: 0, longest: 0 };
  let longest = 1;
  let running = 1;
  for (let index = 1; index < sorted.length; index += 1) {
    if (dateKeyToTime(sorted[index]) - dateKeyToTime(sorted[index - 1]) === DAY_MS) {
      running += 1;
      longest = Math.max(longest, running);
    } else {
      running = 1;
    }
  }

  const today = getDateKeyAsiaShanghai();
  const anchor = sorted.includes(today) ? today : shiftDateKey(today, -1);
  if (!sorted.includes(anchor)) return { current: 0, longest };
  const activeSet = new Set(sorted);
  let current = 0;
  let cursor = anchor;
  while (activeSet.has(cursor)) {
    current += 1;
    cursor = shiftDateKey(cursor, -1);
  }
  return { current, longest };
}

Page({
  data: {
    navTopPx: 96,
    loading: true,
    bookId: DEFAULT_WORDBOOK_ID,
    rangeDays: 7,
    rangeOptions: RANGE_OPTIONS,
    dailyGoal: 10,
    allDays: [],
    chartDays: [],
    historyRows: [],
    selectedIndex: 6,
    selectedDay: decorateDay(createDay(getDateKeyAsiaShanghai())),
    chartLabels: { start: '', middle: '', end: '' },
    summary: { currentStreak: 0, longestStreak: 0, activeDays: 0, periodLearned: 0, totalLearned: 0 },
    dataNote: ''
  },

  _chartRect: null,
  _loadToken: 0,

  onLoad(query = {}) {
    this.setData({
      navTopPx: getNavTopPx(),
      bookId: query.bookId || DEFAULT_WORDBOOK_ID
    });
    this.loadHistory();
  },

  onPullDownRefresh() {
    this.loadHistory({ force: true }).finally(() => wx.stopPullDownRefresh());
  },

  async loadHistory() {
    const token = ++this._loadToken;
    this.setData({ loading: true });
    const bookId = this.data.bookId || DEFAULT_WORDBOOK_ID;
    const localProgress = wx.getStorageSync(`progress.${bookId}`) || {};
    const [progressRes, historyRes, dailyGoal] = await Promise.all([
      learnService.listAllProgress(bookId).catch(() => null),
      learnService.learningHistory(bookId, { days: 90 }).catch(() => null),
      getUserDailyGoal().catch(() => 10)
    ]);
    if (token !== this._loadToken) return;

    const remoteProgress = progressRes && progressRes.ok && Array.isArray(progressRes.records)
      ? progressRes.records
      : [];
    const mergedProgress = mergeProgressRecords(localProgress, remoteProgress);
    if (remoteProgress.length) wx.setStorageSync(`progress.${bookId}`, mergedProgress);
    const progressRecords = uniqueProgressRecords(mergedProgress);
    const dayMap = {};
    mergeProgressHistory(dayMap, progressRecords);
    mergeLocalHistory(dayMap, bookId);
    if (historyRes && historyRes.ok) mergeCloudHistory(dayMap, historyRes.days || []);

    const allDateKeys = buildDateKeys(90);
    const allDays = allDateKeys.map(dateKey => decorateDay(dayMap[dateKey] || createDay(dateKey)));
    const activeDays = allDays.filter(day => day.activityCount > 0 || day.newLearned > 0);
    const streaks = calculateStreaks(activeDays.map(day => day.dateKey));
    const totalLearned = progressRecords.filter(item => (
      item.status === 'mastered' || normalizeCount(item.correctCount) > 0
    )).length;

    this.setData({
      loading: false,
      dailyGoal: normalizeCount(dailyGoal) || 10,
      allDays,
      historyRows: activeDays.slice().reverse().slice(0, 12),
      summary: {
        currentStreak: streaks.current,
        longestStreak: streaks.longest,
        activeDays: activeDays.length,
        periodLearned: 0,
        totalLearned
      },
      dataNote: historyRes && historyRes.ok
        ? '记录已与云端同步'
        : '较早的记录可能只包含新学数据'
    }, () => this.applyRange(this.data.rangeDays));
  },

  applyRange(days) {
    const chartDays = this.data.allDays.slice(-days);
    if (!chartDays.length) return;
    let selectedIndex = chartDays.length - 1;
    for (let index = chartDays.length - 1; index >= 0; index -= 1) {
      if (chartDays[index].activityCount || chartDays[index].newLearned) {
        selectedIndex = index;
        break;
      }
    }
    const middleIndex = Math.floor((chartDays.length - 1) / 2);
    const periodLearned = chartDays.reduce((sum, day) => sum + day.newLearned, 0);
    const activeDays = chartDays.filter(day => day.activityCount || day.newLearned).length;
    this.setData({
      rangeDays: days,
      chartDays,
      selectedIndex,
      selectedDay: chartDays[selectedIndex],
      chartLabels: {
        start: formatShortDate(chartDays[0].dateKey),
        middle: formatShortDate(chartDays[middleIndex].dateKey),
        end: formatShortDate(chartDays[chartDays.length - 1].dateKey)
      },
      summary: {
        ...this.data.summary,
        activeDays,
        periodLearned
      }
    }, () => this.drawChart());
  },

  onChangeRange(event) {
    const days = normalizeCount(event.currentTarget.dataset.days);
    if (!days || days === this.data.rangeDays) return;
    this.applyRange(days);
  },

  onChartTouch(event) {
    const touch = event.touches && event.touches[0];
    const rect = this._chartRect;
    const days = this.data.chartDays;
    if (!touch || !rect || days.length < 2) return;
    const paddingX = 20;
    const usableWidth = Math.max(1, rect.width - paddingX * 2);
    const localX = Math.max(0, Math.min(usableWidth, touch.clientX - rect.left - paddingX));
    const index = Math.max(0, Math.min(days.length - 1, Math.round((localX / usableWidth) * (days.length - 1))));
    if (index === this.data.selectedIndex) return;
    this.setData({ selectedIndex: index, selectedDay: days[index] }, () => this.drawChart());
  },

  drawChart() {
    const days = this.data.chartDays;
    if (!days.length) return;
    wx.createSelectorQuery()
      .select('#trendChart')
      .fields({ node: true, size: true, rect: true })
      .exec((result) => {
        const target = result && result[0];
        if (!target || !target.node || !target.width || !target.height) return;
        const canvas = target.node;
        const context = canvas.getContext('2d');
        const dpr = (wx.getWindowInfo && wx.getWindowInfo().pixelRatio) || 2;
        canvas.width = target.width * dpr;
        canvas.height = target.height * dpr;
        context.scale(dpr, dpr);
        context.clearRect(0, 0, target.width, target.height);
        this._chartRect = target;

        const padding = { left: 20, right: 20, top: 18, bottom: 20 };
        const chartWidth = target.width - padding.left - padding.right;
        const chartHeight = target.height - padding.top - padding.bottom;
        const values = days.map(day => day.newLearned);
        const maxValue = Math.max(this.data.dailyGoal || 0, ...values, 4);
        const points = values.map((value, index) => ({
          x: padding.left + (days.length === 1 ? chartWidth / 2 : (chartWidth * index) / (days.length - 1)),
          y: padding.top + chartHeight - (value / maxValue) * chartHeight
        }));

        context.lineWidth = 1;
        context.strokeStyle = 'rgba(78, 61, 54, 0.09)';
        [0, 0.5, 1].forEach((ratio) => {
          const y = padding.top + chartHeight * ratio;
          context.beginPath();
          context.moveTo(padding.left, y);
          context.lineTo(target.width - padding.right, y);
          context.stroke();
        });

        const goalY = padding.top + chartHeight - (Math.min(this.data.dailyGoal, maxValue) / maxValue) * chartHeight;
        context.save();
        context.setLineDash([4, 5]);
        context.strokeStyle = 'rgba(230, 91, 75, 0.2)';
        context.beginPath();
        context.moveTo(padding.left, goalY);
        context.lineTo(target.width - padding.right, goalY);
        context.stroke();
        context.restore();

        const fill = context.createLinearGradient(0, padding.top, 0, target.height - padding.bottom);
        fill.addColorStop(0, 'rgba(244, 103, 79, 0.28)');
        fill.addColorStop(1, 'rgba(244, 103, 79, 0.015)');
        context.beginPath();
        context.moveTo(points[0].x, target.height - padding.bottom);
        points.forEach(point => context.lineTo(point.x, point.y));
        context.lineTo(points[points.length - 1].x, target.height - padding.bottom);
        context.closePath();
        context.fillStyle = fill;
        context.fill();

        const line = context.createLinearGradient(padding.left, 0, target.width - padding.right, 0);
        line.addColorStop(0, '#F39A72');
        line.addColorStop(1, '#E74E46');
        context.beginPath();
        points.forEach((point, index) => {
          if (index === 0) context.moveTo(point.x, point.y);
          else context.lineTo(point.x, point.y);
        });
        context.strokeStyle = line;
        context.lineWidth = 2.5;
        context.lineJoin = 'round';
        context.lineCap = 'round';
        context.stroke();

        const selected = points[this.data.selectedIndex] || points[points.length - 1];
        context.beginPath();
        context.arc(selected.x, selected.y, 7, 0, Math.PI * 2);
        context.fillStyle = 'rgba(231, 78, 70, 0.14)';
        context.fill();
        context.beginPath();
        context.arc(selected.x, selected.y, 3.5, 0, Math.PI * 2);
        context.fillStyle = '#E74E46';
        context.fill();
        context.lineWidth = 2;
        context.strokeStyle = '#FFFFFF';
        context.stroke();
      });
  },

  onBack() {
    const pages = getCurrentPages ? getCurrentPages() : [];
    if (pages.length > 1) wx.navigateBack();
    else wx.reLaunch({ url: '/pages/home/index' });
  }
});
