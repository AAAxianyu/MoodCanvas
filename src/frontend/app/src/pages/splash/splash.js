Page({
  onLoad() {
    // 可选：显示加载动画
    tt.showLoading({ title: '加载中...' });

    setTimeout(() => {
      tt.redirectTo({
        url: '/src/pages/index/index', // 更新路径
        success: () => {
          tt.hideLoading();
        },
        fail: (err) => {
          console.error('跳转失败:', err);
          tt.hideLoading();
          tt.showToast({ title: '跳转失败，请重试', icon: 'none' });
        }
      });
    }, 2000);
  },

  onLogoError(e) {
    console.error('Logo加载失败:', e.detail.errMsg);
  },

  onVectorError(e) {
    console.error('Vector图片加载失败:', e.detail.errMsg);
  },

  onGroup16Error(e) {
    console.error('Group16图片加载失败:', e.detail.errMsg);
  }
});
