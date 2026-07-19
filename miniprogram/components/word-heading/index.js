Component({
  properties: {
    word: { type: String, value: '' },
    phonetic: { type: String, value: '' },
    translations: { type: Array, value: [] },
    showRecovery: { type: Boolean, value: false },
    recoveryPassed: { type: Number, value: 0 }
  },

  methods: {
    onPlay() {
      this.triggerEvent('play');
    }
  }
});
