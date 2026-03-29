#!/bin/bash
# ===========================================
# Setup do Servidor - DigitalOcean Droplet
# Workshop AIOX Produto Digital
# ===========================================

set -e

echo "=== Setup do Servidor CRM Produto Digital ==="
echo ""

# 1. Atualizar sistema
echo "[1/7] Atualizando sistema..."
apt update && apt upgrade -y

# 2. Instalar dependencias
echo "[2/7] Instalando dependencias..."
apt install -y python3 python3-pip python3-venv nginx certbot python3-certbot-nginx git curl

# 3. Instalar Node.js (para AIOX)
echo "[3/7] Instalando Node.js..."
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt install -y nodejs

# 4. Criar diretorio do projeto
echo "[4/7] Configurando projeto..."
mkdir -p /opt/meu-crm
cd /opt/meu-crm

# 5. Criar virtual environment
echo "[5/7] Criando ambiente Python..."
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip

# 6. Criar servico systemd
echo "[6/7] Criando servico systemd..."
cat > /etc/systemd/system/meu-crm.service << 'EOF'
[Unit]
Description=CRM Produto Digital
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/meu-crm
Environment=PATH=/opt/meu-crm/venv/bin:/usr/local/bin:/usr/bin
ExecStart=/opt/meu-crm/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable meu-crm

# 7. Configurar Nginx
echo "[7/7] Configurando Nginx..."
cat > /etc/nginx/sites-available/meu-crm << 'EOF'
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_cache_bypass $http_upgrade;
    }
}
EOF

ln -sf /etc/nginx/sites-available/meu-crm /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl reload nginx

echo ""
echo "=== Setup completo! ==="
echo ""
echo "Proximos passos:"
echo "  1. Clone seu repo em /opt/meu-crm/"
echo "  2. Copie .env.example para .env e configure"
echo "  3. pip install -r requirements.txt"
echo "  4. systemctl start meu-crm"
echo "  5. Acesse http://SEU_IP"
echo ""
echo "Para SSL: certbot --nginx -d seudominio.com"
