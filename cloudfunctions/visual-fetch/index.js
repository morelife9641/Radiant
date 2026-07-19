const cloud = require('wx-server-sdk');
cloud.init({ env: cloud.DYNAMIC_CURRENT_ENV });

const db = cloud.database();
const PAGE_SIZE = 100;
const MAX_VISUALS = 1000;

function ok(data) {
  return { ok: true, ...data };
}

function fail(code, message) {
  return { ok: false, code, message };
}

function dateKeyShanghai(date = new Date()) {
  const parts = new Intl.DateTimeFormat('en-CA', {
    timeZone: 'Asia/Shanghai',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  }).formatToParts(date);
  const map = parts.reduce((acc, item) => {
    acc[item.type] = item.value;
    return acc;
  }, {});
  return `${map.year}-${map.month}-${map.day}`;
}

function pickByDate(items, dateKey) {
  if (!items.length) return null;
  let hash = 0;
  for (let i = 0; i < dateKey.length; i += 1) {
    hash = (hash * 31 + dateKey.charCodeAt(i)) >>> 0;
  }
  return items[hash % items.length];
}

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

function wordIdFor(value) {
  const slug = normalizeString(value)
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '_')
    .replace(/^_+|_+$/g, '')
    .replace(/_+/g, '_');
  return slug ? `word_${slug}` : '';
}

function normalizePhonetic(visual) {
  const phonetic = visual.phonetic || visual.pronunciation || visual.pron;
  if (typeof phonetic === 'object' && phonetic) {
    return firstString([phonetic.default, phonetic.us, phonetic.uk, phonetic.value, phonetic.text]);
  }
  return normalizeString(phonetic);
}

function normalizeTranslation(visual) {
  const senses = Array.isArray(visual.senses) ? visual.senses : [];
  const firstSense = senses[0] || {};
  return firstString([
    visual.translationZh,
    visual.translation,
    visual.shortZh,
    visual.meaningZh,
    visual.definitionZh,
    firstSense.translation,
    firstSense.translationZh,
    firstSense.definitionZh
  ]);
}

function normalizeImage(visual) {
  const image = visual.image || visual.cover || visual.background || visual.media || {};
  const firstImage = Array.isArray(visual.images) ? (visual.images[0] || {}) : {};
  const url = firstString([
    image.url,
    image.src,
    image.cosUrl,
    image.fileUrl,
    image.tempFileURL,
    firstImage.url,
    firstImage.src,
    visual.imageUrl,
    visual.imageURL,
    visual.coverUrl,
    visual.coverURL,
    visual.backgroundUrl,
    visual.url,
    visual.cosUrl
  ]);
  if (!url) return image;
  return {
    ...image,
    url,
    localPath: firstString([image.localPath, image.path, firstImage.localPath, visual.localPath]),
    width: Number(image.width || firstImage.width || visual.width || 0),
    height: Number(image.height || firstImage.height || visual.height || 0),
    format: firstString([image.format, firstImage.format, visual.format])
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

async function fetchVisuals(where, maxItems = MAX_VISUALS) {
  const items = [];
  for (let skip = 0; skip < maxItems; skip += PAGE_SIZE) {
    const result = await db.collection('word_visuals')
      .where(where)
      .skip(skip)
      .limit(PAGE_SIZE)
      .get();
    const page = result.data || [];
    items.push(...page);
    if (page.length < PAGE_SIZE) break;
  }
  return items.slice(0, maxItems);
}

async function dailyVisual(event) {
  const dateKey = event.dateKey || dateKeyShanghai();
  const maxItems = Math.min(Math.max(Number(event.maxItems || MAX_VISUALS), PAGE_SIZE), MAX_VISUALS);
  const publishedItems = await fetchVisuals({ status: 'published' }, maxItems);
  const items = publishedItems.length ? publishedItems : await fetchVisuals({}, maxItems);
  const pickKey = event.refreshSeed ? `${dateKey}:${event.refreshSeed}` : dateKey;
  const visual = normalizeVisual(pickByDate(items, pickKey));
  return ok({ dateKey, visual, total: items.length, refreshed: Boolean(event.refreshSeed) });
}

exports.main = async (event) => {
  const { action } = event;

  try {
    if (action === 'dailyVisual') {
      return await dailyVisual(event);
    }

    return fail('UNKNOWN_ACTION', `Unknown action: ${action || ''}`);
  } catch (err) {
    console.error('[visual-fetch]', err);
    return fail('INTERNAL_ERROR', err.message || 'Internal server error.');
  }
};
