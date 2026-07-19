Component({
  properties: {
    role: { type: String, value: 'assistant' }, // user | assistant
    content: { type: String, value: '' },
    suggestion: { type: String, value: '' }
  },
  methods: {
    onApplySuggestion() {
      this.triggerEvent('apply', { text: this.data.suggestion });
    }
  }
});
