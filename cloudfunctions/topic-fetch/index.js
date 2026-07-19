const cloud = require('wx-server-sdk');
cloud.init({ env: cloud.DYNAMIC_CURRENT_ENV });

const db = cloud.database();
const _ = db.command;

const DEFAULT_LIMIT = 5;
const MAX_LIMIT = 20;
const MAX_TOPIC_IDS = 5;
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

function normalizeTopicIds(topicIds) {
  if (Array.isArray(topicIds)) {
    return topicIds.map((item) => String(item || '').trim()).filter(Boolean).slice(0, MAX_TOPIC_IDS);
  }

  const topicId = String(topicIds || '').trim();
  return topicId ? [topicId] : [];
}

function uniq(values) {
  return Array.from(new Set(values.filter(Boolean)));
}

async function fetchByIds(collection, ids) {
  const cleanIds = uniq(ids);
  if (!cleanIds.length) return [];
  const rows = [];
  for (let index = 0; index < cleanIds.length; index += IN_QUERY_CHUNK_SIZE) {
    const chunk = cleanIds.slice(index, index + IN_QUERY_CHUNK_SIZE);
    const result = await db.collection(collection)
      .where({ _id: _.in(chunk) })
      .limit(chunk.length)
      .get();
    rows.push(...(result.data || []));
  }
  return rows;
}

function mapById(rows) {
  return rows.reduce((map, row) => {
    map[row._id] = row;
    return map;
  }, {});
}

function uniqueLinks(rows) {
  const seen = {};
  return rows.filter((row) => {
    const key = row._id || `${row.topicId}:${row.lineId}:${row.wordId}:${row.normalized}`;
    if (seen[key]) return false;
    seen[key] = true;
    return true;
  });
}

function mapTopic(topic) {
  if (!topic) return null;
  return {
    id: topic._id,
    name: topic.name || topic._id,
    type: topic.type || '',
    cover: topic.cover || {},
    source: topic.source || {}
  };
}

function mapExample(link, line, topic) {
  return {
    line,
    words: [link],
    matched: {
      wordId: link.wordId,
      normalized: link.normalized,
      surface: link.surface,
      positions: link.positions || [],
      matchType: link.matchType || 'exact'
    },
    topic: mapTopic(topic)
  };
}

function sortExamples(a, b) {
  const aAudio = a.line && a.line.audio && a.line.audio.url ? 1 : 0;
  const bAudio = b.line && b.line.audio && b.line.audio.url ? 1 : 0;
  if (aAudio !== bAudio) return bAudio - aAudio;

  const aTime = a.line && a.line.scene ? Number(a.line.scene.timestampMs || 0) : 0;
  const bTime = b.line && b.line.scene ? Number(b.line.scene.timestampMs || 0) : 0;
  if (aTime !== bTime) return aTime - bTime;

  return String(a.line && a.line._id || '').localeCompare(String(b.line && b.line._id || ''));
}

async function wordExamples(event) {
  const wordId = String(event.wordId || '').trim();
  const topicIds = normalizeTopicIds(event.topicIds);
  const limit = normalizeLimit(event.limit);

  if (!wordId) {
    return fail('WORD_ID_REQUIRED', 'Missing wordId.');
  }

  const linkRows = [];
  if (topicIds.length) {
    for (const topicId of topicIds) {
      const result = await db.collection('content_line_words')
        .where({ wordId, topicId })
        .limit(limit)
        .get();
      linkRows.push(...(result.data || []));
    }
  } else {
    const result = await db.collection('content_line_words')
      .where({ wordId })
      .limit(limit)
      .get();
    linkRows.push(...(result.data || []));
  }

  const links = uniqueLinks(linkRows);
  const lineIds = links.map((item) => item.lineId);
  const resolvedTopicIds = topicIds.length ? topicIds : links.map((item) => item.topicId);
  const lines = await fetchByIds('content_lines', lineIds);
  const topics = await fetchByIds('content_topics', resolvedTopicIds);
  const lineMap = mapById(lines);
  const topicMap = mapById(topics);

  const examples = links
    .map((link) => mapExample(link, lineMap[link.lineId], topicMap[link.topicId]))
    .filter((item) => item.line)
    .sort(sortExamples)
    .slice(0, limit);

  return ok({
    primary: examples,
    secondary: [],
    topics: topics.map(mapTopic).filter(Boolean)
  });
}

exports.main = async (event) => {
  const { action } = event;

  try {
    if (action === 'wordExamples') {
      return await wordExamples(event);
    }

    return fail('UNKNOWN_ACTION', `Unknown action: ${action || ''}`);
  } catch (err) {
    console.error('[topic-fetch]', err);
    return fail('INTERNAL_ERROR', err.message || 'Internal server error.');
  }
};
