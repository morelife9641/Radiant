Component({
  options: {
    virtualHost: true
  },

  properties: {
    title: {
      type: String,
      value: '正在点亮内容'
    },
    description: {
      type: String,
      value: ''
    },
    tone: {
      type: String,
      value: 'warm'
    },
    fullscreen: {
      type: Boolean,
      value: false
    },
    compact: {
      type: Boolean,
      value: false
    },
    fill: {
      type: Boolean,
      value: false
    },
    raised: {
      type: Boolean,
      value: false
    }
  }
});
