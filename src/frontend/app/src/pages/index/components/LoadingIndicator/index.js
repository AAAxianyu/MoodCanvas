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
            this.setData({ 
              isHiding: false,
              showImage: false // 新增：同步控制图片显隐
            });
          }, 500);
        } else {
          this.setData({ showImage: true }); // 新增：显示时同步开启图片
        }
      }
    },
    progress: {
      type: Number,
      value: 0
    }
  },
  data: {
    isHiding: false,
    showImage: true // 新增：图片显隐状态
  },
  methods: {}
});
