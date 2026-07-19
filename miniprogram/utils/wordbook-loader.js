import { wordbookService } from '../services/wordbook';

// 正式环境以云数据库为唯一词书数据源，避免完整词书进入小程序主包。
let cloudBooksCache = null;
const cloudPageCache = {};
const cloudWordCache = {};

const FALLBACK_WORDBOOKS = {
  ielts_content_words: {
    _id: 'ielts_content_words',
    id: 'ielts_content_words',
    title: '雅思真题语境词汇',
    name: '雅思真题语境词汇',
    category: 'exam',
    language: 'en',
    level: 'B1-C1',
    cefrLevel: 'B1-C1',
    description: '词汇来自雅思阅读、听力、写作及口语语料，并提供真实出处和语境例句',
    cover: {
      letter: 'C',
      color: '#234E52',
      image: 'https://word-content-assets-1411800061.cos.ap-guangzhou.myqcloud.com/covers/wordbooks/ielts_content_words.png'
    },
    totalWords: 1352,
    status: 'published',
    version: 1
  }
};

function normalizePhonetic(phonetic) {
  if (!phonetic) return '';
  if (typeof phonetic === 'string') {
    const text = phonetic.trim();
    return text === '[object Object]' ? '' : text;
  }
  if (typeof phonetic !== 'object') return String(phonetic || '').trim();
  return [
    phonetic.default,
    phonetic.us,
    phonetic.uk,
    phonetic.en,
    phonetic.text,
    phonetic.value,
    phonetic.phonetic
  ].map(normalizePhonetic).find(Boolean) || '';
}

function normalizeSynonym(synonym = {}) {
  if (typeof synonym === 'string') {
    return {
      word: synonym,
      nuance_explanation: '',
      example_en: '',
      example_zh: ''
    };
  }

  return {
    ...synonym,
    nuance_explanation: synonym.nuance_explanation || synonym.nuance || '',
    example_en: synonym.example_en || synonym.exampleEn || '',
    example_zh: synonym.example_zh || synonym.exampleZh || ''
  };
}

function normalizeSense(sense = {}) {
  const definitionEn = sense.definitionEn || sense.definition_en || sense.definition || '';
  const definitionZh = sense.definitionZh || sense.definition_zh || '';
  const collinsEn = sense.collinsEn || (sense.collins_definition && sense.collins_definition.en) || '';
  const collinsZh = sense.collinsZh || (sense.collins_definition && sense.collins_definition.zh) || '';

  return {
    ...sense,
    senseId: sense.senseId || sense.sense_id || '',
    definitionEn,
    definitionZh,
    collinsEn,
    collinsZh,
    collins_definition: collinsEn || collinsZh ? { en: collinsEn, zh: collinsZh } : sense.collins_definition,
    synonyms: Array.isArray(sense.synonyms) ? sense.synonyms.map(normalizeSynonym) : [],
    antonyms: Array.isArray(sense.antonyms) ? sense.antonyms : [],
    gamingLink: sense.gamingLink || sense.gaming_link || null,
    gaming_link: sense.gamingLink || sense.gaming_link || null
  };
}

function normalizeWord(item = {}) {
  const source = item || {};
  const coreSense = source.coreSense && typeof source.coreSense === 'object'
    ? source.coreSense
    : {};
  const shortDefinitionEn = String(coreSense.en || source.shortDefinitionEn || source.short_definition_en || '').trim();
  const shortDefinitionZh = String(coreSense.zh || source.shortDefinitionZh || source.short_definition_zh || '').trim();

  return {
    ...source,
    id: source.wordId || source._id,
    _id: source.wordId || source._id,
    phonetic: normalizePhonetic(source.phonetic),
    coreSense: shortDefinitionEn || shortDefinitionZh
      ? { ...coreSense, en: shortDefinitionEn, zh: shortDefinitionZh }
      : null,
    shortDefinitionEn,
    shortDefinitionZh,
    senses: Array.isArray(source.senses) ? source.senses.map(normalizeSense) : []
  };
}

function normalizeBook(book = {}) {
  const title = book.title || book.name || '';
  const rawCover = book.cover || {};
  const cover = typeof rawCover === 'string' ? { color: rawCover } : rawCover;

  return {
    ...book,
    id: book._id || book.id,
    name: title,
    title,
    level: book.level || book.cefrLevel || '',
    letter: cover.letter || title.slice(0, 1) || '',
    cover,
    coverColor: cover.color || '#1A1A1A',
    coverImage: cover.image || ''
  };
}

export function getWordbook(id) {
  return null;
}

export function getMeta(id) {
  const b = getWordbook(id);
  if (b) return b.wordbook;
  return FALLBACK_WORDBOOKS[id] || null;
}

export function getWords(id) {
  const b = getWordbook(id);
  return b ? b.words : [];
}

export function getWordByOrder(id, order) {
  const words = getWords(id);
  return words.find(w => w.order === order) || null;
}

export function getWordByWord(id, word) {
  const words = getWords(id);
  return words.find(w => w.word === word) || null;
}

export function listAvailable() {
  return Object.keys(FALLBACK_WORDBOOKS);
}

export async function listCloudWordbooks(category, options = {}) {
  if (options.refresh) {
    cloudBooksCache = null;
  }

  if (!cloudBooksCache) {
    const res = await wordbookService.list();
    if (!res || !res.ok) throw new Error((res && res.message) || '词书列表加载失败');
    cloudBooksCache = (res.items || res.books || []).map(normalizeBook);
  }

  return category
    ? cloudBooksCache.filter(book => book.category === category)
    : cloudBooksCache;
}

export function clearWordbookCloudCache() {
  cloudBooksCache = null;
}

export async function listAvailableAsync(category) {
  const cloudBooks = await listCloudWordbooks(category).catch(() => []);
  const fallbackBooks = Object.values(FALLBACK_WORDBOOKS)
    .map(normalizeBook)
    .filter(book => !category || book.category === category);
  return Array.from(new Set(cloudBooks.concat(fallbackBooks).map(book => book.id).filter(Boolean)));
}

export async function getMetaAsync(id, options = {}) {
  const cloudBooks = await listCloudWordbooks(undefined, options).catch(() => []);
  const cloudBook = cloudBooks.find(book => book.id === id);
  if (cloudBook) return cloudBook;

  const localMeta = getMeta(id);
  return localMeta ? normalizeBook(localMeta) : null;
}

export async function getWordsPage(id, options = {}) {
  const limit = options.limit || 50;
  const cursor = options.cursor || '';
  const sort = options.sort || 'order';
  const cacheKey = `${id}:${limit}:${cursor}:${sort}`;

  if (cloudPageCache[cacheKey]) return cloudPageCache[cacheKey];

  const res = await wordbookService.detail(id, { limit, cursor, sort }).catch(() => null);
  if (!res || !res.ok) {
    const localWords = getWords(id).map(normalizeWord);
    const sortedLocalWords = sort === 'az'
      ? localWords.slice().sort((a, b) => String(a.word || '').toLowerCase().localeCompare(String(b.word || '').toLowerCase()))
      : localWords;
    const offset = Number(cursor || 0);
    if (!sortedLocalWords.length || !Number.isFinite(offset)) {
      throw new Error((res && res.message) || '词书单词加载失败');
    }

    const page = {
      book: normalizeBook(getMeta(id) || {}),
      total: sortedLocalWords.length,
      cursor: offset + limit < sortedLocalWords.length ? String(offset + limit) : '',
      items: sortedLocalWords.slice(offset, offset + limit)
    };
    cloudPageCache[cacheKey] = page;
    return page;
  }

  const page = {
    book: normalizeBook(res.book || {}),
    total: res.total || 0,
    cursor: res.cursor || '',
    items: (res.items || []).map(normalizeWord)
  };
  cloudPageCache[cacheKey] = page;
  return page;
}

export async function getWordsAsync(id, options = {}) {
  const words = [];
  let cursor = options.cursor || '';
  const limit = options.limit || 100;
  const maxPages = options.maxPages || 1;

  for (let pageIndex = 0; pageIndex < maxPages; pageIndex += 1) {
    const page = await getWordsPage(id, { limit, cursor });
    words.push(...page.items);
    cursor = page.cursor;
    if (!cursor) break;
  }

  if (words.length) return words;
  return getWords(id).map(normalizeWord);
}

export async function getWordByWordAsync(id, word) {
  const cacheKey = `${id}:${String(word || '').toLowerCase()}`;
  if (cloudWordCache[cacheKey]) return cloudWordCache[cacheKey];

  const res = await wordbookService.word(id, word).catch(() => null);
  if (res && res.ok && res.item) {
    const item = normalizeWord(res.item);
    cloudWordCache[cacheKey] = item;
    return item;
  }

  const localWord = getWordByWord(id, word);
  return localWord ? normalizeWord(localWord) : null;
}

export async function getWordsByWordsAsync(id, words) {
  const values = Array.from(new Set(
    (Array.isArray(words) ? words : [])
      .map(value => String(value || '').trim().toLowerCase())
      .filter(Boolean)
  ));
  if (!values.length) return [];

  const missing = values.filter(value => !cloudWordCache[`${id}:${value}`]);
  if (missing.length) {
    const res = await wordbookService.words(id, missing).catch(() => null);
    if (!res || !res.ok) throw new Error((res && res.message) || '批量加载单词失败');
    for (const rawItem of res.items || []) {
      const item = normalizeWord(rawItem);
      cloudWordCache[`${id}:${String(item.normalized || item.word || '').toLowerCase()}`] = item;
    }
  }

  return values
    .map(value => cloudWordCache[`${id}:${value}`])
    .filter(Boolean);
}

export async function searchWordsAsync(id, keyword, options = {}) {
  const q = String(keyword || '').trim().toLowerCase();
  if (!q) return [];

  const res = await wordbookService.search(id, q, options).catch(() => null);
  if (res && res.ok) {
    return (res.items || []).map(normalizeWord);
  }

  return getWords(id)
    .map(normalizeWord)
    .filter(item => String(item.normalized || item.word || '').toLowerCase().startsWith(q))
    .slice(0, options.limit || 20);
}
