#!/bin/bash

set -e

echo "=== 幻兽帕鲁服务器一键安装脚本 ==="
echo "自动安装最新版本"
echo ""

if [ "$EUID" -ne 0 ]; then
    echo "错误: 请使用root用户运行此脚本"
    exit 1
fi

read -p "请输入服务器密码 (留空则不设置): " SERVER_PASSWORD
read -p "请输入管理员密码: " ADMIN_PASSWORD
read -p "请输入最大玩家数 (默认32): " MAX_PLAYERS
read -p "请输入服务器端口 (默认8211): " SERVER_PORT

SERVER_PASSWORD=${SERVER_PASSWORD:-""}
MAX_PLAYERS=${MAX_PLAYERS:-32}
SERVER_PORT=${SERVER_PORT:-8211}
RCON_PORT=$((SERVER_PORT + 3))

echo ""
echo "安装配置:"
echo "  - 服务器密码: ${SERVER_PASSWORD:-(无密码)}"
echo "  - 管理员密码: $ADMIN_PASSWORD"
echo "  - 最大玩家数: $MAX_PLAYERS"
echo "  - 服务器端口: $SERVER_PORT"
echo "  - RCON端口: $RCON_PORT"
echo ""

read -p "确认安装? (y/N): " CONFIRM
if [[ ! "$CONFIRM" =~ ^[Yy]$ ]]; then
    echo "已取消安装"
    exit 0
fi

echo ""
echo "=== 步骤1: 更新系统 ==="
apt update && apt upgrade -y

echo ""
echo "=== 步骤2: 安装依赖 ==="
apt install -y steamcmd lib32gcc-s1 screen

echo ""
echo "=== 步骤3: 创建steam用户 ==="
if ! id "steam" &>/dev/null; then
    useradd -m steam
fi

echo ""
echo "=== 步骤4: 下载帕鲁服务器 ==="
su - steam -c "mkdir -p ~/palworld-server"
su - steam -c "steamcmd +force_install_dir ~/palworld-server +login anonymous +app_update 2394010 validate +quit"

echo ""
echo "=== 步骤5: 创建启动脚本 ==="
cat > /home/steam/palworld-server/start.sh <<EOF
#!/bin/bash
cd /home/steam/palworld-server
./Pal/Binaries/Linux/PalServer-Linux-Shipping \
    -port=$SERVER_PORT \
    -players=$MAX_PLAYERS \
    -servername="My Palworld Server" \
    -serverpassword="$SERVER_PASSWORD" \
    -adminpassword="$ADMIN_PASSWORD" \
    -rconenabled=true \
    -rconport=$RCON_PORT \
    -rconpassword="$ADMIN_PASSWORD"
EOF

chmod +x /home/steam/palworld-server/start.sh
chown steam:steam /home/steam/palworld-server/start.sh

echo ""
echo "=== 步骤6: 创建配置文件 ==="
mkdir -p /home/steam/palworld-server/Pal/Saved/Config/LinuxServer

cat > /home/steam/palworld-server/Pal/Saved/Config/LinuxServer/PalWorldSettings.ini <<EOF
[/Script/Pal.PalGameWorldSettings]
OptionSettings=(Difficulty=None,DayTimeSpeedRate=1.000000,NightTimeSpeedRate=1.000000,ExpRate=1.000000,PalCaptureRate=1.000000,PalSpawnNumRate=1.000000,PalDamageRateAttack=1.000000,PalDamageRateDefense=1.000000,PlayerDamageRateAttack=1.000000,PlayerDamageRateDefense=1.000000,PlayerStomachDecreaceRate=1.000000,PlayerStaminaDecreaceRate=1.000000,PlayerAutoHPRegeneRate=1.000000,PlayerAutoHPRegeneRateInSleep=1.000000,PalStomachDecreaceRate=1.000000,PalStaminaDecreaceRate=1.000000,PalAutoHPRegeneRate=1.000000,PalAutoHPRegeneRateInSleep=1.000000,BuildObjectDamageRate=1.000000,BuildObjectDeteriorationDamageRate=1.000000,CollectionDropRate=1.000000,CollectionObjectHpRate=1.000000,CollectionObjectRespawnSpeedRate=1.000000,EnemyDropRate=1.000000,DeathPenalty=All,BanListURL="https://api.palworldgame.com/api/banlist.txt")

[RCON]
Enabled=true
Port=$RCON_PORT
Password=$ADMIN_PASSWORD
EOF

chown -R steam:steam /home/steam/palworld-server/Pal/Saved

echo ""
echo "=== 步骤7: 创建systemd服务 ==="
cat > /etc/systemd/system/palworld.service <<EOF
[Unit]
Description=Palworld Dedicated Server
After=network.target

[Service]
User=steam
WorkingDirectory=/home/steam/palworld-server
ExecStart=/usr/bin/screen -DmS palworld ./start.sh
ExecStop=/usr/bin/screen -S palworld -X quit
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable palworld

echo ""
echo "=== 安装完成 ==="
echo ""
echo "服务器信息:"
echo "  - 服务器目录: /home/steam/palworld-server"
echo "  - 存档目录: /home/steam/palworld-server/Pal/Saved"
echo "  - 服务器端口: $SERVER_PORT"
echo "  - RCON端口: $RCON_PORT"
echo "  - 管理员密码: $ADMIN_PASSWORD"
echo ""
echo "常用命令:"
echo "  启动服务器: sudo systemctl start palworld"
echo "  停止服务器: sudo systemctl stop palworld"
echo "  查看状态: sudo systemctl status palworld"
echo "  查看日志: sudo journalctl -u palworld -f"
echo "  连接控制台: screen -r palworld (按 Ctrl+A+D 退出)"
echo ""
echo "请确保防火墙开放端口:"
echo "  sudo ufw allow $SERVER_PORT/tcp"
echo "  sudo ufw allow $RCON_PORT/tcp"
echo "  sudo ufw reload"