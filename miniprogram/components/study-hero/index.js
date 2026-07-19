Component({
  options: {
    multipleSlots: true
  },

  properties: {
    word: { type: String, value: '' },
    phonetic: { type: null, value: '' },
    translations: { type: Array, value: [] },
    showHeading: { type: Boolean, value: true },
    showProgress: { type: Boolean, value: false },
    progressPercent: { type: Number, value: 0 },
    showRecovery: { type: Boolean, value: false },
    recoveryPassed: { type: Number, value: 0 }
  },

  data: {
    phoneticText: ''
  },

  observers: {
    phonetic(value) {
      this.setData({ phoneticText: formatPhonetic(value) });
    }
  },

  methods: {
    onBack() {
      this.triggerEvent('back');
    },

    onPlay() {
      this.triggerEvent('play');
    }
  }
});

function formatPhonetic(value) {
  if (!value) return '';
  if (typeof value === 'string') return value.trim();
  if (typeof value !== 'object') return String(value).trim();
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
