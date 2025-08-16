# MoodCanvas 部署指南

## 部署方式

### 1. Docker部署（推荐）

#### 创建Dockerfile
```dockerfile
FROM python:3.12-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# 复制项目文件
COPY requirements.txt .
COPY src/ ./src/
COPY config/ ./config/
COPY scripts/ ./scripts/

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 创建数据目录
RUN mkdir -p data/{models,input,output,temp,generated_images}

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 构建和运行
```bash
# 构建镜像
docker build -t moodcanvas .

# 运行容器
docker run -d \
  --name moodcanvas \
  -p 8000:8000 \
  -e ARK_API_KEY=your_api_key \
  -v $(pwd)/data:/app/data \
  moodcanvas
```

### 2. 传统部署

#### 环境准备
```bash
# 安装Python 3.12+
sudo apt update
sudo apt install python3.12 python3.12-venv python3.12-pip

# 创建项目目录
mkdir /opt/moodcanvas
cd /opt/moodcanvas
```

#### 代码部署
```bash
# 克隆代码
git clone https://github.com/your-repo/moodcanvas.git .

# 创建虚拟环境
python3.12 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

#### 服务配置
```bash
# 创建systemd服务文件
sudo nano /etc/systemd/system/moodcanvas.service
```

```ini
[Unit]
Description=MoodCanvas API Service
After=network.target

[Service]
Type=exec
User=moodcanvas
Group=moodcanvas
WorkingDirectory=/opt/moodcanvas
Environment=PATH=/opt/moodcanvas/venv/bin
Environment=ARK_API_KEY=your_api_key
ExecStart=/opt/moodcanvas/venv/bin/uvicorn src.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

#### 启动服务
```bash
# 重新加载systemd
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start moodcanvas

# 设置开机自启
sudo systemctl enable moodcanvas

# 查看状态
sudo systemctl status moodcanvas
```

### 3. 云服务部署

#### AWS EC2
```bash
# 连接到EC2实例
ssh -i your-key.pem ubuntu@your-ec2-ip

# 安装依赖
sudo apt update
sudo apt install python3.12 python3.12-venv nginx

# 部署代码
cd /opt
sudo git clone https://github.com/your-repo/moodcanvas.git
sudo chown -R ubuntu:ubuntu moodcanvas
cd moodcanvas

# 设置环境
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Nginx配置
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /opt/moodcanvas/data/generated_images/;
    }
}
```

## 环境配置

### 1. 环境变量
```bash
# 必需的环境变量
ARK_API_KEY=your_doubao_api_key

# 可选的环境变量
LOG_LEVEL=INFO
HOST=0.0.0.0
PORT=8000
DEBUG=false
```

### 2. 配置文件
确保`config/config.json`中的路径配置正确：
```json
{
  "paths": {
    "input_dir": "data/input",
    "output_dir": "data/output",
    "temp_dir": "data/temp",
<<<<<<< HEAD
    "models_cache": "./data/models",
=======
    "models_cache": "./src/data/models",
>>>>>>> 6c05c4473a1d189c5635a8fac8fd5c44011bd4e8
    "generated_images_dir": "data/generated_images"
  }
}
```

## 性能优化

### 1. 进程管理
```bash
# 使用gunicorn多进程
pip install gunicorn

# 启动命令
gunicorn src.main:app \
  -w 4 \
  -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 120 \
  --max-requests 1000
```

### 2. 反向代理
```nginx
# 启用gzip压缩
gzip on;
gzip_types text/plain text/css application/json application/javascript;

# 设置缓存
location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

## 监控和日志

### 1. 日志配置
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/moodcanvas.log'),
        logging.StreamHandler()
    ]
)
```

### 2. 健康检查
```bash
# 检查服务状态
curl http://localhost:8000/api/v1/health

# 检查系统资源
curl http://localhost:8000/api/v1/health/system

# 检查模型状态
curl http://localhost:8000/api/v1/health/models
```

## 安全配置

### 1. 防火墙设置
```bash
# 只开放必要端口
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw enable
```

### 2. SSL证书
```bash
# 使用Let's Encrypt
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## 备份和恢复

### 1. 数据备份
```bash
# 备份数据目录
tar -czf moodcanvas_backup_$(date +%Y%m%d).tar.gz data/

# 备份配置文件
cp config/config.json config_backup_$(date +%Y%m%d).json
```

### 2. 恢复数据
```bash
# 恢复数据
tar -xzf moodcanvas_backup_20240101.tar.gz

# 恢复配置
cp config_backup_20240101.json config/config.json
```

## 故障排除

### 1. 常见问题
- **端口被占用**: 检查端口使用情况 `netstat -tlnp | grep 8000`
- **权限问题**: 确保用户有读写权限 `sudo chown -R user:user /opt/moodcanvas`
- **依赖缺失**: 检查Python包安装 `pip list | grep fastapi`

### 2. 日志查看
```bash
# 查看应用日志
tail -f logs/moodcanvas.log

# 查看系统日志
sudo journalctl -u moodcanvas -f

# 查看Nginx日志
sudo tail -f /var/log/nginx/access.log
```

## 更新部署

### 1. 代码更新
```bash
# 拉取最新代码
git pull origin main

# 更新依赖
source venv/bin/activate
pip install -r requirements.txt

# 重启服务
sudo systemctl restart moodcanvas
```

### 2. 回滚策略
```bash
# 回滚到指定版本
git checkout <commit-hash>

# 重启服务
sudo systemctl restart moodcanvas
```
