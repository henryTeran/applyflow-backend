# 🐳 Docker Quick Start Guide

## Prerequisites

- Docker Desktop installed
- Docker Compose installed

## 🚀 Quick Start

### 1. Create .env file

```bash
cp .env.example .env
```

Edit `.env` with your settings:

```env
# SMTP (required for email sending)
SMTP_HOST=smtp.gmail.com
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM=your-email@gmail.com

# OpenAI (optional)
OPENAI_API_KEY=sk-your-key

# Security (generate a strong secret)
SECRET_KEY=your-super-secret-key-here
```

### 2. Start all services

```bash
docker-compose up -d
```

This will start:
- **PostgreSQL** database on port 5432
- **Redis** for caching and queues on port 6379
- **FastAPI** application on port 8000
- **Celery Worker** for background tasks
- **Celery Beat** for scheduled tasks

### 3. Check status

```bash
docker-compose ps
```

All services should show status "Up".

### 4. View logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f web
docker-compose logs -f celery_worker
```

### 5. Access the application

- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/ping

## 📋 Common Commands

### Start services

```bash
# Start all services
docker-compose up -d

# Start specific service
docker-compose up -d web
```

### Stop services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v
```

### View logs

```bash
# Follow all logs
docker-compose logs -f

# Follow specific service
docker-compose logs -f web
docker-compose logs -f celery_worker
```

### Run migrations

```bash
# Migrations run automatically on startup
# To run manually:
docker-compose exec web alembic upgrade head
```

### Access database

```bash
# PostgreSQL shell
docker-compose exec db psql -U applyflow_user -d applyflow_db

# List tables
docker-compose exec db psql -U applyflow_user -d applyflow_db -c "\dt"
```

### Execute commands in container

```bash
# Python shell
docker-compose exec web python

# Run tests
docker-compose exec web pytest

# Access bash
docker-compose exec web bash
```

### Rebuild after code changes

```bash
# Rebuild and restart
docker-compose up -d --build

# Rebuild specific service
docker-compose up -d --build web
```

## 🔧 Development Workflow

### 1. Code changes

The `web` service has volume mounting, so code changes are reflected immediately (with auto-reload enabled).

### 2. Add new dependencies

If you add packages to `requirements.txt`:

```bash
docker-compose up -d --build web celery_worker
```

### 3. Database migrations

```bash
# Create migration
docker-compose exec web alembic revision --autogenerate -m "Description"

# Apply migration
docker-compose exec web alembic upgrade head
```

### 4. Run tests

```bash
docker-compose exec web pytest tests/
```

## 📊 Monitoring

### Check container resources

```bash
docker stats
```

### Check health

```bash
# Web service
curl http://localhost:8000/health

# Database
docker-compose exec db pg_isready -U applyflow_user

# Redis
docker-compose exec redis redis-cli ping
```

## 🐛 Troubleshooting

### Services won't start

```bash
# Check logs
docker-compose logs

# Restart specific service
docker-compose restart web
```

### Database connection issues

```bash
# Check database is running
docker-compose ps db

# Check database logs
docker-compose logs db

# Verify connection
docker-compose exec db psql -U applyflow_user -d applyflow_db -c "SELECT 1;"
```

### Port already in use

If port 8000, 5432, or 6379 is already in use:

Edit `docker-compose.yml` and change the port mapping:

```yaml
ports:
  - "8001:8000"  # Use port 8001 instead
```

### Clear everything and start fresh

```bash
# Stop all containers
docker-compose down

# Remove volumes (deletes database!)
docker-compose down -v

# Remove images
docker-compose down --rmi all

# Start fresh
docker-compose up -d --build
```

### Celery tasks not running

```bash
# Check worker logs
docker-compose logs celery_worker

# Restart worker
docker-compose restart celery_worker

# Monitor tasks
docker-compose exec web python -c "from app.celery_app import celery_app; print(celery_app.control.inspect().active())"
```

## 🎯 Production Deployment

For production, modify `docker-compose.yml`:

1. **Remove debug mode**:
   ```yaml
   environment:
     - DEBUG=False
   ```

2. **Use environment file**:
   ```yaml
   env_file:
     - .env.production
   ```

3. **Add restart policies**:
   ```yaml
   restart: always
   ```

4. **Use production WSGI server**:
   ```dockerfile
   CMD ["gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
   ```

5. **Add nginx reverse proxy**
6. **Use secrets management**
7. **Set up log aggregation**
8. **Enable HTTPS**

## 📚 Additional Resources

- **Docker Documentation**: https://docs.docker.com/
- **Docker Compose**: https://docs.docker.com/compose/
- **FastAPI in Docker**: https://fastapi.tiangolo.com/deployment/docker/

## 🎉 Success!

Your ApplyFlow backend is now running in Docker! 🚀

Access the API at: http://localhost:8000/docs
