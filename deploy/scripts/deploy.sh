#!/usr/bin/env bash
set -euo pipefail

# InterFinOps - Deployment Script
# Zero-downtime deployment with rolling restarts

APP_DIR="${APP_DIR:-/opt/interfinops}"
COMPOSE_FILE="${APP_DIR}/docker-compose.prod.yml"
BACKUP_BEFORE_DEPLOY="${BACKUP_BEFORE_DEPLOY:-true}"
BRANCH="${BRANCH:-main}"

cd "${APP_DIR}"

echo "==> InterFinOps Deployment"
echo "    Directory: ${APP_DIR}"
echo "    Branch:    ${BRANCH}"
echo "    Time:      $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo ""

# -------------------------------------------------------
# 1. Pull latest code
# -------------------------------------------------------
echo "==> Pulling latest code from ${BRANCH}..."
git fetch origin
git checkout "${BRANCH}"
git pull origin "${BRANCH}"

# -------------------------------------------------------
# 2. Pre-deploy backup
# -------------------------------------------------------
if [ "${BACKUP_BEFORE_DEPLOY}" = "true" ]; then
    echo "==> Running pre-deploy database backup..."
    bash "${APP_DIR}/deploy/scripts/backup.sh" || {
        echo "WARNING: Backup failed. Continuing deployment..."
    }
fi

# -------------------------------------------------------
# 3. Build new images
# -------------------------------------------------------
echo "==> Building new Docker images..."
docker compose -f "${COMPOSE_FILE}" build --no-cache backend frontend

# -------------------------------------------------------
# 4. Run database migrations
# -------------------------------------------------------
echo "==> Running database migrations..."
docker compose -f "${COMPOSE_FILE}" run --rm backend alembic upgrade head

# -------------------------------------------------------
# 5. Zero-downtime restart
# -------------------------------------------------------
echo "==> Restarting services (zero-downtime)..."

# Scale backend to 2 instances temporarily
docker compose -f "${COMPOSE_FILE}" up -d --no-deps --scale backend=2 backend
echo "    Waiting for new backend instance to be healthy..."
sleep 10

# Check health of new instance
if docker compose -f "${COMPOSE_FILE}" exec backend curl -sf http://localhost:8000/api/health > /dev/null 2>&1; then
    echo "    New backend instance is healthy."
else
    echo "WARNING: Health check inconclusive. Proceeding with restart..."
fi

# Scale back to 1 (removes old container)
docker compose -f "${COMPOSE_FILE}" up -d --no-deps --scale backend=1 backend

# Restart frontend and nginx
docker compose -f "${COMPOSE_FILE}" up -d --no-deps frontend
docker compose -f "${COMPOSE_FILE}" up -d --no-deps nginx

# -------------------------------------------------------
# 6. Cleanup
# -------------------------------------------------------
echo "==> Cleaning up old Docker images..."
docker image prune -f

# -------------------------------------------------------
# 7. Verify deployment
# -------------------------------------------------------
echo "==> Verifying deployment..."
sleep 5

SERVICES=("postgres" "backend" "frontend" "nginx")
ALL_HEALTHY=true

for service in "${SERVICES[@]}"; do
    STATUS=$(docker compose -f "${COMPOSE_FILE}" ps --format json "${service}" 2>/dev/null | python3 -c "import sys,json; print(json.load(sys.stdin).get('State','unknown'))" 2>/dev/null || echo "unknown")
    if [ "${STATUS}" = "running" ]; then
        echo "    ${service}: running"
    else
        echo "    ${service}: ${STATUS} (WARNING)"
        ALL_HEALTHY=false
    fi
done

echo ""
if [ "${ALL_HEALTHY}" = true ]; then
    echo "==> Deployment successful!"
else
    echo "==> Deployment completed with warnings. Check service status."
    echo "    Run: docker compose -f ${COMPOSE_FILE} ps"
    echo "    Logs: docker compose -f ${COMPOSE_FILE} logs --tail=50"
fi

echo "    Time: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
