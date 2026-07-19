import { formatPos } from './pos';

const QUESTION_TYPES = {
  WORD_TO_ZH: 'word_to_zh',
  SENSE_TO_WORD: 'sense_to_word',
  DEFINITION_TO_WORD: 'definition_to_word',
  ZH_TO_WORD: 'zh_to_word',
  SPELLING: 'spelling'
};
const QUESTION_SCHEMA_VERSION = 2;

function getWordId(word) {
  return word && (word.wordId || word._id || '');
}

function getNormalized(word) {
  return String((word && (word.normalized || word.word)) || '').trim().toLowerCase();
}

function getPrimarySense(word) {
  return word && Array.isArray(word.senses) && word.senses[0] ? word.senses[0] : null;
}

function getCoreSense(word) {
  const source = word || {};
  const coreSense = source.coreSense && typeof source.coreSense === 'object'
    ? source.coreSense
    : {};
  return {
    en: String(coreSense.en || source.shortDefinitionEn || source.short_definition_en || '').trim(),
    zh: String(coreSense.zh || source.shortDefinitionZh || source.short_definition_zh || '').trim()
  };
}

function normalizeAsciiWidth(value) {
  return String(value || '')
    .replace(/[\uFF10-\uFF19\uFF21-\uFF3A\uFF41-\uFF5A\uFF0E]/g, char => String.fromCharCode(char.charCodeAt(0) - 0xFEE0))
    .replace(/\u3000/g, ' ');
}

function extractLeadingPos(text) {
  const match = normalizeAsciiWidth(text)
    .trim()
    .match(/^((?:adj|adv|noun|verb|prep|conj|pron|num|interj|article|vi|vt|n|v|a|ad))(?:\.|\s+)/i);
  return match ? match[1] : '';
}

function getPosLabel(word) {
  const sense = getPrimarySense(word);
  return formatPos((sense && sense.pos) || extractLeadingPos(sense && sense.translation));
}

export function getTranslation(word) {
  const sense = getPrimarySense(word);
  const translation = sense && sense.translation ? normalizeAsciiWidth(sense.translation).trim() : '';
  return translation
    .replace(/^((?:adj|adv|noun|verb|prep|conj|pron|num|interj|article|vi|vt|n|v|a|ad))(?:\.|\s+)\s*/i, '')
    .trim();
}

function getEnglishDefinition(word) {
  return getCoreSense(word).en
    .split(/\\n|\r?\n/)
    .map(item => item.trim())
    .find(Boolean) || '';
}

function getChineseDefinition(word) {
  return getCoreSense(word).zh
    .split(/\\n|\r?\n/)
    .map(item => item.trim())
    .find(Boolean) || '';
}

function getSenseId(word) {
  const sense = getPrimarySense(word);
  return sense && sense.senseId ? sense.senseId : '';
}

function getPhonetic(word) {
  return formatPhonetic(word && word.phonetic);
}

function formatPhonetic(value) {
  if (!value) return '';
  if (typeof value === 'string') {
    const text = value.trim();
    return text === '[object Object]' ? '' : text;
  }
  if (typeof value !== 'object') return String(value || '').trim();
  return [
    value.default,
    value.us,
    value.uk,
    value.en,
    value.text,
    value.value,
    value.phonetic
  ].map(formatPhonetic).find(Boolean) || '';
}

function shuffle(items) {
  const arr = items.slice();
  for (let i = arr.length - 1; i > 0; i -= 1) {
    const j = Math.floor(Math.random() * (i + 1));
    const tmp = arr[i];
    arr[i] = arr[j];
    arr[j] = tmp;
  }
  return arr;
}

function optionId(index) {
  return String.fromCharCode(97 + index);
}

function makeChoice(word, text, correct, index, options = {}) {
  return {
    id: optionId(index),
    text,
    wordText: word && word.word ? word.word : getNormalized(word),
    translationText: options.translationText === undefined
      ? getTranslation(word)
      : options.translationText,
    posLabel: options.showPosLabel === false ? '' : getPosLabel(word),
    value: getWordId(word),
    wordId: getWordId(word),
    senseId: getSenseId(word),
    correct
  };
}

function pickDistractors(word, distractorPool, mapper, limit = 3) {
  const currentWordId = getWordId(word);
  const used = new Set([mapper(word)]);
  const candidates = shuffle(
    (Array.isArray(distractorPool) ? distractorPool : [])
      .filter(item => item && getWordId(item) && getWordId(item) !== currentWordId)
      .map(item => ({ word: item, text: mapper(item) }))
      .filter(item => item.text)
  );

  const picked = [];
  for (const item of candidates) {
    if (used.has(item.text)) continue;
    used.add(item.text);
    picked.push(item);
    if (picked.length >= limit) break;
  }
  return picked;
}

function buildBaseQuestion(word, type, meta = {}) {
  const wordId = getWordId(word);
  return {
    id: `q_${wordId}_${type}_${Date.now()}_${Math.floor(Math.random() * 10000)}`,
    type,
    wordId,
    word: word.word || getNormalized(word),
    normalized: getNormalized(word),
    senseId: getSenseId(word),
    prompt: {},
    choices: [],
    answer: {},
    meta: {
      schemaVersion: QUESTION_SCHEMA_VERSION,
      ...meta
    }
  };
}

function buildWordToZhQuestion(word, distractorPool) {
  const correct = getTranslation(word);
  const q = buildBaseQuestion(word, QUESTION_TYPES.WORD_TO_ZH, {
    generator: 'rule',
    dataSource: 'word',
    difficulty: 1,
    reviewIntent: 'recognition'
  });

  q.prompt = {
    lang: 'en',
    word: word.word || '',
    phonetic: getPhonetic(word),
    showAudio: true
  };
  q.choices = shuffle([
    { word, text: correct, correct: true },
    ...pickDistractors(word, distractorPool, getTranslation)
  ]).map((item, index) => makeChoice(item.word, item.text, item.correct === true, index));
  q.answer = {
    type: 'choice',
    value: getWordId(word),
    wordId: getWordId(word),
    senseId: getSenseId(word),
    text: correct
  };
  return q;
}

function buildZhToWordQuestion(word, distractorPool) {
  const translation = getTranslation(word);
  const q = buildBaseQuestion(word, QUESTION_TYPES.ZH_TO_WORD, {
    generator: 'rule',
    dataSource: 'word',
    difficulty: 2,
    reviewIntent: 'recall'
  });

  q.prompt = {
    lang: 'zh',
    text: translation,
    posLabel: getPosLabel(word)
  };
  q.choices = shuffle([
    { word, text: word.word || '', correct: true },
    ...pickDistractors(word, distractorPool, item => item.word || '')
  ]).map((item, index) => makeChoice(item.word, item.text, item.correct === true, index, { showPosLabel: false }));
  q.answer = {
    type: 'choice',
    value: getWordId(word),
    wordId: getWordId(word),
    senseId: getSenseId(word),
    text: word.word || ''
  };
  return q;
}

function buildSenseToWordQuestion(word, distractorPool) {
  const definition = getChineseDefinition(word);
  if (!definition) return buildWordToZhQuestion(word, distractorPool);

  const q = buildBaseQuestion(word, QUESTION_TYPES.SENSE_TO_WORD, {
    generator: 'rule',
    dataSource: 'coreSense',
    difficulty: 2,
    reviewIntent: 'sense_recognition'
  });

  q.senseId = '';
  q.prompt = {
    lang: 'zh',
    text: definition,
    posLabel: '',
    hint: '根据词义选择对应单词'
  };
  q.choices = shuffle([
    { word, text: word.word || '', correct: true },
    ...pickDistractors(word, distractorPool, item => item.word || '')
  ]).map((item, index) => makeChoice(item.word, item.text, item.correct === true, index, {
    showPosLabel: false,
    translationText: getChineseDefinition(item.word) || getTranslation(item.word)
  }));
  q.answer = {
    type: 'choice',
    value: getWordId(word),
    wordId: getWordId(word),
    senseId: '',
    text: word.word || ''
  };
  return q;
}

function buildDefinitionToWordQuestion(word, distractorPool) {
  const definition = getEnglishDefinition(word);
  if (!definition) return buildSenseToWordQuestion(word, distractorPool);

  const q = buildBaseQuestion(word, QUESTION_TYPES.DEFINITION_TO_WORD, {
    generator: 'rule',
    dataSource: 'coreSense',
    difficulty: 2,
    reviewIntent: 'definition_recognition'
  });

  q.senseId = '';
  q.prompt = {
    lang: 'en',
    text: definition,
    zhText: getChineseDefinition(word),
    posLabel: ''
  };
  q.choices = shuffle([
    { word, text: word.word || '', correct: true },
    ...pickDistractors(word, distractorPool, item => item.word || '')
  ]).map((item, index) => makeChoice(item.word, item.text, item.correct === true, index, {
    showPosLabel: false,
    translationText: getChineseDefinition(item.word) || getTranslation(item.word)
  }));
  q.answer = {
    type: 'choice',
    value: getWordId(word),
    wordId: getWordId(word),
    senseId: '',
    text: word.word || ''
  };
  return q;
}

export function normalizeTextAnswer(value) {
  return String(value || '')
    .trim()
    .toLowerCase()
    .replace(/[.,!?;:'"()[\]{}，。！？；：“”‘’（）【】]+$/g, '')
    .replace(/^[.,!?;:'"()[\]{}，。！？；：“”‘’（）【】]+/g, '')
    .replace(/\s+/g, ' ');
}

function maskLetters(word) {
  const chars = String(word || '').split('');
  if (chars.length <= 2) return chars;

  return chars.map((char, index) => {
    if (!/[a-z]/i.test(char)) return char;
    if (index === 0 || index === chars.length - 1) return char;
    const shouldHide = /[aeiou]/i.test(char) || index % 3 === 0;
    return shouldHide ? null : char;
  });
}

function buildSpellingQuestion(word) {
  const answer = normalizeTextAnswer(word.word || '');
  const q = buildBaseQuestion(word, QUESTION_TYPES.SPELLING, {
    generator: 'rule',
    dataSource: 'word',
    difficulty: 3,
    reviewIntent: 'spelling'
  });

  q.prompt = {
    lang: 'zh',
    translation: getTranslation(word),
    phonetic: getPhonetic(word),
    letters: maskLetters(word.word || '')
  };
  q.choices = [];
  q.answer = {
    type: 'text',
    value: word.word || '',
    normalized: answer,
    acceptable: [answer]
  };
  return q;
}

function pickQuestionType(word, options = {}) {
  const progress = options.progress || {};
  const mode = options.mode || 'daily';
  const questionIndex = Math.max(0, Number(options.questionIndex || 0));
  const enableSpellingQuestions = options.enableSpellingQuestions === true;
  const correctCount = Number(progress.correctCount || 0);
  const wrongCount = Number(progress.wrongCount || 0);
  const status = progress.status || '';

  if (!word || !getTranslation(word)) return QUESTION_TYPES.WORD_TO_ZH;
  if (status === 'difficult' || wrongCount > correctCount) return QUESTION_TYPES.WORD_TO_ZH;
  if (mode === 'review') {
    if (correctCount >= 3 && enableSpellingQuestions) return QUESTION_TYPES.SPELLING;
    if (correctCount >= 2 && getEnglishDefinition(word)) return QUESTION_TYPES.DEFINITION_TO_WORD;
    if (correctCount <= 0) return QUESTION_TYPES.WORD_TO_ZH;
    if (getEnglishDefinition(word) && questionIndex % 3 === 2) {
      return QUESTION_TYPES.DEFINITION_TO_WORD;
    }
    if (getChineseDefinition(word)) {
      return questionIndex % 3 === 1
        ? QUESTION_TYPES.SENSE_TO_WORD
        : QUESTION_TYPES.WORD_TO_ZH;
    }
    return QUESTION_TYPES.WORD_TO_ZH;
  }
  if (correctCount <= 0) return QUESTION_TYPES.WORD_TO_ZH;
  if (correctCount === 1) {
    return getChineseDefinition(word) ? QUESTION_TYPES.SENSE_TO_WORD : QUESTION_TYPES.WORD_TO_ZH;
  }
  if (correctCount === 2 && getEnglishDefinition(word)) return QUESTION_TYPES.DEFINITION_TO_WORD;
  if (correctCount >= 2 && enableSpellingQuestions) return QUESTION_TYPES.SPELLING;
  if (correctCount >= 2 && getEnglishDefinition(word)) return QUESTION_TYPES.DEFINITION_TO_WORD;
  return QUESTION_TYPES.SENSE_TO_WORD;
}

export function buildQuestion(word, distractorPool = [], options = {}) {
  const requestedType = options.type || pickQuestionType(word, options);

  if (requestedType === QUESTION_TYPES.SPELLING) {
    return buildSpellingQuestion(word);
  }

  if (requestedType === QUESTION_TYPES.ZH_TO_WORD) {
    return buildZhToWordQuestion(word, distractorPool);
  }

  if (requestedType === QUESTION_TYPES.SENSE_TO_WORD) {
    return buildSenseToWordQuestion(word, distractorPool);
  }

  if (requestedType === QUESTION_TYPES.DEFINITION_TO_WORD) {
    return buildDefinitionToWordQuestion(word, distractorPool);
  }

  return buildWordToZhQuestion(word, distractorPool);
}

export { QUESTION_TYPES };
