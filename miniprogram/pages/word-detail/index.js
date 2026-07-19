import { getWordByWordAsync, searchWordsAsync } from '../../utils/wordbook-loader';
import { topicService } from '../../services/topic';
import { wordbookService } from '../../services/wordbook';
import { playUrl, playWord, stopAudio } from '../../utils/audio';
import { learnService } from '../../services/learn';
import { formatPos } from '../../utils/pos';

const DEFAULT_TOPIC_IDS = ['tbbt', 'ted_bv1m5lz6ceyq'];
const PROGRESS_KEY = (bookId) => `progress.${bookId}`;
const DEFAULT_TABS = [
  { key: 'basic', label: '基础' },
  { key: 'corpus', label: '语料' },
  { key: 'synonyms', label: '近义词' },
  { key: 'antonyms', label: '反义词' },
  { key: 'confusing', label: '辨析' }
];
const CONTENT_WORD_TABS = [
  { key: 'basic', label: '基础' },
  { key: 'corpus', label: '原文' },
  { key: 'learning', label: '学习' },
  { key: 'confusing', label: '辨析' },
  { key: 'suggestions', label: '候选' }
];
const DEFAULT_WORDBOOK_ID = 'ielts_content_words';

function getNavTopPx() {
  const app = getApp();
  const g = app && app.globalData ? app.globalData : {};
  return Math.ceil(g.navBarHeightPx || ((g.statusBarHeight || 44) + 48)) + 8;
}

Page({
  data: {
    word: null,
    headingTranslations: [],
    activeTab: 'basic',
    tabs: DEFAULT_TABS,
    hasSynonyms: false,
    hasAntonyms: false,
    antonyms: [],
    confusingItems: [],
    relationsRequested: false,
    relationsLoading: false,
    relationSynonyms: [],
    relationAntonyms: [],
    relationConfusing: [],
    relationRecords: [],
    relationSenseOptions: [],
    currentSenseId: '',
    relationGroups: [],
    relationsError: '',
    learningRequested: false,
    learningLoading: false,
    learningError: '',
    learningContent: null,
    shortDefinitionRevealed: false,
    lexicalSuggestions: [],
    examplesRequested: false,
    examplesAvailable: true,
    examplesError: '',
    examplesTitle: '语料例句',
    examples: [],
    featuredExample: null,
    examplesLoading: false,
    fromLearn: false,
    bookId: '',
    isFavorite: false,
    isIgnored: false,
    expandedCollocationIndex: -1,
    tokenPopover: {
      visible: false,
      loading: false,
      x: 0,
      y: 0,
      arrowX: 0,
      word: '',
      phonetic: '',
      translation: '',
      found: false
    },
    expandedKey: '',   // 'senseIdx-synIdx'
    navTopPx: 96,
    orbLevel: '0',
    recovery: null
  },

  _tokenLookupVersion: 0,
  _autoPlayTimer: null,

  async onLoad(query) {
    this.setData({ navTopPx: getNavTopPx() });
    const bookId = query.bookId || 'cet4';
    const wordStr = decodeURIComponent(query.word || '');
    const fromLearn = query.fromLearn === '1';
    const orbLevel = ['0', '20', '40', '60', '80', '100'].includes(String(query.orbLevel || ''))
      ? String(query.orbLevel)
      : '0';
    const recoveryStep = Number(query.recoveryStep || 0);
    const recoveryTotal = Number(query.recoveryTotal || 3);
    const recoveryPassed = Number(query.recoveryPassed || 0);
    const recovery = recoveryStep
      ? {
        step: recoveryStep,
        total: recoveryTotal || 3,
        passed: Math.max(0, Math.min(recoveryPassed, recoveryTotal || 3))
      }
      : null;
    const w = await getWordByWordAsync(bookId, wordStr).catch(() => null);
    if (!w) {
      wx.showToast({ title: '未找到单词', icon: 'none' });
      setTimeout(() => wx.navigateBack(), 1200);
      return;
    }
    const displayWord = decorateWordExamples(w);
    const relationSenseOptions = buildRelationSenseOptions(displayWord);
    const progress = loadProgress(bookId);
    const currentProgress = getWordProgress(progress, displayWord);
    wx.setNavigationBarTitle({ title: w.word });
    this.setData({
      word: displayWord,
      headingTranslations: buildHeadingTranslations(displayWord),
      bookId,
      tabs: getTabs(bookId),
      activeTab: 'basic',
      expandedKey: '',
      examples: [],
      featuredExample: null,
      examplesRequested: false,
      examplesAvailable: true,
      examplesTitle: getExamplesTitle(bookId),
      relationsRequested: false,
      relationsLoading: false,
      relationSynonyms: [],
      relationAntonyms: [],
      relationConfusing: [],
      relationRecords: [],
      relationSenseOptions,
      currentSenseId: relationSenseOptions.length ? relationSenseOptions[0].senseId : '',
      relationGroups: [],
      relationsError: '',
      learningRequested: false,
      learningLoading: false,
      learningError: '',
      learningContent: null,
      shortDefinitionRevealed: false,
      lexicalSuggestions: [],
      expandedCollocationIndex: -1,
      examplesError: '',
      fromLearn,
      orbLevel,
      recovery,
      isFavorite: Boolean(currentProgress.favorite),
      isIgnored: currentProgress.status === 'ignored',
      ...buildTabMeta(displayWord)
    });

    if (isContentWordbook(bookId)) {
      this.loadExamples(displayWord.wordId || displayWord._id);
      this.loadLearningContent(displayWord.wordId || displayWord._id);
    }

    clearTimeout(this._autoPlayTimer);
    this._autoPlayTimer = setTimeout(() => {
      playWord(w.word);
    }, 320);
  },

  async loadExamples(wordId) {
    if (!wordId) return;

    this.setData({ examplesLoading: true, examplesRequested: true, examplesAvailable: true, examplesError: '' });

    const bookId = this.data.bookId || '';
    const options = {
      limit: 20
    };
    if (!isContentWordbook(bookId)) {
      options.topicIds = DEFAULT_TOPIC_IDS;
    }

    const res = await withTimeout(topicService.wordExamples(wordId, {
      ...options
    }), 8000).catch(() => null);

    const examples = res && res.ok && Array.isArray(res.primary)
      ? res.primary.map(item => formatExample(item, this.data.word))
      : [];

    this.setData({
      examples,
      featuredExample: examples[0] || null,
      examplesLoading: false,
      examplesError: res && res.ok ? '' : '语料暂时加载失败'
    });
  },

  onSwitchTab(e) {
    const tab = e.currentTarget.dataset.tab || 'basic';
    this.setData({ activeTab: tab, 'tokenPopover.visible': false });

    if (tab === 'corpus' && !this.data.examplesRequested && this.data.word) {
      this.loadExamples(this.data.word.wordId || this.data.word._id);
    }

    if (isRelationTab(tab) && !this.data.relationsRequested && this.data.word) {
      this.loadRelations(this.data.word.wordId || this.data.word._id);
    }

    if ((tab === 'learning' || tab === 'suggestions') && !this.data.learningRequested && this.data.word) {
      this.loadLearningContent(this.data.word.wordId || this.data.word._id);
    }
  },

  onOpenCorpus() {
    this.setData({ activeTab: 'corpus', 'tokenPopover.visible': false });
    if (!this.data.examplesRequested && this.data.word) {
      this.loadExamples(this.data.word.wordId || this.data.word._id);
    }
  },

  onToggleCollocation(e) {
    const index = Number(e.currentTarget.dataset.index);
    this.setData({
      expandedCollocationIndex: this.data.expandedCollocationIndex === index ? -1 : index
    });
  },

  async loadRelations(wordId) {
    if (!wordId) return;

    this.setData({ relationsLoading: true, relationsRequested: true, relationsError: '' });

    const res = await withTimeout(wordbookService.relations(wordId, {
      limit: 80,
      includeDraft: isContentWordbook(this.data.bookId)
    }), 8000).catch(() => null);
    if (!res || !res.ok) {
      this.setData({ relationsLoading: false, relationsError: '词义关系暂时加载失败' });
      return;
    }

    const relationMeta = buildRelationMeta(
      res.relations || [],
      res.groups || [],
      this.data.bookId,
      this.data.currentSenseId
    );
    this.setData({
      ...relationMeta,
      relationsLoading: false,
      relationsError: ''
    });
  },

  async loadLearningContent(wordId) {
    if (!wordId) return;

    this.setData({ learningLoading: true, learningRequested: true, learningError: '' });

    const res = await withTimeout(wordbookService.learningContent(wordId, {
      includeDraft: isContentWordbook(this.data.bookId),
      suggestionLimit: 40
    }), 8000).catch(() => null);

    if (!res || !res.ok) {
      this.setData({ learningLoading: false, learningError: '扩展内容暂时加载失败' });
      return;
    }

    this.setData({
      learningContent: normalizeLearningContent(res.learningContent),
      lexicalSuggestions: Array.isArray(res.suggestions) ? res.suggestions.map(normalizeSuggestion) : [],
      learningLoading: false,
      learningError: ''
    });
  },

  onToggleShortDefinition() {
    const content = this.data.learningContent || {};
    if (!content.shortDefinitionZh) return;
    this.setData({
      shortDefinitionRevealed: !this.data.shortDefinitionRevealed
    });
  },

  onSelectRelationSense(e) {
    const senseId = String(e.currentTarget.dataset.sense || '').trim();
    if (!senseId || senseId === this.data.currentSenseId) return;

    this.setData({
      currentSenseId: senseId,
      ...buildRelationLists(this.data.relationRecords || [], this.data.bookId, senseId)
    });
  },

  onToggleSyn(e) {
    const { sense, syn } = e.currentTarget.dataset;
    const key = `${sense}-${syn}`;
    this.setData({ expandedKey: this.data.expandedKey === key ? '' : key });
  },

  onOpenRelationWord(e) {
    if (String(e.currentTarget.dataset.open || '1') === '0') return;
    const word = e.currentTarget.dataset.word;
    if (!word) return;
    const bookId = (this.data.word && this.data.word.bookId) || DEFAULT_WORDBOOK_ID;
    wx.navigateTo({
      url: `/pages/word-detail/index?bookId=${bookId}&word=${encodeURIComponent(word)}`
    });
  },

  onPlay() {
    const w = this.data.word;
    if (!w) return;
    playWord(w.word);
  },

  onPlayExample(e) {
    const { url } = e.currentTarget.dataset;
    playUrl(url);
  },

  async onSearchToken(e) {
    const word = e.currentTarget.dataset.word;
    if (!word) return;
    const bookId = (this.data.word && this.data.word.bookId) || DEFAULT_WORDBOOK_ID;
    const position = getPopoverPosition(e);
    const version = this._tokenLookupVersion + 1;
    this._tokenLookupVersion = version;

    this.setData({
      tokenPopover: {
        visible: true,
        loading: true,
        x: position.x,
        y: position.y,
        arrowX: position.arrowX,
        word,
        phonetic: '',
        translation: '',
        found: false
      }
    });

    const result = await lookupTokenWord(bookId, word);
    if (version !== this._tokenLookupVersion) return;
    const primarySense = result && result.senses && result.senses[0] ? result.senses[0] : null;

    this.setData({
      tokenPopover: {
        visible: true,
        loading: false,
        x: position.x,
        y: position.y,
        arrowX: position.arrowX,
        word: result && result.word ? result.word : word,
        phonetic: result ? result.phonetic : '',
        translation: primarySense ? primarySense.translation : '当前词书未收录',
        found: Boolean(result)
      }
    });
  },

  onCloseTokenPopover() {
    this.setData({ 'tokenPopover.visible': false });
  },

  onOpenPopoverWord() {
    const popover = this.data.tokenPopover || {};
    if (!popover.found || !popover.word) return;
    const bookId = (this.data.word && this.data.word.bookId) || DEFAULT_WORDBOOK_ID;
    this.setData({ 'tokenPopover.visible': false });
    wx.navigateTo({
      url: `/pages/word-detail/index?bookId=${bookId}&word=${encodeURIComponent(popover.word)}`
    });
  },

  onBack() {
    const pages = getCurrentPages();
    if (pages.length > 1) {
      wx.navigateBack({ delta: 1 });
    } else {
      wx.reLaunch({ url: '/pages/home/index' });
    }
  },

  async onToggleFavorite() {
    const word = this.data.word;
    if (!word) return;
    const progress = loadProgress(this.data.bookId);
    const key = getWordKey(word);
    if (!key) return;

    const now = Date.now();
    const prev = progress[key] || {};
    const favorite = !this.data.isFavorite;
    progress[key] = {
      ...prev,
      wordId: getWordId(word) || prev.wordId,
      normalized: key,
      word: word.word || prev.word || key,
      favorite,
      favoritedAt: favorite ? now : null,
      clientUpdatedAt: now,
      updatedAt: now
    };
    saveProgress(this.data.bookId, progress);
    syncPreviousLearnState(word, { favorite });
    this.setData({ isFavorite: favorite });
    wx.showToast({ title: favorite ? '已收藏' : '已取消收藏', icon: 'none' });
    const res = await syncWordStateToCloud(this.data.bookId, word, progress[key]);
    if (!res || !res.ok) {
      console.warn('[word-detail] favorite sync failed', res);
      wx.showToast({ title: '收藏已本地保存，同步稍后重试', icon: 'none' });
    }
  },

  onIgnoreWord() {
    const word = this.data.word;
    if (!word) return;

    wx.showModal({
      title: '从学习中删除？',
      content: `删除后不会再主动安排「${word.word}」进入学习队列，可在详情页恢复。`,
      confirmText: '删除',
      confirmColor: '#DC2626',
      success: (res) => {
        if (!res.confirm) return;
        const nextProgress = setIgnoredProgress(this.data.bookId, word);
        syncWordStateToCloud(this.data.bookId, word, nextProgress);
        syncPreviousLearnState(word, { ignored: true });
        this.setData({ isIgnored: true });

        if (this.data.fromLearn) {
          const pages = getCurrentPages();
          const prevPage = pages[pages.length - 2];
          if (prevPage && typeof prevPage.removeCurrentWordFromQueue === 'function') {
            prevPage.removeCurrentWordFromQueue();
          }
          wx.navigateBack();
        } else {
          wx.showToast({ title: '已从学习中删除', icon: 'none' });
        }
      }
    });
  },

  onRestoreWord() {
    const word = this.data.word;
    if (!word) return;
    const progress = loadProgress(this.data.bookId);
    const key = getWordKey(word);
    if (!key) return;

    const now = Date.now();
    const prev = progress[key] || {};
    const hasAnswered = Number(prev.correctCount || 0) > 0;
    progress[key] = {
      ...prev,
      wordId: getWordId(word) || prev.wordId,
      normalized: key,
      word: word.word || prev.word || key,
      status: hasAnswered ? 'reviewing' : 'new',
      nextReviewAt: hasAnswered ? prev.nextReviewAt : null,
      ignoredAt: null,
      clientUpdatedAt: now,
      updatedAt: now
    };
    saveProgress(this.data.bookId, progress);
    syncWordStateToCloud(this.data.bookId, word, progress[key]);
    syncPreviousLearnState(word, { ignored: false });
    this.setData({ isIgnored: false });
    wx.showToast({ title: '已恢复', icon: 'none' });
  },

  onLearnNext() {
    const pages = getCurrentPages();
    const prevPage = pages[pages.length - 2];

    if (prevPage) {
      prevPage._advanceAfterDetail = true;
    }

    wx.navigateBack();
  },

  onUnload() {
    clearTimeout(this._autoPlayTimer);
    stopAudio();
  },

  onHide() {
    clearTimeout(this._autoPlayTimer);
    stopAudio();
  }
});

function loadProgress(bookId) {
  return wx.getStorageSync(PROGRESS_KEY(bookId)) || {};
}

function saveProgress(bookId, progress) {
  wx.setStorageSync(PROGRESS_KEY(bookId), progress);
}

function getWordKey(word) {
  return word && (word.normalized || word.word);
}

function getWordId(word) {
  return word && (word.wordId || word._id || word.id || '');
}

function getWordProgress(progress, word) {
  const key = getWordKey(word);
  return key ? (progress[key] || {}) : {};
}

function withTimeout(promise, timeoutMs = 8000) {
  return Promise.race([
    promise,
    new Promise((_, reject) => {
      setTimeout(() => reject(new Error('REQUEST_TIMEOUT')), timeoutMs);
    })
  ]);
}

function setIgnoredProgress(bookId, word) {
  const progress = loadProgress(bookId);
  const key = getWordKey(word);
  if (!key) return {};
  const now = Date.now();
  const prev = progress[key] || {};
  progress[key] = {
    ...prev,
    wordId: getWordId(word) || prev.wordId,
    normalized: key,
    word: word.word || prev.word || key,
    status: 'ignored',
    ignoredAt: now,
    clientUpdatedAt: now,
    updatedAt: now
  };
  saveProgress(bookId, progress);
  return progress[key];
}

function syncWordStateToCloud(bookId, word, progress) {
  return learnService.updateWordState({
    bookId,
    wordId: getWordId(word) || progress.wordId,
    word: word.word,
    normalized: word.normalized || progress.normalized || word.word,
    favorite: progress.favorite,
    favoritedAt: progress.favoritedAt,
    status: progress.status === 'ignored' ? 'ignored' : undefined,
    ignoredAt: progress.ignoredAt,
    clientUpdatedAt: progress.clientUpdatedAt || progress.updatedAt
  }).catch((err) => {
    console.warn('[word-detail] sync word state failed', err);
  });
}

function syncPreviousLearnState(word, patch) {
  const pages = getCurrentPages();
  const prevPage = pages[pages.length - 2];
  if (!prevPage) return;

  if (typeof patch.favorite === 'boolean' && prevPage.data && prevPage.data.currentWord) {
    const current = prevPage.data.currentWord;
    if (getWordId(current) === getWordId(word) || getWordKey(current) === getWordKey(word)) {
      prevPage.setData({ isFavorite: patch.favorite });
    }
  }

  if (typeof patch.ignored === 'boolean' && prevPage.data && prevPage.data.currentWord) {
    const current = prevPage.data.currentWord;
    if (getWordId(current) === getWordId(word) || getWordKey(current) === getWordKey(word)) {
      prevPage.setData({ isIgnored: patch.ignored });
    }
  }
}

function buildTabMeta(word = {}) {
  const senses = Array.isArray(word.senses) ? word.senses : [];
  const antonyms = [];

  for (const sense of senses) {
    if (Array.isArray(sense.antonyms)) antonyms.push(...sense.antonyms);
  }

  return {
    hasSynonyms: senses.some(sense => Array.isArray(sense.synonyms) && sense.synonyms.length),
    hasAntonyms: antonyms.length > 0,
    antonyms: Array.from(new Set(antonyms.filter(Boolean))),
    confusingItems: normalizeConfusingItems(word, senses)
  };
}

function buildRelationSenseOptions(word = {}) {
  const senses = Array.isArray(word.senses) ? word.senses : [];
  return senses
    .filter(sense => sense && sense.senseId)
    .map(sense => ({
      senseId: sense.senseId,
      posLabel: sense.posLabel || formatPos(sense.pos) || '词义',
      translation: String(sense.translation || '').trim()
    }));
}

function buildRelationMeta(relations = [], groups = [], bookId = '', currentSenseId = '') {
  const normalizedRelations = relations.map(normalizeRelation).filter(item => item.word);
  return {
    relationRecords: normalizedRelations,
    ...buildRelationLists(normalizedRelations, bookId, currentSenseId),
    relationGroups: groups.map(normalizeRelationGroup)
  };
}

function buildRelationLists(relations = [], bookId = '', currentSenseId = '') {
  const scopedRelations = currentSenseId
    ? relations.filter(item => !item.fromSenseId || item.fromSenseId === currentSenseId)
    : relations;
  const relationSynonyms = scopedRelations.filter(item => item.kind === 'synonyms');
  const relationAntonyms = scopedRelations.filter(item => item.kind === 'antonyms');
  const relationConfusing = isContentWordbook(bookId)
    ? scopedRelations.filter(item => item.kind !== 'antonyms')
    : scopedRelations.filter(item => item.kind === 'confusing');

  return {
    relationSynonyms,
    relationAntonyms,
    relationConfusing
  };
}

function normalizeRelation(relation = {}) {
  const relationType = relation.relationType || '';
  const senseScope = relation.senseScope || {};
  const explanation = relation.explanationZh || relation.explanationEn || '';
  const example = relation.exampleZh || relation.exampleEn || '';

  return {
    ...relation,
    word: relation.toWord || relation.toWordId || '',
    typeLabel: relationTypeLabel(relationType),
    kind: relationKind(relationType),
    fromSenseId: String(senseScope.fromSenseId || '').trim(),
    toSenseId: String(senseScope.toSenseId || '').trim(),
    explanation,
    explanationTokens: tokenizeEnglishText(relation.explanationEn || ''),
    example,
    exampleEnTokens: tokenizeEnglishText(relation.exampleEn || ''),
    strengthText: ''
  };
}

function normalizeRelationGroup(group = {}) {
  return {
    ...group,
    memberLabel: Array.isArray(group.members)
      ? group.members.map(item => item.word).filter(Boolean).join(' / ')
      : ''
  };
}

function normalizeLearningContent(content) {
  if (!content) return null;
  const coreSense = content.coreSense && typeof content.coreSense === 'object'
    ? content.coreSense
    : {};
  const shortDefinitionEn = String(coreSense.en || content.shortDefinitionEn || content.short_definition_en || '').trim();
  const shortDefinitionZh = String(coreSense.zh || content.shortDefinitionZh || content.short_definition_zh || '').trim();
  const morphology = content.morphology || {};
  const examProfile = content.examProfile || {};
  const sourceStats = content.sourceStats || {};

  return {
    ...content,
    coreSense: {
      ...coreSense,
      en: shortDefinitionEn,
      zh: shortDefinitionZh
    },
    shortDefinitionEn,
    shortDefinitionZh,
    morphology: {
      ...morphology,
      segments: Array.isArray(morphology.segments)
        ? morphology.segments.map(item => ({
          ...item,
          meaningText: item.meaningZh || item.noteZh || ''
        }))
        : [],
      relatedWords: Array.isArray(morphology.relatedWords)
        ? morphology.relatedWords.map(item => ({
          ...item,
          displayText: item.translationZh || item.connectionZh || item.referenceStatus || ''
        }))
        : []
    },
    collocations: Array.isArray(content.collocations) ? content.collocations : [],
    grammarPatterns: Array.isArray(content.grammarPatterns)
      ? content.grammarPatterns.map(item => ({
        ...item,
        exampleTokens: tokenizeEnglishText(item.exampleEn || '')
      }))
      : [],
    commonErrors: Array.isArray(content.commonErrors)
      ? content.commonErrors.map(item => ({
        ...item,
        titleText: item.title || item.errorType || '注意',
        bodyText: item.explanationZh || item.noteZh || ''
      }))
      : [],
    examProfile,
    sourceStats,
    occurrenceText: sourceStats.occurrenceCount || sourceStats.articleCount
      ? `${Number(sourceStats.occurrenceCount || 0)} 次 / ${Number(sourceStats.articleCount || 0)} 篇`
      : '',
    priorityText: examProfile.priority ? `阅读优先级 ${examProfile.priority}/5` : '',
    writingText: examProfile.writingValue ? `写作价值 ${examProfile.writingValue}/5` : '',
    hasShortDefinition: Boolean(shortDefinitionEn),
    hasProfile: Boolean(sourceStats.occurrenceCount || sourceStats.articleCount || examProfile.priority || examProfile.writingValue),
    hasMorphology: Boolean(
      morphology.explanationZh
      || (Array.isArray(morphology.segments) && morphology.segments.length)
      || (Array.isArray(morphology.relatedWords) && morphology.relatedWords.length)
    ),
    hasCollocations: Array.isArray(content.collocations) && content.collocations.length > 0,
    hasGrammarPatterns: Array.isArray(content.grammarPatterns) && content.grammarPatterns.length > 0,
    hasCommonErrors: Array.isArray(content.commonErrors) && content.commonErrors.length > 0
  };
}

function normalizeSuggestion(item = {}) {
  return {
    ...item,
    word: item.targetWord || item.targetWordId || '',
    typeLabel: relationTypeLabel(item.relationType || ''),
    explanation: item.explanationZh || '',
    exampleEnTokens: tokenizeEnglishText(item.exampleEn || ''),
    targetHint: item.targetInWordbook ? '本书收录' : (item.targetInGlobalWords ? '词库收录' : '文本候选'),
    canOpen: Boolean(item.targetInWordbook)
  };
}

function relationKind(type) {
  if (type === 'antonym') return 'antonyms';
  if (type === 'confusing' || type === 'contrast') return 'confusing';
  if (type === 'synonym' || type === 'near_synonym') return 'synonyms';
  return 'related';
}

function relationTypeLabel(type) {
  const map = {
    synonym: '同义',
    near_synonym: '近义',
    antonym: '反义',
    confusing: '易混淆',
    contrast: '对比',
    related: '相关'
  };
  return map[type] || '相关';
}

function isRelationTab(tab) {
  return tab === 'synonyms' || tab === 'antonyms' || tab === 'confusing';
}

function decorateWordExamples(word = {}) {
  const senses = Array.isArray(word.senses) ? word.senses : [];
  return {
    ...word,
    senses: senses.map((sense) => {
      const definitionEn = String(sense.definitionEn || sense.definition_en || sense.definition || '').trim();
      const definitionZh = String(sense.definitionZh || sense.definition_zh || '').trim();
      return {
        ...sense,
        definitionEn,
        definitionZh,
        hasDetails: Boolean(definitionEn || definitionZh || sense.collins_definition || sense.gaming_link),
        posLabel: formatPos(sense.pos),
        translationLines: splitTranslationLines(sense.translation || ''),
        definitionTokens: tokenizeEnglishText(definitionEn),
        collinsDefinitionTokens: tokenizeEnglishText(sense.collins_definition && sense.collins_definition.en ? sense.collins_definition.en : ''),
        gamingLinkTokens: tokenizeEnglishText(sense.gaming_link && sense.gaming_link.context ? sense.gaming_link.context : ''),
        synonyms: Array.isArray(sense.synonyms)
          ? sense.synonyms.map((syn) => ({
            ...syn,
            nuanceTokens: tokenizeEnglishText(syn.nuance_explanation || ''),
            exampleTokens: tokenizeEnglishText(syn.example_en || '')
          }))
          : []
      };
    })
  };
}

function buildHeadingTranslations(word = {}) {
  const result = [];
  const senses = Array.isArray(word.senses) ? word.senses : [];

  for (const sense of senses) {
    const lines = Array.isArray(sense.translationLines) ? sense.translationLines : [];
    lines.forEach((line, index) => {
      const text = String(line || '').trim();
      if (!text) return;
      const embeddedPos = text.match(/^((?:n|v|vi|vt|adj|adv|a|ad|prep|conj|pron|num|int)\.)\s+/i);
      result.push({
        pos: embeddedPos ? embeddedPos[1] : (index === 0 ? (sense.posLabel || sense.pos || '') : ''),
        text: embeddedPos ? text.slice(embeddedPos[0].length).trim() : text
      });
    });
  }

  return result;
}

function splitTranslationLines(translation) {
  const text = String(translation || '').trim();
  if (!text) return [];

  const posPattern = '(?:n|v|adj|adv|a|ad|prep|conj|pron|num|int)\\.?';
  const marked = text
    .replace(new RegExp(`；\\s*(${posPattern}\\s*)`, 'gi'), '\n$1')
    .replace(new RegExp(`(\\/[^/]+\\/\\s*)(${posPattern}\\s*)`, 'gi'), '$1\n$2');
  const lines = marked
    .split(/\n+/)
    .map(item => normalizeTranslationLinePos(item.trim()))
    .filter(Boolean);

  return lines.length ? lines : [text];
}

function normalizeTranslationLinePos(line) {
  return String(line || '')
    .replace(/^((?:\/[^/]+\/\s*)?)(n|v|adj|adv|a|ad|prep|conj|pron|num|int)\.?\s+/i, (all, prefix, pos) => {
      const label = formatPos(pos);
      return `${prefix || ''}${label ? `${label} ` : ''}`;
    });
}

function normalizeConfusingItems(word, senses) {
  const sources = [
    word.confusing,
    word.confusables,
    word.easilyConfused,
    word.easily_confused,
    ...senses.map(sense => sense.confusing || sense.confusables || sense.easilyConfused || sense.easily_confused)
  ];

  return sources
    .flatMap(item => Array.isArray(item) ? item : (item ? [item] : []))
    .map((item) => {
      if (typeof item === 'string') return { word: item, explanation: '' };
      return {
        word: item.word || item.term || '',
        explanation: item.explanation || item.nuance || item.note || '',
        explanationTokens: tokenizeEnglishText(item.explanation || item.nuance || item.note || ''),
        example: item.example || item.example_en || '',
        exampleTokens: tokenizeEnglishText(item.example || item.example_en || '')
      };
    })
    .filter(item => item.word);
}

function formatExample(item, currentWord) {
  const line = item.line || {};
  const topic = item.topic || {};
  const scene = line.scene || {};
  const audio = line.audio || {};
  const timestampMs = Number(scene.timestampMs || 0);
  const highlightValues = getHighlightValues(currentWord);

  return {
    id: line._id,
    text: line.text || '',
    tokens: markCurrentTokens(tokenizeEnglishText(line.text || ''), highlightValues),
    translationZh: line.translationZh || '',
    audioUrl: audio.url || '',
    topicName: topic.name || '',
    topicCover: topic.cover || {},
    sourceLabel: [topic.name, scene.section, formatTime(timestampMs)].filter(Boolean).join(' · ')
  };
}

function getHighlightValues(word) {
  const values = new Set();
  const rawValues = [
    word && word.word,
    word && word.normalized,
    word && word.wordId ? String(word.wordId).replace(/^word_/, '') : ''
  ];
  rawValues.forEach((value) => {
    const normalized = normalizeLookupWord(value);
    if (!normalized) return;
    values.add(normalized);
    getLookupCandidates(normalized).forEach(candidate => values.add(candidate));
    getGeneratedInflections(normalized).forEach(candidate => values.add(candidate));
  });
  return values;
}

function markCurrentTokens(tokens, highlightValues) {
  if (!highlightValues || !highlightValues.size) return tokens;
  return tokens.map((token) => {
    if (!token.searchable) return token;
    return {
      ...token,
      current: highlightValues.has(normalizeLookupWord(token.value))
    };
  });
}

function isContentWordbook(bookId) {
  return String(bookId || '') === 'ielts_content_words';
}

function getExamplesTitle(bookId) {
  return isContentWordbook(bookId) ? '阅读原文例句' : '语料例句';
}

function getTabs(bookId) {
  return isContentWordbook(bookId) ? CONTENT_WORD_TABS : DEFAULT_TABS;
}

function tokenizeEnglishText(text) {
  const value = String(text || '');
  if (!value) return [];

  const parts = value.match(/[A-Za-z][A-Za-z'-]*|[^A-Za-z]+/g) || [];
  return parts.map((part) => {
    const isWord = /^[A-Za-z][A-Za-z'-]*$/.test(part);
    const normalized = part.toLowerCase().replace(/^'+|'+$/g, '');
    const searchable = isWord && normalized.length > 1;
    return {
      text: isWord ? part : preserveInlineWhitespace(part),
      value: searchable ? normalized : '',
      searchable
    };
  });
}

function preserveInlineWhitespace(value) {
  return String(value || '').replace(/[ \t\r\n]+/g, (spaces) => {
    return '\u00a0'.repeat(spaces.length);
  });
}

function normalizeLookupWord(value) {
  return String(value || '')
    .toLowerCase()
    .replace(/^word_/, '')
    .replace(/^'+|'+$/g, '')
    .replace(/'s$/, '');
}

async function lookupTokenWord(bookId, rawWord) {
  const candidates = getLookupCandidates(rawWord);

  for (const candidate of candidates) {
    const exact = await getWordByWordAsync(bookId, candidate).catch(() => null);
    if (exact) return exact;
  }

  for (const candidate of candidates) {
    if (candidate.length < 3) continue;
    const results = await searchWordsAsync(bookId, candidate, { limit: 5 }).catch(() => []);
    if (results && results.length) return results[0];
  }

  return null;
}

function getLookupCandidates(rawWord) {
  const word = String(rawWord || '')
    .toLowerCase()
    .replace(/^'+|'+$/g, '')
    .replace(/'s$/, '');
  const candidates = [];

  function add(value) {
    const normalized = String(value || '').replace(/^'+|'+$/g, '');
    if (normalized.length > 1 && !candidates.includes(normalized)) {
      candidates.push(normalized);
    }
  }

  add(word);

  if (word.endsWith('ies') && word.length > 4) add(`${word.slice(0, -3)}y`);
  if (word.endsWith('ves') && word.length > 4) {
    add(`${word.slice(0, -3)}f`);
    add(`${word.slice(0, -3)}fe`);
  }
  if (word.endsWith('es') && word.length > 3) add(word.slice(0, -2));
  if (word.endsWith('s') && word.length > 3) add(word.slice(0, -1));

  if (word.endsWith('ied') && word.length > 4) add(`${word.slice(0, -3)}y`);
  if (word.endsWith('ed') && word.length > 3) {
    const base = word.slice(0, -2);
    add(base);
    add(`${base}e`);
    if (hasDoubleFinalConsonant(base)) add(base.slice(0, -1));
  }

  if (word.endsWith('ing') && word.length > 5) {
    const base = word.slice(0, -3);
    add(base);
    add(`${base}e`);
    if (hasDoubleFinalConsonant(base)) add(base.slice(0, -1));
  }

  if (word.endsWith('er') && word.length > 4) {
    const base = word.slice(0, -2);
    add(base);
    add(`${base}e`);
    if (hasDoubleFinalConsonant(base)) add(base.slice(0, -1));
  }

  if (word.endsWith('est') && word.length > 5) {
    const base = word.slice(0, -3);
    add(base);
    add(`${base}e`);
    if (hasDoubleFinalConsonant(base)) add(base.slice(0, -1));
  }

  return candidates;
}

function getGeneratedInflections(rawWord) {
  const word = normalizeLookupWord(rawWord);
  const candidates = [];

  function add(value) {
    const normalized = normalizeLookupWord(value);
    if (normalized.length > 1 && !candidates.includes(normalized)) {
      candidates.push(normalized);
    }
  }

  if (!word) return candidates;

  add(word);

  if (word.endsWith('y') && word.length > 2 && !/[aeiou]y$/.test(word)) {
    add(`${word.slice(0, -1)}ies`);
    add(`${word.slice(0, -1)}ied`);
  } else {
    add(`${word}s`);
    add(`${word}ed`);
  }

  if (/(s|x|z|ch|sh)$/.test(word)) add(`${word}es`);
  if (word.endsWith('e') && word.length > 2) {
    add(`${word}d`);
    add(`${word.slice(0, -1)}ing`);
  } else {
    add(`${word}ing`);
  }

  if (word.endsWith('f') && word.length > 2) add(`${word.slice(0, -1)}ves`);
  if (word.endsWith('fe') && word.length > 3) add(`${word.slice(0, -2)}ves`);

  return candidates;
}

function hasDoubleFinalConsonant(value) {
  if (!value || value.length < 2) return false;
  const last = value[value.length - 1];
  const prev = value[value.length - 2];
  return last === prev && !/[aeiou]/.test(last);
}

function formatTime(timestampMs) {
  if (!timestampMs) return '';
  const totalSeconds = Math.floor(timestampMs / 1000);
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = totalSeconds % 60;
  return `${minutes}:${String(seconds).padStart(2, '0')}`;
}

function getPopoverPosition(e) {
  const detail = e.detail || {};
  const info = wx.getWindowInfo ? wx.getWindowInfo() : wx.getSystemInfoSync();
  const width = info.windowWidth || 375;
  const margin = 12;
  const rawX = Number(detail.x || width / 2);
  const popoverWidth = Math.min(width - margin * 2, width * 384 / 750);
  const half = popoverWidth / 2;
  const x = Math.max(half + margin, Math.min(width - half - margin, rawX));
  const y = Math.max(80, Number(detail.y || 120) + 14);
  const arrowX = Math.max(18, Math.min(popoverWidth - 18, rawX - x + half));

  return { x, y, arrowX };
}
