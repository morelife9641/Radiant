Component({
  options: { multipleSlots: true, styleIsolation: 'shared' },
  properties: {
    type: { type: String, value: 'primary' }, // primary | ghost | text
    size: { type: String, value: 'md' },      // sm | md | lg
    block: { type: Boolean, value: false },
    disabled: { type: Boolean, value: false },
    loading: { type: Boolean, value: false }
  },
  methods: {
    onTap(e) {
      if (this.data.disabled || this.data.loading) return;
      this.triggerEvent('tap', e.detail);
    }
  }
});
