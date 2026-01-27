# Production Deployment Checklist

## 🚀 Pre-Deployment

### Infrastructure Setup

- [ ] SSL/TLS certificates installed and configured
- [ ] Domain name configured and DNS propagated
- [ ] Load balancer configured (if applicable)
- [ ] Firewall rules configured
- [ ] Database backups enabled and tested
- [ ] Log aggregation configured
- [ ] Monitoring and alerting configured

### Application Configuration

- [ ] Environment variables set in production
- [ ] Secrets stored securely (not in code)
- [ ] Database connection string configured
- [ ] Redis connection configured
- [ ] API keys generated and stored
- [ ] CORS origins configured correctly
- [ ] Rate limiting configured

### Code Quality

- [ ] All tests passing (`pytest`)
- [ ] Code formatted (`black src/`)
- [ ] No linting errors (`flake8 src/`)
- [ ] Type checking passed (`mypy src/`)
- [ ] Security scan passed (`bandit -r src/`)
- [ ] Dependencies updated and scanned (`safety check`)

### Database

- [ ] Database migrations tested
- [ ] Database backup created
- [ ] Database indexes optimized
- [ ] Connection pooling configured
- [ ] Backup restoration tested

### Performance

- [ ] Load testing completed
- [ ] Performance profiling done
- [ ] Caching configured
- [ ] Static files optimized
- [ ] Database queries optimized

---

## 📦 Deployment Steps

### 1. Backup Current System

```bash
# Backup database
docker-compose exec postgres pg_dump -U postgres gpuscraper > backup_$(date +%Y%m%d_%H%M%S).sql

# Backup configuration
cp .env .env.backup
cp docker-compose.yml docker-compose.yml.backup
```

### 2. Pull Latest Code

```bash
git fetch origin
git checkout main
git pull origin main
```

### 3. Build Docker Images

```bash
# Build with no cache for clean build
docker-compose build --no-cache

# Or build specific service
docker-compose build backend
docker-compose build frontend
```

### 4. Run Database Migrations

```bash
# Test migrations first
docker-compose run backend alembic upgrade head --sql

# Apply migrations
docker-compose run backend alembic upgrade head
```

### 5. Deploy New Version

```bash
# Stop current containers
docker-compose down

# Start new containers
docker-compose up -d

# Check status
docker-compose ps
```

### 6. Run Smoke Tests

```bash
# Run deployment checks
python scripts/deployment_check.py --url http://your-domain.com

# Or manually test
curl http://your-domain.com/health
curl http://your-domain.com/api/v1/products?limit=1
```

### 7. Monitor Deployment

```bash
# Watch logs
docker-compose logs -f

# Check specific service
docker-compose logs -f backend

# Check metrics
curl http://your-domain.com/metrics
```

---

## ✅ Post-Deployment Verification

### Functional Tests

- [ ] Health endpoint responding (`/health`)
- [ ] API endpoints working (`/api/v1/products`)
- [ ] Frontend loading correctly
- [ ] Database connectivity OK
- [ ] Authentication working
- [ ] Rate limiting active
- [ ] Scrapers can run successfully

### Performance Tests

- [ ] Response times within SLA (< 200ms)
- [ ] No memory leaks
- [ ] CPU usage normal (< 70%)
- [ ] Database connections healthy
- [ ] Cache hit rate acceptable (> 50%)

### Security Tests

- [ ] HTTPS working correctly
- [ ] Security headers present
- [ ] Authentication enforced
- [ ] Rate limiting working
- [ ] No exposed secrets
- [ ] CORS configured correctly

### Monitoring

- [ ] Application metrics being collected
- [ ] Logs being aggregated
- [ ] Alerts configured and working
- [ ] Dashboards accessible
- [ ] Error tracking active

---

## 🔄 Rollback Procedure

If deployment fails:

### 1. Stop New Version

```bash
docker-compose down
```

### 2. Restore Previous Version

```bash
# Restore configuration
cp .env.backup .env
cp docker-compose.yml.backup docker-compose.yml

# Checkout previous version
git checkout <previous-commit-hash>

# Rebuild
docker-compose build
```

### 3. Restore Database

```bash
# Only if database was migrated
docker-compose exec postgres psql -U postgres gpuscraper < backup_YYYYMMDD_HHMMSS.sql
```

### 4. Start Previous Version

```bash
docker-compose up -d
```

### 5. Verify Rollback

```bash
python scripts/deployment_check.py
```

---

## 📊 Monitoring Checklist

### First Hour

- [ ] Check error logs every 5 minutes
- [ ] Monitor response times
- [ ] Watch CPU and memory usage
- [ ] Check database connections
- [ ] Verify no critical alerts

### First Day

- [ ] Review error rates
- [ ] Check performance metrics
- [ ] Verify backup jobs ran
- [ ] Review user feedback
- [ ] Check scraper success rates

### First Week

- [ ] Analyze performance trends
- [ ] Review security logs
- [ ] Check resource utilization
- [ ] Verify monitoring alerts
- [ ] Plan optimizations if needed

---

## 🚨 Emergency Contacts

- **DevOps Lead:** [Contact Info]
- **Backend Lead:** [Contact Info]
- **Database Admin:** [Contact Info]
- **On-Call Engineer:** [Contact Info]

---

## 📝 Deployment Log

| Date | Version | Deployed By | Status | Notes |
|------|---------|-------------|--------|-------|
| 2026-01-26 | 2.0.0 | [Name] | ✅ Success | Initial production deployment |
|  |  |  |  |  |

---

## 🔧 Common Issues

### Issue: Container won't start

**Symptoms:** Container exits immediately

**Solution:**

```bash
# Check logs
docker-compose logs backend

# Check configuration
docker-compose config

# Rebuild
docker-compose build --no-cache backend
```

### Issue: Database connection failed

**Symptoms:** API returns 500 errors

**Solution:**

```bash
# Check database is running
docker-compose ps postgres

# Check database logs
docker-compose logs postgres

# Verify connection string in .env
```

### Issue: High memory usage

**Symptoms:** Container restarts, OOM errors

**Solution:**

```bash
# Check memory usage
docker stats

# Increase memory limit in docker-compose.yml
# Optimize queries and caching
```

---

**Last Updated:** 2026-01-26  
**Version:** 2.0.0
