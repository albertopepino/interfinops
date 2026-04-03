#!/usr/bin/env bash
set -euo pipefail

# InterFinOps - Hetzner VPS Setup Script
# Run as root on a fresh Ubuntu 22.04+ server

DEPLOY_USER="deploy"
SSH_PORT="${SSH_PORT:-2222}"
DOMAIN="${DOMAIN_NAME:?Set DOMAIN_NAME environment variable}"

echo "==> InterFinOps Server Setup"
echo "    Domain: ${DOMAIN}"
echo "    SSH Port: ${SSH_PORT}"
echo ""

# -------------------------------------------------------
# 1. System updates
# -------------------------------------------------------
echo "==> Updating system packages..."
apt-get update && apt-get upgrade -y
apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    software-properties-common \
    ufw \
    fail2ban \
    unattended-upgrades

# -------------------------------------------------------
# 2. Create non-root deploy user
# -------------------------------------------------------
echo "==> Creating deploy user..."
if ! id "${DEPLOY_USER}" &>/dev/null; then
    adduser --disabled-password --gecos "Deploy User" "${DEPLOY_USER}"
    usermod -aG sudo "${DEPLOY_USER}"
    mkdir -p /home/${DEPLOY_USER}/.ssh
    cp /root/.ssh/authorized_keys /home/${DEPLOY_USER}/.ssh/authorized_keys 2>/dev/null || true
    chown -R ${DEPLOY_USER}:${DEPLOY_USER} /home/${DEPLOY_USER}/.ssh
    chmod 700 /home/${DEPLOY_USER}/.ssh
    chmod 600 /home/${DEPLOY_USER}/.ssh/authorized_keys 2>/dev/null || true
    echo "${DEPLOY_USER} ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/${DEPLOY_USER}
    chmod 440 /etc/sudoers.d/${DEPLOY_USER}
fi

# -------------------------------------------------------
# 3. Configure SSH
# -------------------------------------------------------
echo "==> Configuring SSH on port ${SSH_PORT}..."
sed -i "s/^#\?Port .*/Port ${SSH_PORT}/" /etc/ssh/sshd_config
sed -i "s/^#\?PermitRootLogin .*/PermitRootLogin no/" /etc/ssh/sshd_config
sed -i "s/^#\?PasswordAuthentication .*/PasswordAuthentication no/" /etc/ssh/sshd_config
sed -i "s/^#\?PubkeyAuthentication .*/PubkeyAuthentication yes/" /etc/ssh/sshd_config
systemctl restart sshd

# -------------------------------------------------------
# 4. Configure UFW firewall
# -------------------------------------------------------
echo "==> Configuring UFW firewall..."
ufw default deny incoming
ufw default allow outgoing
ufw allow ${SSH_PORT}/tcp comment "SSH"
ufw allow 80/tcp comment "HTTP"
ufw allow 443/tcp comment "HTTPS"
ufw --force enable

# -------------------------------------------------------
# 5. Configure fail2ban
# -------------------------------------------------------
echo "==> Configuring fail2ban..."
cat > /etc/fail2ban/jail.local <<JAILEOF
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5
backend = systemd

[sshd]
enabled = true
port = ${SSH_PORT}
filter = sshd
logpath = /var/log/auth.log
maxretry = 3
bantime = 86400
JAILEOF

systemctl enable fail2ban
systemctl restart fail2ban

# -------------------------------------------------------
# 6. Install Docker
# -------------------------------------------------------
echo "==> Installing Docker..."
if ! command -v docker &>/dev/null; then
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" \
        > /etc/apt/sources.list.d/docker.list
    apt-get update
    apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
fi

usermod -aG docker ${DEPLOY_USER}
systemctl enable docker
systemctl start docker

# -------------------------------------------------------
# 7. Install Certbot for Let's Encrypt
# -------------------------------------------------------
echo "==> Installing Certbot..."
apt-get install -y certbot

# Create webroot directory for ACME challenges
mkdir -p /var/www/certbot

# Obtain SSL certificate
echo "==> Obtaining SSL certificate for ${DOMAIN}..."
certbot certonly \
    --standalone \
    --non-interactive \
    --agree-tos \
    --email "admin@${DOMAIN}" \
    --domain "${DOMAIN}" \
    -d "www.${DOMAIN}" \
    || echo "WARNING: Certbot failed. Ensure DNS is pointed to this server and run certbot manually."

# Setup auto-renewal cron
cat > /etc/cron.d/certbot-renew <<CRONEOF
0 3 * * * root certbot renew --quiet --deploy-hook "docker restart interfinops-nginx" >> /var/log/certbot-renew.log 2>&1
CRONEOF

# -------------------------------------------------------
# 8. Create application directories
# -------------------------------------------------------
echo "==> Creating application directories..."
APP_DIR="/opt/interfinops"
mkdir -p ${APP_DIR}
mkdir -p ${APP_DIR}/backups
mkdir -p ${APP_DIR}/logs
mkdir -p /var/www/certbot

chown -R ${DEPLOY_USER}:${DEPLOY_USER} ${APP_DIR}

# -------------------------------------------------------
# 9. Enable automatic security updates
# -------------------------------------------------------
echo "==> Enabling unattended upgrades..."
cat > /etc/apt/apt.conf.d/20auto-upgrades <<APTEOF
APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Unattended-Upgrade "1";
APT::Periodic::AutocleanInterval "7";
APTEOF

# -------------------------------------------------------
# Done
# -------------------------------------------------------
echo ""
echo "========================================"
echo "  Server setup complete!"
echo "========================================"
echo ""
echo "  SSH port:    ${SSH_PORT}"
echo "  Deploy user: ${DEPLOY_USER}"
echo "  App dir:     ${APP_DIR}"
echo "  Domain:      ${DOMAIN}"
echo ""
echo "  Next steps:"
echo "  1. Test SSH: ssh -p ${SSH_PORT} ${DEPLOY_USER}@<server-ip>"
echo "  2. Clone repo to ${APP_DIR}"
echo "  3. Copy .env file to ${APP_DIR}/.env"
echo "  4. Run: cd ${APP_DIR} && docker compose -f docker-compose.prod.yml up -d"
echo ""
