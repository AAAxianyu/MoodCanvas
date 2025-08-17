Page({
  data: {
    imageUrl: 'https://picsum.photos/600/800', // 默认图片
    emojis: [
      { icon: 'https://picsum.photos/48/48?grayscale' },
      { icon: 'https://picsum.photos/48/48?yellow' },
      { icon: 'https://picsum.photos/48/48?grayscale' },
      { icon: 'https://picsum.photos/48/48?grayscale' },
      { icon: 'https://picsum.photos/48/48?grayscale' }
    ],
    currentEmojiIndex: 1,
    progressPercent: 20
  },
  
  onLoad(options) {
    if (options.imageUrl) {
      this.setData({ imageUrl: options.imageUrl });
    }
  },
  
  selectEmoji(e) {
    const index = e.currentTarget.dataset.index;
    this.setData({
      currentEmojiIndex: index,
      progressPercent: index * 20
    });
  },
  
  closePreview() {
    tt.navigateBack();
  },
  
  confirmSelection() {
    // 处理确认选择的逻辑
    tt.navigateBack();
  }
});
