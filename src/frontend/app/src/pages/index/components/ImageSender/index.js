Component({
  options: { virtualHost: true, styleIsolation: 'isolated' },
  properties: {
    max: { type: Number, value: 6 },
    autoSend: { type: Boolean, value: true },
    preset: { type: Array, value: [] }
  },
  data: { files: [] },

  observers: {
    preset(v) {
      console.log('preset changed:', v);
      if (Array.isArray(v) && v.length) {
        const mapped = v.map(p => ({
          id: `p_${Date.now()}_${Math.random().toString(36).slice(2,6)}`,
          path: p
        }));
        this.setData({ files: mapped.slice(0, this.data.max) });
      }
    }
  },

  methods: {
    onPick() {
      const remain = this.data.max - this.data.files.length;
      if (remain <= 0) return;
      tt.chooseImage({
        count: remain,
        sizeType: ['original', 'compressed'],
        sourceType: ['album', 'camera'],
        success: (res) => {
          const paths = res.tempFilePaths
            || (res.tempFiles && res.tempFiles.map(f => f.tempFilePath))
            || [];
          const append = paths.map(p => ({
            id: `f_${Date.now()}_${Math.random().toString(36).slice(2,6)}`,
            path: p
          }));
          this.setData({ files: this.data.files.concat(append) }, () => {
            if (this.data.autoSend) this._send(this.data.files.map(f => f.path));
          });
        }
      });
    },
    onPreview(e) {
      const { path } = e.currentTarget.dataset;
      const urls = this.data.files.map(f => f.path);
      tt.previewImage({ current: path, urls });
    },
    onRemove(e) {
      const { id } = e.currentTarget.dataset;
      this.setData({ files: this.data.files.filter(f => f.id !== id) });
    },
    onSendTap() {
      if (!this.data.files.length) return;
      this._send(this.data.files.map(f => f.path));
    },
    _send(paths) {
      this.triggerEvent('send', { files: paths });
      if (!this.properties.autoSend) this.setData({ files: [] });
    }
  }
});
