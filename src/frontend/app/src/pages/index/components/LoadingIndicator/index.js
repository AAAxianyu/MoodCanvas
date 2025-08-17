Component({
  properties: {
    text: {
      type: String,
      value: '加载中...'
    },
    show: {
      type: Boolean,
      value: false,
      observer: function(newVal) {
        if (!newVal) {
          this.setData({ isHiding: true });
          setTimeout(() => {
            this.setData({ isHiding: false });
          }, 500);
        }
      }
    },
    progress: {
      type: Number,
      value: 0
    }
  },
  data: {
    isHiding: false
  },
  methods: {}
});
