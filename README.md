# Palworld Server Management Panel

一个基于 Python + FastAPI + Vue.js 的幻兽帕鲁服务器管理面板,运行在 Debian 12 / Ubuntu 上。

## 🎯 功能特性

- **服务器管理**: 启动、停止、保存服务器
- **玩家管理**: 查看在线玩家、踢出玩家、封禁玩家
- **RCON支持**: 通过RCON协议远程管理服务器
- **备份管理**: 创建、恢复、删除服务器备份
- **系统监控**: 实时监控CPU、内存、磁盘、网络使用情况
- **Web界面**: 现代化的Web管理界面,支持响应式设计

## 🛠️ 技术栈

### 后端
- Python 3.11+
- FastAPI - 高性能Web框架
- Uvicorn - ASGI服务器
- python-valve + rcon - RCON协议实现
- psutil - 系统监控

### 前端
- Vue 3 - 渐进式JavaScript框架
- Element Plus - Vue 3组件库
- Axios - HTTP客户端
- Vite - 构建工具

## 🚀 安装部署

### 系统要求

- Debian 12 / Ubuntu 22.04+
- Python 3.11+
- Node.js 18+ (仅用于前端构建)
- 幻兽帕鲁服务器 (可使用一键安装脚本)

### 完整部署流程

```
┌─────────────────────────────────────────────────────────┐
│ 步骤1: 安装帕鲁服务器                                    │
│   sudo ./scripts/install-palworld-server.sh             │
├─────────────────────────────────────────────────────────┤
│ 步骤2: 启动帕鲁服务器                                    │
│   sudo systemctl start palworld                         │
├─────────────────────────────────────────────────────────┤
│ 步骤3: 配置管理面板                                      │
│   cd backend && cp .env.example .env                    │
│   nano .env  # 设置RCON_PASSWORD等配置                   │
├─────────────────────────────────────────────────────────┤
│ 步骤4: 启动管理面板                                      │
│   sudo systemctl start palworld-panel                   │
├─────────────────────────────────────────────────────────┤
│ 步骤5: 访问面板                                         │
│   http://your-server-ip:8000                           │
└─────────────────────────────────────────────────────────┘
```

### 1. 帕鲁服务器一键安装

```bash
chmod +x scripts/install-palworld-server.sh
sudo ./scripts/install-palworld-server.sh
```

脚本功能:
- ✅ 自动更新系统和安装依赖
- ✅ 创建steam用户
- ✅ 使用SteamCMD下载服务器
- ✅ 配置RCON远程管理
- ✅ 创建systemd服务(开机自启)

### 2. 管理面板一键安装

```bash
chmod +x install.sh
sudo ./install.sh
```

脚本功能:
- ✅ 安装Python和Node.js依赖
- ✅ 复制文件到 `/opt/palworld-panel`
- ✅ 创建数据目录和备份目录
- ✅ 安装systemd服务(开机自启)

### 3. 手动安装(可选)

#### 3.1 后端安装

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
nano .env  # 配置服务器路径和RCON密码
```

#### 3.2 前端构建

```bash
cd frontend
npm install
npm run build
```

#### 3.3 系统服务部署

```bash
sudo cp systemd/palworld-panel.service /etc/systemd/system/
sudo nano /etc/systemd/system/palworld-panel.service  # 修改路径
sudo systemctl daemon-reload
sudo systemctl start palworld-panel
sudo systemctl enable palworld-panel
```

### 4. 前端构建

```bash
cd frontend
npm install
npm run build
```

## ⚙️ 配置说明

### 后端配置 (.env)

```env
# 应用配置
DEBUG=False
SECRET_KEY=your-secret-key-change-this-in-production

# 幻兽帕鲁服务器配置
PALWORLD_SERVER_DIR=/home/steam/palworld-server
PALWORLD_SERVER_EXECUTABLE=Pal/Binaries/Linux/PalServer-Linux-Shipping
PALWORLD_SAVE_DIR=Pal/Saved

# RCON配置 (默认端口 = 游戏端口 + 3)
RCON_HOST=127.0.0.1
RCON_PORT=8214
RCON_PASSWORD=your-admin-password

# 备份配置
BACKUP_DIR=/var/backups/palworld
MAX_BACKUPS=10

# 数据库配置
DATABASE_URL=sqlite+aiosqlite:///./data/palworld_panel.db
```

### RCON配置

确保帕鲁服务器已启用RCON。在服务器配置文件中添加:

```ini
[RCON]
Enabled=true
Port=8214
Password=your-admin-password
```

## 📡 API文档

启动后端服务后,访问以下地址查看API文档:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🔐 默认账户

- 用户名: **admin**
- 密码: **admin123**

**重要**: 首次登录后请立即修改密码!

## 📁 目录结构

```
palworld-panel/
├── backend/                 # Python后端
│   ├── app/
│   │   ├── api/            # API路由
│   │   ├── models/          # 数据模型
│   │   ├── services/        # 业务逻辑
│   │   ├── config.py        # 配置管理
│   │   └── main.py          # 主应用
│   ├── requirements.txt     # Python依赖
│   ├── .env                 # 环境变量
│   └── .env.example         # 环境变量示例
├── frontend/                # Vue前端
│   ├── src/
│   │   ├── api/            # API调用
│   │   ├── router/         # 路由配置
│   │   ├── views/          # 页面组件
│   │   ├── App.vue         # 根组件
│   │   └── main.js         # 入口文件
│   ├── package.json        # Node.js依赖
│   └── vite.config.js      # Vite配置
├── scripts/                 # 安装脚本
│   └── install-palworld-server.sh  # 帕鲁服务器一键安装
├── systemd/                 # 系统服务配置
│   ├── palworld-panel.service      # 面板服务
│   └── palworld.service            # 服务器服务(由脚本创建)
└── README.md               # 说明文档
```

## 🔧 常用命令

### 帕鲁服务器
```bash
sudo systemctl start palworld    # 启动服务器
sudo systemctl stop palworld     # 停止服务器
sudo systemctl status palworld   # 查看状态
sudo journalctl -u palworld -f   # 查看日志
```

### 管理面板
```bash
sudo systemctl start palworld-panel    # 启动面板
sudo systemctl stop palworld-panel     # 停止面板
sudo systemctl status palworld-panel   # 查看状态
```

## ❓ 常见问题

### 1. RCON连接失败
- 检查RCON是否在服务器配置中启用
- 确认RCON端口和密码配置正确(默认端口=游戏端口+3)
- 检查防火墙是否允许RCON端口

### 2. 无法启动服务器
- 确认服务器可执行文件路径正确
- 检查文件权限
- 查看后端日志获取详细错误信息

### 3. 备份失败
- 确认备份目录有写入权限
- 检查磁盘空间是否充足
- 确认服务器存档目录路径正确

### 4. 服务启动失败(权限问题)
```bash
sudo mkdir -p /var/backups/palworld
sudo chown your-user:your-user /var/backups/palworld
```

## 📋 开发计划

- [ ] 支持多服务器管理
- [ ] 添加服务器日志查看功能
- [ ] 实现定时自动备份
- [ ] 添加玩家白名单管理
- [ ] 支持服务器配置文件编辑
- [ ] 添加性能图表展示
- [ ] 实现WebSocket实时通信

## 📜 许可证

MIT License

## 🤝 贡献

欢迎提交Issue和Pull Request!