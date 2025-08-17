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
    presetImages: []          // ← 新增：预置给 ImageSender 的图片
  },

  // 防止连点
  _sendingLock: false,

  // —— 输入 —— //
  handleInput(e) {
    this.setData({ inputValue: e.detail.value });
  },

  // —— 录音入口（待接） —— //
  onRecord() {
    console.log('TODO: 打开录音逻辑');
  },

  // —— 相机/相册 → 预览页 —— //
  onCamera() {
    // 你的路由可能是 /pages/preview/index；按实际调整
    tt.navigateTo({
      url: `/pages/preview/index?src=${encodeURIComponent('https://picsum.photos/600/800')}`
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
  handleSend(e) {
    if (this._sendingLock) return;

    // 兼容键盘回车：e.detail.value；按钮：this.data.inputValue
    const raw = (e && e.detail && typeof e.detail.value === 'string')
      ? e.detail.value
      : this.data.inputValue;

    // 规整空白与长度
    const text = (raw || '').replace(/\s+/g, ' ').trim();
    if (!text) return;
    const content = text.slice(0, 500); // 可调上限

    this._sendingLock = true;

    // 构造用户消息
    const now = new Date();
    const userMsg = {
      mid: genId('user'),
      role: 'user',
      type: 'text',
      content,
      time: formatTime(now),
      status: 'sent'
    };

    const next = this.data.messages.concat(userMsg);

    // 1) 加入列表 + 清空输入
    this.setData({ messages: next, inputValue: '' }, () => {
      // 2) 滚到底（处理“同值不触发”）
      this._scrollToBottom();

      // 3)（可选）加“AI 打字中”占位，然后去调后端
      this._pushTyping();

      // TODO: 在这里调用你的后端接口
      // 调用成功后用真实消息替换占位；下面用 setTimeout 模拟
      setTimeout(() => {
        this._replaceTypingWith({
          mid: genId('ai'),
          role: 'ai',
          type: 'text',
          content: '收到～我来帮你生成图，稍等。',
          time: formatTime()
        });

        // 再模拟返回一张图片消息（如果需要）
        setTimeout(() => {
          this.setData({
            showImageSender: true,
            presetImages: ['/static/images/test.jpg']
          }, () => {
            console.log('ImageSender state:', this.data.showImageSender, this.data.presetImages);
            const imageSender = this.selectComponent('#imageSender');
            if (imageSender) {
              console.log('ImageSender files:', imageSender.data.files);
            } else {
              console.error('ImageSender component not found');
            }
          });
        }, 500);
      }, 600);

      this._sendingLock = false;
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
  }

  
});
