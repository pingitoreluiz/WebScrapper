# Docker Deployment Guide

## 🐳 Quick Start

### Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- 2GB RAM minimum
- 10GB disk space

---

## 🚀 Development Deployment

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/WebScrapper.git
cd WebScrapper
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your settings
nano .env
```

**Required Variables:**

- `POSTGRES_PASSWORD` - Database password
- `API_KEY` - API authentication key

### 3. Start Services

```bash
docker-compose up -d
```

### 4. Verify Deployment

```bash
# Check services
docker-compose ps

# Check logs
docker-compose logs -f

# Test backend
curl http://localhost:8000/health

# Test frontend
curl http://localhost/health
```

### 5. Access Application

- **Frontend:** <http://localhost>
- **Backend API:** <http://localhost:8000>
- **API Docs:** <http://localhost:8000/docs>

---

## 🛠️ Docker Commands

### Build Images

```bash
# Build all images
docker-compose build

# Build specific service
docker-compose build backend
docker-compose build frontend

# Build without cache
docker-compose build --no-cache
```

### Manage Services

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose stop

# Restart services
docker-compose restart

# Remove services
docker-compose down

# Remove services and volumes
docker-compose down -v
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres

# Last 100 lines
docker-compose logs --tail=100
```

### Execute Commands

```bash
# Backend shell
docker-compose exec backend bash

# Run migrations
docker-compose exec backend python -m alembic upgrade head

# Run scraper
docker-compose exec backend python -m src.scrapers.run

# Database shell
docker-compose exec postgres psql -U gpuscraper
```

---

## 📊 Monitoring

### Health Checks

```bash
# Backend health
curl http://localhost:8000/health

# Frontend health
curl http://localhost/health

# Database health
docker-compose exec postgres pg_isready
```

### Resource Usage

```bash
# Container stats
docker stats

# Disk usage
docker system df

# Clean up
docker system prune -a
```

---

## 🔧 Troubleshooting

### Services Won't Start

```bash
# Check logs
docker-compose logs

# Check ports
netstat -tulpn | grep -E '80|8000|5432'

# Restart services
docker-compose restart
```

### Database Connection Issues

```bash
# Check database logs
docker-compose logs postgres

# Verify database is ready
docker-compose exec postgres pg_isready

# Reset database
docker-compose down -v
docker-compose up -d
```

### Permission Issues

```bash
# Fix log directory permissions
sudo chown -R 1000:1000 logs/

# Fix data directory permissions
sudo chown -R 1000:1000 data/
```

---

## 🔐 Production Deployment

### 1. Use Production Compose File

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### 2. Enable HTTPS

Use a reverse proxy (nginx, Traefik, Caddy) with Let's Encrypt:

```yaml
# docker-compose.prod.yml
services:
  nginx-proxy:
    image: nginxproxy/nginx-proxy
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - /var/run/docker.sock:/tmp/docker.sock:ro
      - certs:/etc/nginx/certs
```

### 3. Use Secrets Management

```bash
# Use Docker secrets instead of .env
docker secret create postgres_password /path/to/password
docker secret create api_key /path/to/api_key
```

### 4. Set Up Backups

```bash
# Backup database
docker-compose exec postgres pg_dump -U gpuscraper gpuscraper > backup.sql

# Restore database
docker-compose exec -T postgres psql -U gpuscraper gpuscraper < backup.sql
```

---

## 📈 Scaling

### Horizontal Scaling

```bash
# Scale backend
docker-compose up -d --scale backend=3

# Use load balancer
# Add nginx/traefik for load balancing
```

### Resource Limits

```yaml
# docker-compose.yml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
```

---

## 🔄 Updates & Maintenance

### Update Application

```bash
# Pull latest code
git pull

# Rebuild images
docker-compose build

# Restart services
docker-compose up -d
```

### Update Dependencies

```bash
# Update Python packages
docker-compose exec backend pip install --upgrade -r requirements.txt

# Rebuild image
docker-compose build backend
docker-compose up -d backend
```

---

## 📝 Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `POSTGRES_USER` | Database user | gpuscraper | Yes |
| `POSTGRES_PASSWORD` | Database password | - | Yes |
| `POSTGRES_DB` | Database name | gpuscraper | Yes |
| `API_KEY` | API authentication key | - | Yes |
| `CORS_ORIGINS` | Allowed CORS origins | localhost | No |
| `LOG_LEVEL` | Logging level | INFO | No |
| `HEADLESS` | Headless browser mode | true | No |
| `MAX_PAGES` | Max pages to scrape | 10 | No |

---

## ❓ FAQ

**Q: How do I reset the database?**

```bash
docker-compose down -v
docker-compose up -d
```

**Q: How do I view real-time logs?**

```bash
docker-compose logs -f
```

**Q: How do I backup data?**

```bash
docker-compose exec postgres pg_dump -U gpuscraper > backup.sql
```

**Q: Services are slow, what should I do?**

```bash
# Check resource usage
docker stats

# Increase resources in docker-compose.yml
# Or allocate more resources to Docker Desktop
```

---

## 🆘 Support

- **Issues:** <https://github.com/yourusername/WebScrapper/issues>
- **Documentation:** See `docs/` directory
- **Docker Docs:** <https://docs.docker.com>

---

**Last Updated:** 2024-01-26
