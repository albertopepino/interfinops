# InterFinOps

International financial operations platform for managing multi-currency invoicing, expense tracking, and financial reporting across borders.

## Tech Stack

- **Backend:** Python 3.12, FastAPI, SQLAlchemy, Alembic, PostgreSQL 16
- **Frontend:** React, TypeScript, Vite, Tailwind CSS
- **Infrastructure:** Docker, Nginx, Let's Encrypt SSL

## Quick Start

1. Copy the environment template and fill in your values:

```bash
cp .env.example .env
```

2. Start all services:

```bash
docker compose up -d
```

3. Access the application:
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API docs: http://localhost:8000/docs

## Production Deployment

See `deploy/scripts/setup-server.sh` for initial server provisioning, then use `deploy/scripts/deploy.sh` for deployments. Backups are handled by `deploy/scripts/backup.sh`.

```bash
# First-time server setup (run as root)
DOMAIN_NAME=yourdomain.com bash deploy/scripts/setup-server.sh

# Deploy
bash deploy/scripts/deploy.sh

# Manual backup
bash deploy/scripts/backup.sh
```
