const https = require('https');
const cloud = require('wx-server-sdk');

cloud.init({ env: cloud.DYNAMIC_CURRENT_ENV });

const DEEPSEEK_BASE_URL = 'https://api.deepseek.com';
const DEFAULT_MODEL = 'deepseek-v4-flash';
const MAX_SENSES = 5;

function ok(data) {
  return { ok: true, ...data };
}

function fail(code, message) {
  return { ok: false, code, message };
}

function cleanText(value, limit = 320) {
  return String(value || '').replace(/\s+/g, ' ').trim().slice(0, limit);
}

function requestJson(url, payload, headers = {}) {
  return new Promise((resolve, reject) => {
    const request = https.request(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(JSON.stringify(payload)),
        ...headers
      },
      timeout: 25000
    }, (response) => {
      const chunks = [];
      response.on('data', chunk => chunks.push(chunk));
      response.on('end', () => {
        const body = Buffer.concat(chunks).toString('utf8');
        let data = null;

        try {
          data = body ? JSON.parse(body) : null;
        } catch (err) {
          return reject(new Error('INVALID_PROVIDER_RESPONSE'));
        }

        if (response.statusCode < 200 || response.statusCode >= 300) {
          const message = cleanText(data && data.error && data.error.message, 180) || 'AI 服务暂时不可用';
          const error = new Error(message);
          error.code = response.statusCode;
          return reject(error);
        }

        resolve(data);
      });
    });

    request.on('timeout', () => request.destroy(new Error('AI_REQUEST_TIMEOUT')));
    request.on('error', reject);
    request.write(JSON.stringify(payload));
    request.end();
  });
}

function parseJsonObject(value) {
  const content = String(value || '').trim()
    .replace(/^```json\s*/i, '')
    .replace(/^```\s*/i, '')
    .replace(/\s*```$/, '');
  const start = content.indexOf('{');
  const end = content.lastIndexOf('}');

  if (start < 0 || end <= start) return null;

  try {
    return JSON.parse(content.slice(start, end + 1));
  } catch (err) {
    return null;
  }
}

function normalizeGuide(value = {}) {
  const source = value.guide || value.memoryGuide || value.memory || value.data || value;
  const input = (Array.isArray(source.input) ? source.input : [])
    .map(item => ({
      titleZh: cleanText(item && (item.titleZh || item.title || item.sceneZh), 24),
      contentZh: cleanText(item && (item.contentZh || item.content || item.tipZh), 160)
    }))
    .filter(item => item.titleZh && item.contentZh)
    .slice(0, 3);
  const output = (Array.isArray(source.output) ? source.output : [])
    .map(item => ({
      titleZh: cleanText(item && (item.titleZh || item.title || item.sceneZh), 24),
      contentZh: cleanText(item && (item.contentZh || item.content || item.tipZh), 200),
      exampleEn: cleanText(item && (item.exampleEn || item.example || item.sentenceEn), 180),
      exampleZh: cleanText(item && (item.exampleZh || item.sentenceZh || item.translationZh), 180)
    }))
    .filter(item => item.titleZh && item.contentZh)
    .slice(0, 3);

  return { input, output };
}

function hasGuideContent(guide) {
  return Boolean(
    guide
    && guide.input.length >= 2
    && guide.output.length >= 2
    && guide.output.every(item => item.exampleEn && item.exampleZh)
  );
}

function buildWordPayload(word = {}) {
  const wordText = cleanText(word.word, 64);
  const senses = (Array.isArray(word.senses) ? word.senses : [])
    .slice(0, MAX_SENSES)
    .map(sense => ({
      pos: cleanText(sense.pos, 16),
      translation: cleanText(sense.translation, 160),
      definitionEn: cleanText(sense.definitionEn, 240),
      definitionZh: cleanText(sense.definitionZh, 220)
    }))
    .filter(sense => sense.translation || sense.definitionEn || sense.definitionZh);

  return { word: wordText, senses };
}

const GUIDE_SYSTEM_PROMPT = '你是一名面向 IELTS/CET 学习者的英语词汇教练。必须只返回一个 JSON 对象，且必须使用以下结构：{"input":[{"titleZh":"阅读或听力或同义改写","contentZh":"非空：一条具体、可操作的识别或排除干扰策略"}],"output":[{"titleZh":"写作或口语或表达","contentZh":"非空：一条具体、自然的使用建议","exampleEn":"非空：使用目标词或其自然变形的一句英文例句","exampleZh":"非空：对应中文"}]}。input 和 output 必须各返回 2 到 3 条：输入侧尽量覆盖阅读、听力、同义改写/干扰；输出侧尽量覆盖写作、口语、表达选择。每条都必须紧扣目标词给出的具体词义和词性：输入侧说明可观察的语义信号、常见短搭配或同义改写，帮助定位该词义；输出侧说明适合放进哪类论点、经历或回答。每个 output 的 exampleEn 必须是 8 到 18 个词的自然短句，exampleZh 必须准确翻译该句。使用简体中文，每条只写一个清晰要点。绝不能粘贴、翻译或改写英文词典定义，绝不能用英文长句作为识别技巧；不要编造出处、考试频率或词源；不要返回 Markdown、解释文字或额外字段。';

const GUIDE_RETRY_PROMPT = '只返回合法 JSON，不要 Markdown。必须恰好给出 input 两条和 output 两条。结构为：{"input":[{"titleZh":"阅读","contentZh":"具体识别策略"},{"titleZh":"听力","contentZh":"具体识别策略"}],"output":[{"titleZh":"写作","contentZh":"具体使用建议","exampleEn":"8到18词且含目标词或自然变形的例句","exampleZh":"例句中文"},{"titleZh":"口语","contentZh":"具体使用建议","exampleEn":"8到18词且含目标词或自然变形的例句","exampleZh":"例句中文"}]}。不要输出词典定义，不要英文长释义。';

async function requestGuide(word, apiKey, systemPrompt) {
  const providerResponse = await requestJson(`${DEEPSEEK_BASE_URL}/chat/completions`, {
    model: cleanText(process.env.DEEPSEEK_MODEL, 80) || DEFAULT_MODEL,
    temperature: 0.15,
    max_tokens: 700,
    response_format: { type: 'json_object' },
    messages: [
      { role: 'system', content: systemPrompt },
      { role: 'user', content: JSON.stringify(word) }
    ]
  }, {
    Authorization: `Bearer ${apiKey}`
  });

  const content = providerResponse
    && providerResponse.choices
    && providerResponse.choices[0]
    && providerResponse.choices[0].message
    && providerResponse.choices[0].message.content;

  return {
    content,
    guide: normalizeGuide(parseJsonObject(content) || {})
  };
}

async function generateWordMemoryGuide(event) {
  const apiKey = cleanText(process.env.DEEPSEEK_API_KEY, 256);
  if (!apiKey) {
    return fail('AI_NOT_CONFIGURED', 'AI 扩展服务暂未配置');
  }

  const word = buildWordPayload(event.word);
  if (!word.word || !word.senses.length) {
    return fail('INVALID_WORD', '缺少可用于生成记忆提示的词义');
  }

  const firstAttempt = await requestGuide(word, apiKey, GUIDE_SYSTEM_PROMPT);
  if (hasGuideContent(firstAttempt.guide)) {
    return ok({ guide: firstAttempt.guide });
  }

  console.warn('[ai-chat] invalid first guide', cleanText(firstAttempt.content, 1200));
  const retryAttempt = await requestGuide(word, apiKey, GUIDE_RETRY_PROMPT);
  if (hasGuideContent(retryAttempt.guide)) {
    return ok({ guide: retryAttempt.guide, retried: true });
  }

  console.warn('[ai-chat] invalid retry guide', cleanText(retryAttempt.content, 1200));
  return fail('AI_EMPTY_RESPONSE', 'AI 未返回完整的考试建议，请稍后重试');
}

exports.main = async (event = {}) => {
  try {
    if (event.action === 'wordMemoryGuide') {
      return await generateWordMemoryGuide(event);
    }

    return fail('UNKNOWN_ACTION', '不支持的 AI 请求');
  } catch (err) {
    console.error('[ai-chat]', err);
    return fail('AI_REQUEST_FAILED', 'AI 扩展暂时不可用');
  }
};
