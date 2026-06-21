#!/bin/bash

echo "=== 幻兽帕鲁服务器管理面板安装脚本 ==="

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then
    echo "请使用root用户运行此脚本"
    exit 1
fi

# 安装系统依赖
echo "正在安装系统依赖..."
apt-get update
apt-get install -y python3 python3-pip python3-venv nodejs npm

# 创建安装目录
INSTALL_DIR="/opt/palworld-panel"
echo "创建安装目录: $INSTALL_DIR"
mkdir -p $INSTALL_DIR

# 复制文件
echo "正在复制文件..."
cp -r backend $INSTALL_DIR/
cp -r frontend/dist $INSTALL_DIR/frontend

# 安装Python依赖
echo "正在安装Python依赖..."
cd $INSTALL_DIR/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 创建数据目录
mkdir -p $INSTALL_DIR/backend/data
mkdir -p /var/backups/palworld

# 创建环境变量文件
if [ ! -f "$INSTALL_DIR/backend/.env" ]; then
    echo "创建配置文件..."
    cp $INSTALL_DIR/backend/.env.example $INSTALL_DIR/backend/.env
    echo "请编辑 $INSTALL_DIR/backend/.env 配置服务器路径和RCON密码"
fi

# 安装systemd服务
echo "正在安装systemd服务..."
cp systemd/palworld-panel.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable palworld-panel

echo ""
echo "=== 安装完成 ==="
echo ""
echo "下一步操作:"
echo "1. 编辑配置文件: nano $INSTALL_DIR/backend/.env"
echo "2. 启动服务: systemctl start palworld-panel"
echo "3. 查看状态: systemctl status palworld-panel"
echo "4. 访问面板: http://your-server-ip:8000"
echo ""
echo "默认账户: admin / admin123"
echo "请登录后立即修改密码!"