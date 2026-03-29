#!/bin/bash
# ===========================================
# Deploy Script - Atualizar servidor
# Workshop AIOX Produto Digital
# ===========================================

set -e

SERVER_IP=${1:-"SEU_IP_AQUI"}
SSH_KEY="~/.ssh/id_ed25519"
PROJECT_DIR="/opt/meu-crm"

echo "=== Deploy para $SERVER_IP ==="

# 1. Sync arquivos
echo "[1/3] Sincronizando arquivos..."
rsync -avz --exclude='venv' --exclude='__pycache__' --exclude='.env' --exclude='node_modules' \
  -e "ssh -i $SSH_KEY" \
  ./ root@$SERVER_IP:$PROJECT_DIR/

# 2. Instalar dependencias novas
echo "[2/3] Instalando dependencias..."
ssh -i $SSH_KEY root@$SERVER_IP "cd $PROJECT_DIR && source venv/bin/activate && pip install -r requirements.txt -q"

# 3. Reiniciar servico
echo "[3/3] Reiniciando servico..."
ssh -i $SSH_KEY root@$SERVER_IP "systemctl restart meu-crm && sleep 2 && systemctl is-active meu-crm"

echo ""
echo "=== Deploy completo! ==="
echo "Acesse: http://$SERVER_IP"
