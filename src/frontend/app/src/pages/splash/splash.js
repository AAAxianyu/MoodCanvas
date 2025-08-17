Page({
  onLoad() {
    setTimeout(() => {
      tt.redirectTo({
        url: '/src/pages/index/index'
      });
    }, 5000); // 修改为5秒
  },

  onImageError(e) {
    console.error('启动图加载失败:', e.detail.errMsg);
    tt.showToast({ title: '启动图加载失败', icon: 'none' });
    // 加载替代图片
    this.setData({
      imageUrl: '/static/images/test.jpg' // 替代图片路径
    });
  }
});
