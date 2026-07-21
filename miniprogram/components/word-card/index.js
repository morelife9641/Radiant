Component({
  properties: {
    word: { type: Object, value: null },
    choices: { type: Array, value: [] },
    question: { type: Object, value: null },
    revealAnswer: { type: Boolean, value: false },
    answeredState: { type: Boolean, value: false },
    selectedValueState: { type: String, value: '' },
    correctState: { type: Boolean, value: false },
    textAnswerState: { type: String, value: '' },
    hideHeading: { type: Boolean, value: false }
  },
  data: {
    primarySense: null,   // senses[0]
    wordPhoneticText: '',
    promptPhoneticText: '',
    promptDisplayText: '',
    selectedValue: '',
    revealedOptionValues: {},
    textAnswer: '',
    promptChineseText: '',
    promptChineseVisible: false,
    answered: false,
    correct: false
  },
  observers: {
    'word, question': function onQuestionChanged(w, question) {
      const currentWord = question || w;
      if (!currentWord) {
        this.setData({ primarySense: null, wordPhoneticText: '', promptPhoneticText: '', promptDisplayText: '', selectedValue: '', revealedOptionValues: {}, textAnswer: '', promptChineseText: '', promptChineseVisible: false, answered: false, correct: false });
        return;
      }
      const primary = (w && w.senses && w.senses[0]) || null;
      const wordPhoneticText = formatPhonetic(w && w.phonetic);
      this.setData({
        primarySense: primary,
        wordPhoneticText,
        promptPhoneticText: formatPhonetic(question && question.prompt && question.prompt.phonetic) || wordPhoneticText,
        promptDisplayText: formatPromptText(question),
        selectedValue: '',
        revealedOptionValues: {},
        textAnswer: '',
        promptChineseText: getPromptChineseText(w, question),
        promptChineseVisible: false,
        answered: false,
        correct: false
      });
    },
    revealAnswer(value) {
      if (!value || this.data.answered) return;
      const question = this.data.question || {};
      const answer = question.answer || {};
      this.setData({
        selectedValue: '',
        revealedOptionValues: buildRevealedOptionValues(question, ''),
        textAnswer: answer.value || this.data.textAnswer || '',
        answered: true,
        correct: false
      });
    },
    'answeredState, selectedValueState, correctState, textAnswerState': function syncAnsweredState(answeredState, selectedValueState, correctState, textAnswerState) {
      const nextSelectedValue = selectedValueState || '';
      const nextTextAnswer = textAnswerState || this.data.textAnswer || '';
      const nextCorrect = Boolean(correctState);

      if (!answeredState) {
        if (
          !this.data.answered
          && this.data.selectedValue === nextSelectedValue
          && this.data.textAnswer === (textAnswerState || '')
        ) return;

        this.setData({
          selectedValue: nextSelectedValue,
          revealedOptionValues: {},
          textAnswer: textAnswerState || '',
          answered: false,
          correct: false
        });
        return;
      }

      if (
        this.data.answered
        && this.data.selectedValue === nextSelectedValue
        && this.data.correct === nextCorrect
        && this.data.textAnswer === nextTextAnswer
      ) return;

      this.setData({
        selectedValue: nextSelectedValue,
        revealedOptionValues: buildRevealedOptionValues(this.data.question || {}, nextSelectedValue),
        textAnswer: nextTextAnswer,
        answered: true,
        correct: nextCorrect
      });
    }
  },
  methods: {
    onTogglePromptTranslation() {
      if (!this.data.promptChineseText) return;
      this.setData({ promptChineseVisible: !this.data.promptChineseVisible });
    },

    onChooseOption(e) {
      const { value, correct } = e.currentTarget.dataset;
      if (this.data.answered) {
        this.setData({
          revealedOptionValues: {
            ...(this.data.revealedOptionValues || {}),
            [value]: true
          }
        });
        return;
      }
      const isCorrect = correct === true || Number(correct) === 1;
      const question = this.data.question || {};
      const choice = (question.choices || this.data.choices || []).find(item => item.value === value) || {};

      this.setData({
        selectedValue: value,
        revealedOptionValues: buildRevealedOptionValues(question, value),
        answered: true,
        correct: isCorrect
      });
      this.triggerEvent('answer', {
        questionId: question.id || '',
        wordId: question.wordId || '',
        senseId: question.senseId || '',
        type: question.type || 'word_to_zh',
        result: isCorrect ? 'known' : 'unknown',
        correct: isCorrect,
        value,
        answerText: choice.text || ''
      });
    },
    onInputSpelling(e) {
      this.setData({ textAnswer: String(e.detail.value || '').trim() });
    },
    onSubmitSpelling() {
      if (this.data.answered) return;
      if (!String(this.data.textAnswer || '').trim()) return;
      const question = this.data.question || {};
      const answer = question.answer || {};
      const typed = normalizeTextAnswer(this.data.textAnswer);
      const acceptable = Array.isArray(answer.acceptable) && answer.acceptable.length
        ? answer.acceptable
        : [answer.normalized || answer.value || ''];
      const isCorrect = acceptable.map(normalizeTextAnswer).includes(typed);

      this.setData({
        answered: true,
        correct: isCorrect
      });
      this.triggerEvent('answer', {
        questionId: question.id || '',
        wordId: question.wordId || '',
        senseId: question.senseId || '',
        type: question.type || 'spelling',
        result: isCorrect ? 'known' : 'unknown',
        correct: isCorrect,
        value: typed,
        answerText: this.data.textAnswer
      });
    },
    onPlay() {
      this.triggerEvent('play');
    },
    onOpenDetail() {
      this.triggerEvent('detail');
    }
  }
});

function normalizeTextAnswer(value) {
  return String(value || '')
    .trim()
    .toLowerCase()
    .replace(/[.,!?;:'"()[\]{}，。！？；：“”‘’（）【】]+$/g, '')
    .replace(/^[.,!?;:'"()[\]{}，。！？；：“”‘’（）【】]+/g, '')
    .replace(/\s+/g, ' ');
}

function formatPromptText(question) {
  const prompt = question && question.prompt ? question.prompt : {};
  const text = String(prompt.text || '');
  if (prompt.lang !== 'en') return text;
  return text.replace(/[A-Za-z]{9,}/g, addSoftHyphen);
}

function addSoftHyphen(word) {
  const vowels = 'aeiouy';
  const lower = word.toLowerCase();
  const candidates = [];

  for (let index = 4; index <= word.length - 3; index += 1) {
    const previous = lower[index - 1];
    const current = lower[index];
    if (!vowels.includes(previous) && vowels.includes(current)) candidates.push(index);
  }

  if (!candidates.length) {
    const midpoint = Math.max(4, Math.min(word.length - 3, Math.round(word.length / 2)));
    candidates.push(midpoint);
  }

  const midpoint = word.length / 2;
  const breakAt = candidates.sort((a, b) => Math.abs(a - midpoint) - Math.abs(b - midpoint))[0];
  return `${word.slice(0, breakAt)}\u00AD${word.slice(breakAt)}`;
}

function buildRevealedOptionValues(question = {}, selectedValue = '') {
  const revealed = {};
  if (selectedValue) revealed[selectedValue] = true;
  const correctChoice = (question.choices || []).find(choice => choice && choice.correct);
  if (correctChoice && correctChoice.value) revealed[correctChoice.value] = true;
  return revealed;
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

function getPromptChineseText(word, question) {
  const prompt = question && question.prompt ? question.prompt : {};
  if (prompt.lang !== 'en') return '';

  const coreSense = word && word.coreSense && typeof word.coreSense === 'object'
    ? word.coreSense
    : {};
  const primarySense = word && Array.isArray(word.senses) ? word.senses[0] : null;
  return String(
    prompt.zhText
    || coreSense.zh
    || (word && (word.shortDefinitionZh || word.short_definition_zh))
    || (primarySense && (primarySense.definitionZh || primarySense.definition_zh))
    || (primarySense && primarySense.translation)
    || ''
  ).trim();
}
