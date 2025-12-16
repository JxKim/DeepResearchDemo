#!/bin/bash

# 获取脚本所在目录的上级目录（backend）
BACKEND_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"
ENV_FILE="$BACKEND_DIR/.env"

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# 检查 .env 是否存在
if [ ! -f "$ENV_FILE" ]; then
    log_error "配置文件 .env 未找到: $ENV_FILE"
    exit 1
fi

# 从 .env 文件加载环境变量
# 使用 set -a 和 source 自动导出变量
set -a
source "$ENV_FILE"
set +a

check_port_occupied() {
    local port=$1
    if ss -tuln | grep -q ":$port "; then
        return 0
    else
        return 1
    fi
}

# --- 数据目录配置 ---
DB_DATA_DIR="$BACKEND_DIR/db/data"
mkdir -p "$DB_DATA_DIR"

# PostgreSQL 数据目录
PG_DATA_DIR="$DB_DATA_DIR/postgres"
mkdir -p "$PG_DATA_DIR"

# Milvus 数据目录
MILVUS_DATA_DIR="$DB_DATA_DIR/milvus"
mkdir -p "$MILVUS_DATA_DIR"

# --- PostgreSQL 配置 ---
# 直接使用 .env 中的变量
PG_HOST=${POSTGRES_HOST:-localhost}
PG_PORT=${POSTGRES_PORT:-5432}
PG_USER=${POSTGRES_USER:-postgres}
PG_PASS=${POSTGRES_PASSWORD}
PG_DB=${POSTGRES_DB:-postgres}

# 如果 localhost，则尝试启动 Docker
if [ "$PG_HOST" == "localhost" ] || [ "$PG_HOST" == "127.0.0.1" ]; then
    CONTAINER_NAME="smartagent_postgres"
    
    if check_port_occupied "$PG_PORT"; then
        log_info "PostgreSQL 端口 $PG_PORT 已被占用，跳过启动."
    else
        log_info "正在检查 PostgreSQL 容器 ($CONTAINER_NAME)..."
        
        if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
            if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
                 log_info "PostgreSQL 容器正在运行."
            else
                 log_info "启动现有的 PostgreSQL 容器..."
                 docker start $CONTAINER_NAME
            fi
        else
            log_info "创建并启动新的 PostgreSQL 容器..."
            # 默认使用 postgres:15
            # 挂载数据目录
            docker run -d \
                --name $CONTAINER_NAME \
                -p $PG_PORT:5432 \
                -e POSTGRES_USER=$PG_USER \
                -e POSTGRES_PASSWORD=$PG_PASS \
                -e POSTGRES_DB=$PG_DB \
                -v "$PG_DATA_DIR:/var/lib/postgresql/data" \
                postgres:15
        fi
    fi
else
    log_info "PostgreSQL 配置为远程主机 ($PG_HOST)，跳过本地 Docker 启动."
fi


# --- Milvus 配置 ---
# 使用同目录下的 standalone_embed.sh 启动 Milvus
# 该脚本封装了 Milvus Standalone (Embedded Etcd) 的 docker run 逻辑

# 从 .env 读取 MILVUS_URI
MILVUS_URI=${MILVUS_URI:-http://localhost:19530}
# 提取端口，例如 http://localhost:19530 -> 19530
MILVUS_PORT=$(echo $MILVUS_URI | sed -e 's/.*:\([0-9]*\).*/\1/')

if [[ "$MILVUS_URI" == *"localhost"* ]] || [[ "$MILVUS_URI" == *"127.0.0.1"* ]]; then
    
    if check_port_occupied "$MILVUS_PORT"; then
         log_info "Milvus 端口 $MILVUS_PORT 已被占用，跳过启动."
    else
        # 检查 standalone_embed.sh 是否存在
        MILVUS_SCRIPT="$BACKEND_DIR/db/standalone_embed.sh"
        
        if [ ! -f "$MILVUS_SCRIPT" ]; then
            log_error "Milvus 启动脚本未找到: $MILVUS_SCRIPT"
            # 尝试在当前目录查找 (如果在 db 目录下运行)
            if [ -f "./standalone_embed.sh" ]; then
                 MILVUS_SCRIPT="./standalone_embed.sh"
            else
                 log_warn "尝试跳过 Milvus 自动启动..."
            fi
        fi

        if [ -f "$MILVUS_SCRIPT" ]; then
            log_info "正在启动 Milvus (使用 $MILVUS_SCRIPT)..."
            
            # 确保脚本有执行权限
            chmod +x "$MILVUS_SCRIPT"
            
            # 切换到脚本所在目录执行，因为脚本内部使用了相对路径 $(pwd) 来挂载 volume
            # 使用子 shell 避免影响当前脚本的工作目录
            # 我们需要传递自定义的数据目录给 standalone_embed.sh，或者修改 standalone_embed.sh
            # 由于 standalone_embed.sh 是第三方脚本或固定脚本，我们这里通过环境变量传递 VOLUME_DIR 给它 (如果它支持)
            # 或者我们临时修改它的行为。
            # 查看之前的 standalone_embed.sh 内容，它使用 $(pwd)/volumes/milvus
            # 我们可以创建一个软链接，或者修改 standalone_embed.sh。
            # 为了不修改 standalone_embed.sh (方便升级)，我们在执行前，
            # 在脚本所在目录创建一个指向我们需要的数据目录的软链接 "volumes"
            
            (
                cd "$(dirname "$MILVUS_SCRIPT")"
                
                # 创建 volumes 目录的软链接，指向我们的 MILVUS_DATA_DIR
                # standalone_embed.sh 使用 $(pwd)/volumes/milvus
                # 所以我们需要让 $(pwd)/volumes 指向 MILVUS_DATA_DIR 的上级或者直接处理
                
                # 方案：
                # standalone_embed.sh 期望: ./volumes/milvus
                # 我们希望存储在: $MILVUS_DATA_DIR (例如 backend/db/data/milvus)
                
                # 1. 备份原有的 volumes 目录 (如果存在且不是软链接)
                if [ -d "volumes" ] && [ ! -L "volumes" ]; then
                    log_warn "发现现有的 volumes 目录，将其重命名为 volumes_backup..."
                    mv volumes volumes_backup_$(date +%Y%m%d%H%M%S)
                fi
                
                # 2. 创建指向 $MILVUS_DATA_DIR 父目录的链接，或者直接链接
                # standalone_embed.sh 写死的是 -v $(pwd)/volumes/milvus:/var/lib/milvus
                # 所以我们需要 ./volumes/milvus 对应到 $MILVUS_DATA_DIR
                
                # 确保 ./volumes 存在
                mkdir -p volumes
                
                # 如果 ./volumes/milvus 已经存在且不是链接到我们的目标，则处理
                # 这里为了简单，我们直接把 $MILVUS_DATA_DIR 作为 ./volumes/milvus 的挂载点
                # 但是 docker -v 宿主机路径必须存在。
                
                # 更简单的做法：
                # 修改 standalone_embed.sh 调用方式不太容易，因为它是硬编码的。
                # 我们可以临时设置一个环境变量，如果 standalone_embed.sh 不支持，我们就得修改 standalone_embed.sh
                # 让我们先检查 standalone_embed.sh 是否支持自定义目录。
                # 之前读取的内容显示： -v $(pwd)/volumes/milvus:/var/lib/milvus
                # 它是硬编码的。
                
                # 所以我们采用软链接方案：
                # 让 $(pwd)/volumes/milvus 成为指向 $MILVUS_DATA_DIR 的软链接
                
                mkdir -p volumes
                if [ -d "volumes/milvus" ] && [ ! -L "volumes/milvus" ]; then
                     # 如果是普通目录，说明之前运行过，数据在里面。
                     # 我们应该把数据移动到新位置，然后建立链接
                     log_info "迁移旧的 Milvus 数据到新目录 $MILVUS_DATA_DIR..."
                     cp -r volumes/milvus/* "$MILVUS_DATA_DIR/" 2>/dev/null || true
                     rm -rf volumes/milvus
                fi
                
                if [ ! -L "volumes/milvus" ]; then
                    ln -s "$MILVUS_DATA_DIR" "volumes/milvus"
                fi

                # 注意：standalone_embed.sh 内部使用了 sudo，如果用户非 root 且无 sudo 权限可能会失败
                # 如果当前已经是 root 或者有免密 sudo，则没问题
                # 这里直接调用 bash 运行
                bash standalone_embed.sh start
            )
            
            if [ $? -eq 0 ]; then
                 log_info "Milvus 启动命令执行成功."
            else
                 log_error "Milvus 启动命令执行失败."
            fi
        fi
    fi
else
    log_info "Milvus 配置为远程 URI ($MILVUS_URI)，跳过本地 Docker 启动."
fi

# --- 端口检测 ---
log_info "等待几秒钟让服务启动..."
sleep 5

log_info "--- 端口占用检测 ---"
check_port() {
    local port=$1
    local name=$2
    if ss -tuln | grep -q ":$port "; then
        log_info "端口 $port ($name) 正在被占用 (服务已启动)."
    else
        log_warn "端口 $port ($name) 未被占用 (可能启动失败或还在启动中)."
    fi
}

check_port "$PG_PORT" "PostgreSQL"
check_port "$MILVUS_PORT" "Milvus"

log_info "数据库服务启动脚本执行完成."
