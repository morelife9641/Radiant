const cloud = require('wx-server-sdk');
cloud.init({ env: cloud.DYNAMIC_CURRENT_ENV });

const db = cloud.database();
const _ = db.command;

const DEFAULT_LIMIT = 50;
const MAX_LIMIT = 100;
const MAX_BATCH_WORDS = 50;
const IN_QUERY_CHUNK_SIZE = 10;

function ok(data) {
  return { ok: true, ...data };
}

function fail(code, message) {
  return { ok: false, code, message };
}

function normalizeLimit(limit) {
  const value = Number(limit || DEFAULT_LIMIT);
  if (!Number.isFinite(value) || value <= 0) return DEFAULT_LIMIT;
  return Math.min(Math.floor(value), MAX_LIMIT);
}

function encodeCursor(value) {
  if (!value) return '';
  return Buffer.from(JSON.stringify(value), 'utf8').toString('base64');
}

function decodeCursor(cursor) {
  if (!cursor) return null;

  try {
    return JSON.parse(Buffer.from(cursor, 'base64').toString('utf8'));
  } catch (err) {
    return null;
  }
}

async function fetchBook(bookId) {
  try {
    const result = await db.collection('wordbooks').doc(bookId).get();
    return result.data || null;
  } catch (err) {
    return null;
  }
}

async function countWordsForBook(bookId) {
  if (!bookId) return 0;
  try {
    const result = await db.collection('wordbook_words').where({ bookId }).count();
    return Number(result.total || 0);
  } catch (err) {
    console.warn('[wordbook-fetch] countWordsForBook failed', bookId, err);
    return 0;
  }
}

async function withResolvedTotalWords(book) {
  const totalWords = Number(book && book.totalWords);
  if (Number.isFinite(totalWords) && totalWords > 0) {
    return { ...book, totalWords };
  }

  const countedTotal = await countWordsForBook(book && book._id);
  return { ...book, totalWords: countedTotal };
}

function mapBook(book) {
  const title = book.title || book.name || '';

  return {
    _id: book._id,
    title,
    name: title,
    category: book.category,
    description: book.description || '',
    language: book.language || 'en',
    cover: book.cover || '',
    totalWords: book.totalWords || 0,
    status: book.status || 'published',
    version: book.version || 1,
    createdAt: book.createdAt || null,
    updatedAt: book.updatedAt || null
  };
}

async function listWordbooks(event) {
  const { category } = event;
  const where = { status: 'published' };

  if (category) {
    where.category = category;
  }

  const result = await db.collection('wordbooks').where(where).limit(100).get();
  const hydratedBooks = await Promise.all((result.data || []).map(withResolvedTotalWords));
  const items = hydratedBooks
    .map(mapBook)
    .sort((a, b) => {
      const byCreatedAt = Number(a.createdAt || 0) - Number(b.createdAt || 0);
      if (byCreatedAt !== 0) return byCreatedAt;
      return String(a._id).localeCompare(String(b._id));
    });

  return ok({ items, books: items });
}

function normalizeSort(sort) {
  return sort === 'az' ? 'az' : 'order';
}

function buildWordbookWordsQuery(bookId, cursorData, sort) {
  if (!cursorData) {
    return { bookId };
  }

  const lastWordId = String(cursorData.lastWordId || '');

  if (sort === 'az') {
    const lastNormalized = String(cursorData.lastNormalized || '');

    if (!lastNormalized || !lastWordId) {
      return null;
    }

    return _.or([
      { bookId, normalized: _.gt(lastNormalized) },
      { bookId, normalized: lastNormalized, wordId: _.gt(lastWordId) }
    ]);
  }

  const lastOrder = Number(cursorData.lastOrder);
  if (!Number.isFinite(lastOrder) || !lastWordId) {
    return null;
  }

  return _.or([
    { bookId, order: _.gt(lastOrder) },
    { bookId, order: lastOrder, wordId: _.gt(lastWordId) }
  ]);
}

function selectSenses(bookWord, word) {
  if (Array.isArray(bookWord.bookSenseOverride) && bookWord.bookSenseOverride.length > 0) {
    return bookWord.bookSenseOverride;
  }

  return Array.isArray(word.senses) ? word.senses : [];
}

function normalizeCoreSense(content = {}) {
  const source = content || {};
  const coreSense = source.coreSense && typeof source.coreSense === 'object'
    ? source.coreSense
    : {};
  const en = String(coreSense.en || source.shortDefinitionEn || source.short_definition_en || '').trim();
  const zh = String(coreSense.zh || source.shortDefinitionZh || source.short_definition_zh || '').trim();
  return en || zh ? { ...coreSense, en, zh } : null;
}

function joinWordbookItem(bookWord, wordMap, learningContentMap = {}) {
  const word = wordMap[bookWord.wordId] || {};
  const learningContent = learningContentMap[bookWord.wordId] || {};
  const coreSense = normalizeCoreSense(learningContent);
  const normalized = bookWord.normalized || word.normalized || '';

  return {
    wordId: bookWord.wordId,
    bookId: bookWord.bookId,
    word: bookWord.word || word.word || normalized,
    normalized,
    type: word.type || 'word',
    phonetic: word.phonetic || {},
    senses: selectSenses(bookWord, word),
    order: bookWord.order,
    chapter: bookWord.chapter || '',
    important: Boolean(bookWord.important),
    audio: word.audio || null,
    audioPolicy: word.audioPolicy || null,
    coreSense,
    shortDefinitionEn: coreSense ? coreSense.en : '',
    shortDefinitionZh: coreSense ? coreSense.zh : ''
  };
}

function wordIdFor(normalized) {
  const slug = String(normalized || '')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '_')
    .replace(/^_+|_+$/g, '')
    .replace(/_+/g, '_');

  return slug ? `word_${slug}` : '';
}

function chunk(values, size = IN_QUERY_CHUNK_SIZE) {
  const chunks = [];
  for (let index = 0; index < values.length; index += size) {
    chunks.push(values.slice(index, index + size));
  }
  return chunks;
}

async function fetchByIds(collection, ids) {
  const rows = [];
  for (const values of chunk(Array.from(new Set(ids.filter(Boolean))))) {
    const result = await db.collection(collection)
      .where({ _id: _.in(values) })
      .limit(values.length)
      .get();
    rows.push(...(result.data || []));
  }
  return rows;
}

async function fetchLearningContentMap(wordIds) {
  const groups = chunk(Array.from(new Set(wordIds.filter(Boolean))));
  const results = await Promise.all(groups.map(values => (
    db.collection('word_learning_content')
      .where({ wordId: _.in(values) })
      .field({
        _id: true,
        wordId: true,
        coreSense: true,
        shortDefinitionEn: true,
        shortDefinitionZh: true,
        short_definition_en: true,
        short_definition_zh: true
      })
      .limit(values.length)
      .get()
      .catch(() => ({ data: [] }))
  )));
  const rows = results.reduce((all, result) => all.concat(result.data || []), []);
  return rows.reduce((map, item) => {
    const wordId = item.wordId || item._id;
    if (wordId) map[wordId] = item;
    return map;
  }, {});
}

async function fetchWords(event) {
  const bookId = event.bookId || event.id;
  const normalizedValues = Array.from(new Set(
    (Array.isArray(event.words) ? event.words : [])
      .map(value => String(value || '').trim().toLowerCase())
      .filter(Boolean)
  )).slice(0, MAX_BATCH_WORDS);

  if (!bookId) return fail('BOOK_ID_REQUIRED', 'Missing bookId.');
  if (!normalizedValues.length) return ok({ items: [] });

  const bookRows = [];
  for (const values of chunk(normalizedValues)) {
    const result = await db.collection('wordbook_words')
      .where({ bookId, normalized: _.in(values) })
      .limit(values.length)
      .get();
    bookRows.push(...(result.data || []));
  }

  const wordIds = Array.from(new Set(bookRows.map(row => row.wordId).filter(Boolean)));
  const [words, learningContentMap] = await Promise.all([
    fetchByIds('words', wordIds),
    fetchLearningContentMap(wordIds)
  ]);

  const wordMap = words.reduce((map, word) => {
    map[word._id] = word;
    return map;
  }, {});
  const rowMap = bookRows.reduce((map, row) => {
    map[row.normalized] = row;
    return map;
  }, {});
  const items = normalizedValues
    .map(normalized => rowMap[normalized])
    .filter(Boolean)
    .map(row => joinWordbookItem(row, wordMap, learningContentMap));

  return ok({ items });
}

async function fetchWordbookDetail(event) {
  const bookId = event.bookId || event.id;
  const limit = normalizeLimit(event.limit);
  const cursorData = decodeCursor(event.cursor);
  const sort = normalizeSort(event.sort);

  if (!bookId) {
    return fail('BOOK_ID_REQUIRED', 'Missing bookId.');
  }

  if (event.cursor && !cursorData) {
    return fail('BAD_CURSOR', 'Invalid cursor.');
  }

  const rawBook = await fetchBook(bookId);
  const book = rawBook ? await withResolvedTotalWords(rawBook) : null;
  if (!book) {
    return fail('BOOK_NOT_FOUND', `Wordbook not found: ${bookId}`);
  }

  const where = buildWordbookWordsQuery(bookId, cursorData, sort);
  if (!where) {
    return fail('BAD_CURSOR', 'Invalid cursor.');
  }

  let query = db.collection('wordbook_words').where(where);
  if (sort === 'az') {
    query = query.orderBy('normalized', 'asc').orderBy('wordId', 'asc');
  } else {
    query = query.orderBy('order', 'asc').orderBy('wordId', 'asc');
  }

  const pageResult = await query.limit(limit + 1).get();

  const pageRows = pageResult.data || [];
  const rows = pageRows.slice(0, limit);
  const wordIds = rows.map((item) => item.wordId).filter(Boolean);

  let words = [];
  let learningContentMap = {};
  if (wordIds.length > 0) {
    [words, learningContentMap] = await Promise.all([
      fetchByIds('words', wordIds),
      fetchLearningContentMap(wordIds)
    ]);
  }

  const wordMap = words.reduce((map, word) => {
    map[word._id] = word;
    return map;
  }, {});

  const items = rows.map((row) => joinWordbookItem(row, wordMap, learningContentMap));
  const last = rows[rows.length - 1];
  let nextCursor = '';
  if (pageRows.length > limit && last) {
    nextCursor = sort === 'az'
      ? encodeCursor({ lastNormalized: last.normalized, lastWordId: last.wordId })
      : encodeCursor({ lastOrder: last.order, lastWordId: last.wordId });
  }

  return ok({
    book: mapBook(book),
    total: book.totalWords || 0,
    cursor: nextCursor,
    items
  });
}

async function fetchWord(event) {
  const bookId = event.bookId || event.id;
  const normalized = String(event.normalized || event.word || '').trim().toLowerCase();
  const wordId = event.wordId || wordIdFor(normalized);

  if (!bookId) {
    return fail('BOOK_ID_REQUIRED', 'Missing bookId.');
  }

  if (!wordId) {
    return fail('WORD_REQUIRED', 'Missing word.');
  }

  const bookWord = await db.collection('wordbook_words').doc(`${bookId}:${wordId}`).get()
    .then((res) => res.data || null)
    .catch(() => null);

  if (!bookWord) {
    return fail('WORD_NOT_FOUND', `Word not found: ${normalized || wordId}`);
  }

  const [word, learningContentMap] = await Promise.all([
    db.collection('words').doc(bookWord.wordId).get()
      .then((res) => res.data || null)
      .catch(() => null),
    fetchLearningContentMap([bookWord.wordId])
  ]);

  return ok({ item: joinWordbookItem(bookWord, word ? { [word._id]: word } : {}, learningContentMap) });
}

async function searchWords(event) {
  const bookId = event.bookId || event.id;
  const keyword = String(event.keyword || event.q || '').trim().toLowerCase();
  const limit = normalizeLimit(event.limit || 20);

  if (!bookId) {
    return fail('BOOK_ID_REQUIRED', 'Missing bookId.');
  }

  if (!keyword) {
    return ok({ items: [], total: 0, keyword: '' });
  }

  const result = await db.collection('wordbook_words')
    .where({
      bookId,
      normalized: _.gte(keyword).and(_.lt(`${keyword}\uffff`))
    })
    .orderBy('normalized', 'asc')
    .orderBy('wordId', 'asc')
    .limit(limit)
    .get();

  const rows = result.data || [];
  const wordIds = rows.map((item) => item.wordId).filter(Boolean);

  let words = [];
  let learningContentMap = {};
  if (wordIds.length > 0) {
    [words, learningContentMap] = await Promise.all([
      fetchByIds('words', wordIds),
      fetchLearningContentMap(wordIds)
    ]);
  }

  const wordMap = words.reduce((map, word) => {
    map[word._id] = word;
    return map;
  }, {});

  const items = rows.map((row) => joinWordbookItem(row, wordMap, learningContentMap));
  return ok({ items, total: items.length, keyword });
}

async function fetchWordRelations(event) {
  const wordId = String(event.wordId || '').trim();
  const limit = normalizeLimit(event.limit || 80);
  const includeDraft = Boolean(event.includeDraft);

  if (!wordId) {
    return fail('WORD_ID_REQUIRED', 'Missing wordId.');
  }

  const result = await db.collection('word_relations')
    .where({
      fromWordId: wordId,
      status: includeDraft ? _.in(['published', 'draft']) : 'published'
    })
    .limit(limit)
    .get();

  const relations = (result.data || [])
    .sort((a, b) => {
      const byStrength = Number(b.strength || 0) - Number(a.strength || 0);
      if (byStrength !== 0) return byStrength;
      return String(a.toWord || a.toWordId || '').localeCompare(String(b.toWord || b.toWordId || ''));
    });

  const groupIds = Array.from(new Set(relations.map((item) => item.groupId).filter(Boolean)));
  let groups = [];
  if (groupIds.length > 0) {
    groups = (await fetchByIds('word_relation_groups', groupIds))
      .filter(group => includeDraft ? ['published', 'draft'].includes(group.status) : group.status === 'published');
  }

  return ok({ relations, groups, total: relations.length });
}

async function fetchWordLearningContent(event) {
  const wordId = String(event.wordId || '').trim();
  const includeDraft = Boolean(event.includeDraft);
  const suggestionLimit = normalizeLimit(event.suggestionLimit || 20);

  if (!wordId) {
    return fail('WORD_ID_REQUIRED', 'Missing wordId.');
  }

  let learningContent = null;
  try {
    const contentResult = await db.collection('word_learning_content')
      .where({ wordId })
      .limit(1)
      .get();
    learningContent = (contentResult.data || [])[0] || null;
  } catch (err) {
    learningContent = null;
  }

  let suggestions = [];
  try {
    const suggestionResult = await db.collection('word_lexical_suggestions')
      .where({
        wordId,
        status: includeDraft ? _.in(['published', 'draft']) : 'published'
      })
      .limit(suggestionLimit)
      .get();

    suggestions = (suggestionResult.data || [])
      .sort((a, b) => {
        const byStrength = Number(b.strength || 0) - Number(a.strength || 0);
        if (byStrength !== 0) return byStrength;
        return String(a.targetWord || '').localeCompare(String(b.targetWord || ''));
      });
  } catch (err) {
    suggestions = [];
  }

  return ok({
    learningContent,
    suggestions,
    totalSuggestions: suggestions.length
  });
}

// action: 'list' | 'detail' | 'word' | 'words' | 'search' | 'relations' | 'learningContent'
exports.main = async (event, context) => {
  const { action } = event;

  try {
    if (action === 'list') {
      return await listWordbooks(event);
    }

    if (action === 'detail') {
      return await fetchWordbookDetail(event);
    }

    if (action === 'word') {
      return await fetchWord(event);
    }

    if (action === 'words') {
      return await fetchWords(event);
    }

    if (action === 'search') {
      return await searchWords(event);
    }

    if (action === 'relations') {
      return await fetchWordRelations(event);
    }

    if (action === 'learningContent') {
      return await fetchWordLearningContent(event);
    }

    return fail('UNKNOWN_ACTION', `Unknown action: ${action || ''}`);
  } catch (err) {
    console.error('[wordbook-fetch]', err);
    return fail('INTERNAL_ERROR', err.message || 'Internal server error.');
  }
};
