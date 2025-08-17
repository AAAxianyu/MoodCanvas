const app = getApp();

// —— 工具函数 —— //
function formatTime(d = new Date()) {
  const h = String(d.getHours()).padStart(2, '0');
  const m = String(d.getMinutes()).padStart(2, '0');
  return `${h}:${m}`;
}
function genId(prefix = 'u') {
  return `${prefix}_${Date.now()}_${Math.random().toString(36).slice(2, 7)}`;
}

Page({
  data: {
    messages: [],
    inputValue: '',
    toView: 'bottom',
    showImageSender: false,   // ← 新增：控制弹层显隐
    presetImages: [],          // ← 新增：预置给 ImageSender 的图片
    showLoading: false,         // 新增：控制加载动画显隐
    loadingProgress: 0,
    loadingText: '情绪PLOG生成中...',
    previewImages: [], // 新增：用于预览的图片列表
    audioTempPath: null, // 新增：存储录音临时路径
    isRecording: false, // 新增：录音状态标志
    recordingTime: 0, // 新增：录音时长
    showHeaderImage: true, // 控制图片显示
    showSidebar: false, // 新增：控制侧边栏显隐
  },

  // 防止连点
  _sendingLock: false,

  onLoad() {
    // 在 onLoad 中添加版本检测
    tt.getSystemInfo({
      success: (res) => {
        if (compareVersion(res.SDKVersion, '2.87.0') >= 0) {
          this._supportKeyboardEvent = true;
        }
      }
    });

    // 修复：使用输入框组件的 bindkeyboardheightchange 事件
    this._keyboardHeightChange = (res) => {
      this.setData({
        keyboardHeight: res.detail.height,
        composerPaddingBottom: res.detail.height > 0 ? '0' : '24rpx'
      });
      this._scrollToBottom();
    };

    // 3秒后自动隐藏图片
    setTimeout(() => {
      this.setData({ showHeaderImage: false });
    }, 3000);
  },

  onUnload() {
    // 修复：清理事件监听（在组件中通过 offKeyboardHeightChange 实现）
    if (this._keyboardHeightChange) {
      this._keyboardHeightChange = null;
    }
  },

  toggleSidebar() {
    this.setData({ showSidebar: !this.data.showSidebar });
  },

  navigateTo(e) {
    const url = e.currentTarget.dataset.url;
    tt.navigateTo({ url });
    this.setData({ showSidebar: false });
  },

  // —— 输入 —— //
  handleInput(e) {
    this.setData({ inputValue: e.detail.value });
  },

  // —— 录音入口（待接） —— //
  onRecord() {
    if (this.data.audioTempPath) {
      tt.showToast({ title: '请先发送当前录音', icon: 'none' });
      return;
    }

    // 新增：WAV格式兼容性检测
    tt.getSystemInfo({
      success: (res) => {
        const sdkVersion = res.SDKVersion;
        if (compareVersion(sdkVersion, '1.25.0') < 0) {
          tt.showToast({ title: '当前设备不支持WAV格式', icon: 'none' });
          return;
        }

        const recorderManager = tt.getRecorderManager();
        recorderManager.onStart(() => {
          this.setData({ 
            isRecording: true,
            recordingTime: 0
          });
          this._recordingStartTime = Date.now();
          this._recordingInterval = setInterval(() => {
            const elapsed = Math.floor((Date.now() - this._recordingStartTime) / 1000);
            this.setData({ recordingTime: elapsed });
          }, 200);
        });

        recorderManager.onStop((res) => {
          clearInterval(this._recordingInterval);
          this.setData({ 
            isRecording: false,
            audioTempPath: res.tempFilePath
          });
        });

        recorderManager.onError((err) => {
          clearInterval(this._recordingInterval);
          this.setData({ isRecording: false });
          console.error('录音错误:', err);
        });

        recorderManager.start({
          format: 'wav', // 强制使用WAV格式
          duration: 60000
        });
      }
    });
  },

  stopRecording() {
    if (!this.data.isRecording) return;
    tt.getRecorderManager().stop();
  },

  // —— 相机/相册 → 预览页 —— //
  onCamera() {
    tt.chooseImage({
      count: 1, // 每次选择一张图片
      sizeType: ['original', 'compressed'], // 支持原图和压缩图
      sourceType: ['album', 'camera'], // 支持从相册和相机选择
      success: (res) => {
        const tempFilePaths = res.tempFilePaths;
        if (tempFilePaths && tempFilePaths.length > 0) {
          this.setData({
            previewImages: tempFilePaths // 更新预览图片
          });
        }
      },
      fail: (err) => {
        console.error('选择图片失败:', err);
        tt.showToast({
          title: '选择图片失败',
          icon: 'none'
        });
      }
    });
  },

  onSendImages(e) {
    const paths = e.detail.files || [];
    if (!paths.length) return this.setData({ showImageSender: false, presetImages: [] });

    const now = new Date();
    const add = paths.map(p => ({
      mid: genId('ai'),
      role: 'ai',
      type: 'image',
      src: p,
      time: formatTime(now)
    }));

    this.setData({
      messages: this.data.messages.concat(add),
      showImageSender: false,
      presetImages: []
    }, this._scrollToBottom);
  },

  // —— 发送（按钮/回车共用） —— //
  async handleSend(e) {
    if (this._sendingLock) return;
    this.setData({ showLoading: true });

    const raw = e?.detail?.value || this.data.inputValue;
    const text = raw.trim();
    const hasImages = this.data.previewImages.length > 0;
    const hasAudio = !!this.data.audioTempPath;

    if (!text && !hasImages && !hasAudio) {
      this.setData({ showLoading: false });
      return;
    }

    this._sendingLock = true;
    const now = new Date();
    const messagesToAdd = [];

    // 文字消息
    if (text) {
      messagesToAdd.push({
        mid: genId('user'),
        role: 'user',
        type: 'text',
        content: text.slice(0, 500),
        time: formatTime(now),
        status: 'sent'
      });
    }

    // 图片消息
    if (hasImages) {
      this.data.previewImages.forEach(path => {
        messagesToAdd.push({
          mid: genId('user'),
          role: 'user',
          type: 'image',
          src: path,
          time: formatTime(now)
        });
      });
    }

    // 语音消息
    if (hasAudio) {
      messagesToAdd.push({
        mid: genId('user'),
        role: 'user',
        type: 'audio',
        src: this.data.audioTempPath,
        time: formatTime(now)
      });
    }

    this.setData({
      messages: this.data.messages.concat(messagesToAdd),
      inputValue: '',
      previewImages: [],
      audioTempPath: null
    }, async () => {
      this._scrollToBottom();
      this._pushTyping();

      try {
        // 构造FormData
        const formData = new tt.FormData();
        if (text) formData.append('text', text);
        if (hasImages) {
          this.data.previewImages.forEach((path, index) => {
            formData.append('image_file', {
              uri: path,
              name: `image_${index}.jpg`,
              type: 'image/jpeg'
            });
          });
        }
        if (hasAudio) {
          formData.append('audio', {
            uri: this.data.audioTempPath,
            name: 'audio.wav',
            type: 'audio/wav'
          });
        }

        // 发送请求
        const response = await this._sendToBackend(formData);

        // 处理响应
        if (response.audio?.generated_content) {
          this._replaceTypingWith({
            mid: genId('ai'),
            role: 'ai',
            type: 'text',
            content: response.audio.generated_content.text,
            time: formatTime()
          });

          if (response.generated_image_url) {
            this._appendMessage({
              mid: genId('ai'),
              role: 'ai',
              type: 'image',
              src: response.generated_image_url, // 直接使用返回的URL
              time: formatTime()
            });
          }
        }
      } catch (err) {
        this._replaceTypingWith({
          mid: genId('ai'),
          role: 'ai',
          type: 'text',
          content: '请求失败，请稍后重试',
          time: formatTime()
        });
      } finally {
        this.setData({ showLoading: false });
        this._sendingLock = false;
      }
    });
  },

  // —— 工具：加“AI 正在输入”占位 —— //
  _pushTyping() {
    // 若已存在占位，避免重复
    const hasTyping = this.data.messages.some(m => m.status === 'typing');
    if (hasTyping) return;

    const typing = {
      mid: 'typing', // 固定 id，方便后续替换
      role: 'ai',
      type: 'text',
      content: '正在思考…',
      time: formatTime(),
      status: 'typing'
    };
    this.setData({ messages: this.data.messages.concat(typing) }, this._scrollToBottom);
  },

  // —— 工具：用真实消息替换“typing”占位 —— //
  _replaceTypingWith(realMsg) {
    const list = this.data.messages.slice();
    const idx = list.findIndex(m => m.mid === 'typing');
    if (idx !== -1) {
      list.splice(idx, 1, realMsg);
    } else {
      list.push(realMsg);
    }
    this.setData({ messages: list }, this._scrollToBottom);
  },

  // —— 工具：追加一条消息 —— //
  _appendMessage(msg) {
    this.setData({ messages: this.data.messages.concat(msg) }, this._scrollToBottom);
  },

  // —— 工具：滚到底 —— //
  _scrollToBottom() {
    this.setData({ toView: '' }, () => this.setData({ toView: 'bottom' }));
  },

  handleGeneratePLOG() {
    this.setData({
      showLoading: true,
      loadingProgress: 0,
      loadingText: '情绪PLOG生成中...0%'
    });

    // 模拟后端消息接收（实际替换为WebSocket或API轮询）
    const mockResponseTime = 40000; // 40秒模拟响应时间
    const startTime = Date.now();

    const updateProgress = () => {
      const elapsed = Date.now() - startTime;
      const progress = Math.min(Math.floor((elapsed / mockResponseTime) * 100), 100);
      this.setData({
        loadingProgress: progress,
        loadingText: `情绪PLOG生成中...${progress}%`
      });

      if (progress < 100) {
        setTimeout(updateProgress, 100); // 每100ms更新一次
      } else {
        setTimeout(() => {
          this.setData({ showLoading: false });
          this._appendMessage({
            mid: genId('ai'),
            role: 'ai',
            type: 'text',
            content: '情绪PLOG生成完成！',
            time: formatTime()
          });
        }, 500); // 淡出动画时间
      }
    };

    updateProgress();
  },

  removePreviewImage(e) {
    const index = e.currentTarget.dataset.index;
    const newPreviewImages = this.data.previewImages.filter((_, i) => i !== index);
    this.setData({ previewImages: newPreviewImages });
  },

  playAudio(e) {
    const src = e.currentTarget.dataset.src;
    if (src) {
      const innerAudioContext = tt.createInnerAudioContext();
      innerAudioContext.src = src;
      innerAudioContext.play();
    }
  },

  async _sendToBackend(formData) {
    // 修复：添加超时和重试机制
    try {
      const res = await tt.request({
        url: 'http://115.190.117.155/api/v1/emotion/analyze_multi',
        method: 'POST',
        timeout: 30000, // 30秒超时
        header: {
          'Content-Type': 'multipart/form-data'
        },
        data: formData
      });

      if (res.statusCode === 200) {
        return res.data;
      } else {
        throw new Error(`请求失败: ${res.statusCode}`);
      }
    } catch (err) {
      console.error('请求出错:', err);
      if (err.errMsg.includes('timeout')) {
        tt.showToast({ title: '请求超时', icon: 'none' });
      } else {
        tt.showToast({ title: '请求失败', icon: 'none' });
      }
      throw err;
    }
  },

  // 新增图片处理
  onImageLoad(e) {
    console.log('图片加载成功:', e.currentTarget.dataset.index);
  },

  onImageError(e) {
    console.error('图片加载失败:', e.detail.errMsg);
    const index = e.currentTarget.dataset.index;
    const newPreviewImages = [...this.data.previewImages];
    newPreviewImages.splice(index, 1);
    this.setData({ previewImages: newPreviewImages });
    tt.showToast({ title: '图片加载失败', icon: 'none' });
  }
});

// 新增：版本比较工具函数
function compareVersion(v1, v2) {
  const v1Parts = v1.split('.').map(Number);
  const v2Parts = v2.split('.').map(Number);
  for (let i = 0; i < 3; i++) {
    if (v1Parts[i] > v2Parts[i]) return 1;
    if (v1Parts[i] < v2Parts[i]) return -1;
  }
  return 0;
}
