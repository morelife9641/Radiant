Component({
  properties: {
    value: { type: Number, value: 0 },
    total: { type: Number, value: 100 },
    size: { type: Number, value: 120 }
  },
  observers: {
    'value, total': function () {
      const value = Number(this.data.value || 0);
      const total = Number(this.data.total || 0);
      this.setData({
        percent: total ? Math.min(1, value / total) : 0,
        displayValue: value,
        displayTotal: total
      });
    }
  }
});
