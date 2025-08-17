Page({
  onLoad() {
    setTimeout(() => {
      tt.redirectTo({
        url: '/src/pages/index/index',
        success: () => console.log('跳转成功'),
        fail: (err) => {
          console.error('跳转失败:', err);
          tt.showToast({ title: '跳转失败', icon: 'none' });
        }
      });
    }, 3000);
  }
});
