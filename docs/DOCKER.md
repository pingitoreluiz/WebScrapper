# Docker Guide

## 📦 Images

### Backend Image

- **Base:** python:3.11-slim
- **Size:** ~180MB (optimized)
- **User:** Non-root (appuser)
- **Health Check:** Every 30s
- **Port:** 8000

### Frontend Image

- **Base:** nginx:alpine
- **Size:** ~25MB
- **User:** nginx
- **Health Check:** Every 30s
- **Port:** 80

---

## 🏗️ Build Process

### Multi-Stage Build (Backend)

**Stage 1: Builder**

- Installs build dependencies
- Compiles Python packages
- Creates wheel files

**Stage 2: Runtime**

- Minimal runtime dependencies
- Copies only compiled packages
- No build tools (smaller image)

### Benefits

- ✅ Smaller final image
- ✅ Faster deployments
- ✅ Better security (fewer tools)
- ✅ Optimized layer caching

---

## 🔧 Configuration

### Environment Variables

See `.env.example` for all available variables.

**Critical Variables:**

```env
DATABASE_URL=postgresql://user:pass@postgres:5432/db
API_KEY=your-secure-key
CORS_ORIGINS=http://localhost
```

### Volumes

**postgres-data:**

- Database persistence
- Location: `/var/lib/postgresql/data`
- Backup recommended

**logs:**

- Application logs
- Location: `/app/logs`
- Rotation recommended

---

## 🌐 Networking

### app-network (Bridge)

- Internal communication
- Services: backend, frontend, postgres
- No external exposure (except ports)

### Port Mapping

- `80:80` - Frontend (nginx)
- `8000:8000` - Backend (FastAPI)
- `5432` - Postgres (internal only)

---

## 🔐 Security

### Best Practices Implemented

- ✅ Non-root users
- ✅ Multi-stage builds
- ✅ Minimal base images
- ✅ Health checks
- ✅ Security headers (nginx)
- ✅ No secrets in images

### Production Recommendations

- Use Docker secrets
- Enable TLS/HTTPS
- Regular image updates
- Scan for vulnerabilities
- Limit container resources

---

## 📊 Resource Management

### Recommended Limits

```yaml
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

### Monitoring

```bash
# Real-time stats
docker stats

# Disk usage
docker system df

# Cleanup
docker system prune -a
```

---

## 🔄 Updates

### Update Application

```bash
git pull
docker-compose build
docker-compose up -d
```

### Update Base Images

```bash
docker-compose pull
docker-compose up -d
```

---

## 🐛 Debugging

### Access Container

```bash
docker-compose exec backend bash
docker-compose exec frontend sh
```

### View Logs

```bash
docker-compose logs -f backend
docker-compose logs --tail=100 frontend
```

### Inspect Container

```bash
docker inspect gpuscraper-backend
docker exec -it gpuscraper-backend env
```

---

## 📝 Best Practices

1. **Use .dockerignore** - Exclude unnecessary files
2. **Layer Caching** - Order commands by change frequency
3. **Multi-Stage Builds** - Smaller final images
4. **Health Checks** - Monitor container health
5. **Non-Root Users** - Security best practice
6. **Explicit Versions** - Reproducible builds

---

**See also:** [DEPLOYMENT.md](DEPLOYMENT.md) for deployment guide
