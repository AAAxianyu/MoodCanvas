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
    src: { type: String, value: '' },
    audioSrc: { type: String, value: '' } // 新增：支持语音消息
  },
  methods: {
    onTapImage() {
      if (this.data.src) {
        this.triggerEvent('preview', { src: this.data.src });
      }
    }
  }
});
