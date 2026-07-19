Component({
  options: {
    virtualHost: true
  },

  methods: {
    onTap() {
      this.triggerEvent('back');
    }
  }
});
