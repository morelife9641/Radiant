const WORD_AUDIO_BASE_URL = 'https://ielts-word-audio-1411800061.cos.ap-guangzhou.myqcloud.com/audio';

let innerAudio = null;
let feedbackAudio = null;
let pendingDownload = null;
let pendingDownloadUrl = '';
let downloadSeq = 0;
const abortedSeqs = {};
let audioOptionReady = false;
let lastWordAudioKey = '';
let nextWordAccent = '';

function normalizeWordForAudio(word) {
  return String(word || '').trim();
}

function isRemoteUrl(url) {
  return /^https?:\/\//i.test(String(url || ''));
}

function isAbortError(err) {
  return String((err && err.errMsg) || '').toLowerCase().includes('abort');
}

function reportAudioError(title, detail) {
  console.warn(`[audio] ${title}`, detail);
  wx.showToast({ title, icon: 'none' });
}

function ensureAudioOption() {
  if (audioOptionReady || !wx.setInnerAudioOption) return;

  wx.setInnerAudioOption({
    obeyMuteSwitch: false,
    success() {
      audioOptionReady = true;
    },
    fail(err) {
      console.warn('[audio] setInnerAudioOption failed', err);
    }
  });
}

function abortPendingDownload() {
  if (!pendingDownload || !pendingDownload.abort) return;
  abortedSeqs[downloadSeq] = true;
  try { pendingDownload.abort(); } catch (e) {}
  pendingDownload = null;
  pendingDownloadUrl = '';
}

export function getWordAudioUrl(word, accent = '') {
  const normalized = normalizeWordForAudio(word);
  if (!normalized) return '';
  const suffix = accent === 'uk' ? '_uk' : '';
  return `${WORD_AUDIO_BASE_URL}/${encodeURIComponent(`${normalized}${suffix}`)}.mp3`;
}

function playLocalUrl(url) {
  if (!url) {
    wx.showToast({ title: '暂无音频', icon: 'none' });
    return;
  }

  ensureAudioOption();

  if (innerAudio) {
    try { innerAudio.stop(); innerAudio.destroy(); } catch (e) {}
  }

  innerAudio = wx.createInnerAudioContext();
  innerAudio.autoplay = false;
  innerAudio.obeyMuteSwitch = false;
  innerAudio.src = url;
  innerAudio.onError((err) => {
    reportAudioError('音频播放失败', {
      errMsg: err && err.errMsg,
      errCode: err && err.errCode,
      url
    });
  });
  innerAudio.play();
}

export function playFeedbackSound(type, options = {}) {
  const comboLevel = Math.max(1, Math.min(5, Number(options.combo || 1)));
  const srcMap = {
    correct: `/assets/sounds/answer-correct-${comboLevel}.wav`,
    wrong: '/assets/sounds/answer-wrong.wav'
  };
  const src = srcMap[type] || '/assets/sounds/answer-correct-1.wav';
  if (!src) return;

  ensureAudioOption();

  if (feedbackAudio) {
    try { feedbackAudio.stop(); feedbackAudio.destroy(); } catch (e) {}
  }

  feedbackAudio = wx.createInnerAudioContext();
  feedbackAudio.autoplay = false;
  feedbackAudio.obeyMuteSwitch = false;
  feedbackAudio.src = src;
  feedbackAudio.onError((err) => {
    console.warn('[audio] feedback sound failed', {
      type,
      src,
      errMsg: err && err.errMsg,
      errCode: err && err.errCode
    });
  });
  feedbackAudio.onEnded(() => {
    if (!feedbackAudio) return;
    try { feedbackAudio.destroy(); } catch (e) {}
    feedbackAudio = null;
  });
  feedbackAudio.play();
}

export function playUrl(url) {
  if (!url) {
    wx.showToast({ title: '暂无音频', icon: 'none' });
    return;
  }

  if (!isRemoteUrl(url)) {
    playLocalUrl(url);
    return;
  }

  if (pendingDownload && pendingDownload.abort) {
    if (pendingDownloadUrl === url) {
      return;
    }
    abortPendingDownload();
  }

  const seq = downloadSeq + 1;
  downloadSeq = seq;
  pendingDownloadUrl = url;
  pendingDownload = wx.downloadFile({
    url,
    success(res) {
      if (seq !== downloadSeq) return;

      if (res.statusCode === 200 && res.tempFilePath) {
        playLocalUrl(res.tempFilePath);
        return;
      }
      reportAudioError('音频不可访问', {
        statusCode: res.statusCode,
        url
      });
    },
    fail(err) {
      if (seq !== downloadSeq) return;
      if (isAbortError(err) && abortedSeqs[seq]) return;
      if (isAbortError(err)) {
        playLocalUrl(url);
        return;
      }

      reportAudioError('音频下载失败', {
        errMsg: err && err.errMsg,
        url
      });
    },
    complete() {
      if (seq === downloadSeq) {
        pendingDownload = null;
        pendingDownloadUrl = '';
      }
      delete abortedSeqs[seq];
    }
  });
}

export function playWord(word, options = {}) {
  const key = normalizeWordForAudio(word);
  if (!key) {
    wx.showToast({ title: '暂无音频', icon: 'none' });
    return;
  }

  let accent = options.accent || '';
  if (!options.accent) {
    if (lastWordAudioKey !== key) {
      accent = '';
      lastWordAudioKey = key;
      nextWordAccent = 'uk';
    } else {
      accent = nextWordAccent;
      nextWordAccent = accent === 'uk' ? '' : 'uk';
    }
  } else {
    lastWordAudioKey = key;
    nextWordAccent = options.accent === 'uk' ? '' : 'uk';
  }

  const url = getWordAudioUrl(key, accent);
  playUrl(url);
}

export function stopAudio() {
  if (innerAudio) {
    try {
      innerAudio.stop();
      innerAudio.destroy();
    } catch (e) {}
    innerAudio = null;
  }

  if (pendingDownload && pendingDownload.abort) {
    abortPendingDownload();
  }

  if (feedbackAudio) {
    try {
      feedbackAudio.stop();
      feedbackAudio.destroy();
    } catch (e) {}
    feedbackAudio = null;
  }
}
