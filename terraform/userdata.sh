#!/bin/bash
set -e

LOG="/var/log/userdata.log"
exec > >(tee -a $LOG) 2>&1

echo "=============================="
echo " APIDevOps - Setup iniciando  "
echo "=============================="

# ── 1. Actualizar sistema ──
apt-get update -y
apt-get install -y curl wget git ca-certificates gnupg lsb-release

# ── 2. Instalar Docker ──
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" \
  | tee /etc/apt/sources.list.d/docker.list > /dev/null
apt-get update -y
apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
systemctl enable docker
systemctl start docker
usermod -aG docker ubuntu

# ── 3. Crear docker-compose.yml ──
mkdir -p /home/ubuntu/app
cat > /home/ubuntu/app/docker-compose.yml << COMPOSE
services:

  api-stable:
    image: ${docker_image_stable}
    environment:
      - PORT=5000
    ports:
      - "5000:5000"
    restart: always
    mem_limit: 200m
    memswap_limit: 200m
    labels:
      - "track=stable"

  # Canary removed to avoid pushing canary image

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - /home/ubuntu/app/nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - api-stable
    restart: always
    mem_limit: 200m
    memswap_limit: 200m
COMPOSE

# ── 4. Crear nginx.conf con distribución 75% stable / 25% canary ──
cat > /home/ubuntu/app/nginx.conf << 'NGINX'
events {
    worker_connections 1024;
}

http {
    upstream api_backend {
      server api-stable:5000;   # Solo stable
    }

    server {
        listen 80;

        location / {
            proxy_pass http://api_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }
}
NGINX

chown -R ubuntu:ubuntu /home/ubuntu/app

# ── 5. Levantar los contenedores ──
cd /home/ubuntu/app
docker compose pull
docker compose up -d

echo "=============================="
echo " Setup completado ✅           "
echo "=============================="
