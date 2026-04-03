#!/usr/bin/env bash
set -euo pipefail

# InterFinOps - PostgreSQL Backup Script
# Creates compressed backups and retains the last 30 days

APP_DIR="${APP_DIR:-/opt/interfinops}"
BACKUP_DIR="${BACKUP_DIR:-${APP_DIR}/backups}"
RETENTION_DAYS=30
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
COMPOSE_FILE="${APP_DIR}/docker-compose.prod.yml"

# Load environment variables
if [ -f "${APP_DIR}/.env" ]; then
    set -a
    source "${APP_DIR}/.env"
    set +a
fi

DB_NAME="${POSTGRES_DB:-interfinops}"
DB_USER="${POSTGRES_USER:-interfinops}"
BACKUP_FILE="${BACKUP_DIR}/${DB_NAME}_${TIMESTAMP}.sql.gz"

echo "==> InterFinOps Database Backup"
echo "    Database: ${DB_NAME}"
echo "    Target:   ${BACKUP_FILE}"
echo "    Time:     $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo ""

# Ensure backup directory exists
mkdir -p "${BACKUP_DIR}"

# -------------------------------------------------------
# 1. Create backup
# -------------------------------------------------------
echo "==> Creating database backup..."
docker compose -f "${COMPOSE_FILE}" exec -T postgres \
    pg_dump -U "${DB_USER}" -d "${DB_NAME}" --no-owner --no-privileges \
    | gzip > "${BACKUP_FILE}"

# Verify backup was created and is not empty
if [ ! -s "${BACKUP_FILE}" ]; then
    echo "ERROR: Backup file is empty or was not created."
    rm -f "${BACKUP_FILE}"
    exit 1
fi

BACKUP_SIZE=$(du -h "${BACKUP_FILE}" | cut -f1)
echo "    Backup created: ${BACKUP_FILE} (${BACKUP_SIZE})"

# -------------------------------------------------------
# 2. Remove old backups
# -------------------------------------------------------
echo "==> Cleaning up backups older than ${RETENTION_DAYS} days..."
DELETED_COUNT=0
while IFS= read -r old_backup; do
    rm -f "${old_backup}"
    DELETED_COUNT=$((DELETED_COUNT + 1))
done < <(find "${BACKUP_DIR}" -name "${DB_NAME}_*.sql.gz" -type f -mtime +${RETENTION_DAYS} 2>/dev/null)

if [ ${DELETED_COUNT} -gt 0 ]; then
    echo "    Removed ${DELETED_COUNT} old backup(s)."
else
    echo "    No old backups to remove."
fi

# -------------------------------------------------------
# 3. Summary
# -------------------------------------------------------
TOTAL_BACKUPS=$(find "${BACKUP_DIR}" -name "${DB_NAME}_*.sql.gz" -type f | wc -l)
TOTAL_SIZE=$(du -sh "${BACKUP_DIR}" | cut -f1)

echo ""
echo "==> Backup complete"
echo "    Total backups: ${TOTAL_BACKUPS}"
echo "    Total size:    ${TOTAL_SIZE}"
echo "    Retention:     ${RETENTION_DAYS} days"
