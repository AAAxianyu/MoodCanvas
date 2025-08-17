Component({
  options: {
    multipleSlots: true,
    virtualHost: true,
    styleIsolation: 'isolated'
  },
  properties: {
    role: { type: String, value: 'ai' },
    type: { type: String, value: 'text' },
    content: { type: String, value: '' },
    src: { type: String, value: '' } // 将 imageUrl 改为 src
  },
  methods: {
    onTapImage() {
      if (this.data.src) {
        this.triggerEvent('preview', { src: this.data.src });
      }
    }
  }
});
