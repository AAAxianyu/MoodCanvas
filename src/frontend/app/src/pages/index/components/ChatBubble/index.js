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
    audioSrc: { type: String, value: '' }
  },
  methods: {
    onTapImage() {
      if (this.data.src) {
        this.triggerEvent('preview', { src: this.data.src });
      }
    },
    playAudio() {
      if (this.data.audioSrc) {
        const innerAudioContext = tt.createInnerAudioContext();
        innerAudioContext.src = this.data.audioSrc;
        innerAudioContext.play();
      }
    }
  }
});
