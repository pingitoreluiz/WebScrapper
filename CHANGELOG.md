# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.1.0] - 2026-02-09

### 🏗️ Refactoring - Unificação da Camada de Banco de Dados

Eliminação da dívida técnica causada pela coexistência de duas camadas de banco de dados (SQLite raw + SQLAlchemy ORM). Toda a lógica agora passa pela camada SQLAlchemy unificada.

### Changed

- **`src/main.py`**: Reescrito completamente para usar `ScraperFactory` (Factory Pattern) ao invés de instanciar scrapers diretamente. Agora usa `get_db_session()` + `ProductRepository` para todas as operações de banco.
- **`src/backend/core/repository.py`**: Adicionados métodos `export_to_csv()` e `export_to_json()` ao `ProductRepository`, migrando a funcionalidade de exportação que antes existia na camada legada.

### Removed

- **`src/database.py`**: Removida camada legada de acesso direto ao SQLite via `sqlite3`. Toda funcionalidade (save, stats, search, export, cleanup) já existia no `ProductRepository` via SQLAlchemy ORM.
- **`src/legacy_utils.py`**: Removidas utilidades legadas (`setup_logger`, `ColoredFormatter`, `clean_price`, `extract_chip_brand`, `extract_manufacturer`, `extract_model`, `validate_product_data`, `ProgressTracker`, `print_header`, `print_stats`, `format_duration`). O logging agora usa `src.utils.logger.get_logger` (structlog); funções de formatação foram incorporadas no `main.py`; funções de extração de dados não eram importadas por nenhum módulo ativo.

### Technical Notes

- **Zero breaking changes**: Todos os API routes e testes já usavam exclusivamente a camada SQLAlchemy — nenhuma alteração necessária.
- **Dependências eliminadas**: `sqlite3` direto, `colorama` (via legacy_utils).
- **Padrões utilizados**: Factory Pattern (ScraperFactory), Repository Pattern (ProductRepository), Singleton (get_db_session).

## [3.0.0] - 2026-02-02

### 🚀 Major Feature - Real-Time Updates

Significant architecture upgrade to support real-time data streaming via WebSockets.

### Added

#### WebSockets & Real-Time

- **Backend WebSocket Infrastructure**:
  - `ConnectionManager` for handling multiple websocket connections
  - New `/ws/dashboard` endpoint for real-time streaming
  - Event broadcasting system (Singleton pattern)
- **Frontend Real-Time**:
  - `WebSocketManager` with automatic reconnection strategy
  - Live status indicator (Online/Offline)
  - Toast notifications for live events
  - Dashboard auto-refresh on scraper completion
- **Event System**:
  - `scraper.started`: Push notification when scraping begins
  - `scraper.progress`: Live progress updates (products found/saved)
  - `scraper.completed`: Final summary statistics
  - `product.new`: Instant notification when new products are found

### Changed

- Dashboard now connects automatically to WebSocket on load
- `BaseScraper` updated to broadcast events during execution
- UI feedback improved with connection status indicators

## [2.0.0] - 2026-01-26

### 🎉 Major Release - Production Ready

Complete rewrite and modernization of the GPU Price Scraper system.

### Added

#### Phase 1: Foundation

- SQLAlchemy ORM with PostgreSQL support
- Pydantic models for data validation
- Structured logging with structlog
- Environment-based configuration
- Alembic database migrations

#### Phase 2: Scrapers

- Refactored scraper architecture with Template Method pattern
- Factory pattern for scraper creation
- Support for 3 stores: Pichau, Kabum, Terabyte
- Browser automation with Playwright
- Anti-detection mechanisms
- Automatic retry logic
- Scraper metrics tracking

#### Phase 3: Backend API

- FastAPI REST API with 15+ endpoints
- OpenAPI/Swagger documentation
- API key authentication
- Rate limiting middleware
- Request logging middleware
- CORS configuration
- Product search and filtering
- Analytics endpoints
- Data export (CSV, JSON)

#### Phase 4: Data Engineering

- Data cleaning pipeline
- Data validation system
- Data enrichment (chip brand, manufacturer detection)
- Price trend analysis
- Market insights engine
- Recommendation system
- CSV/JSON/Excel exporters

#### Phase 5: Frontend

- Modern responsive web dashboard
- Real-time data updates
- Interactive charts with Chart.js
- Product search and filtering
- Dark mode support
- Mobile-first design
- Glassmorphism effects

#### Phase 6: DevOps

- Docker containerization (multi-stage builds)
- Docker Compose orchestration
- Nginx web server configuration
- GitHub Actions CI/CD pipeline
- Automated testing in CI
- Security scanning
- Production-ready deployment

#### Phase 7: Quality Assurance

- 88 unit tests (100% passing)
- 15+ integration tests
- 20+ E2E tests with Playwright
- pytest configuration with markers
- 85%+ code coverage
- Performance testing with Locust
- Security testing

#### Phase 8: Documentation

- Complete architecture documentation
- System diagrams (Mermaid)
- Data flow documentation
- Database schema documentation
- API reference documentation
- Contributing guidelines
- Testing guide
- Deployment guide
- Docker guide

#### Phase 9: Polish & Optimizations

- Performance monitoring middleware
- Prometheus metrics integration
- Security headers middleware
- Cache control middleware
- Production deployment checklist
- Deployment smoke tests
- Performance profiling tools

### Changed

- Migrated from basic scraping to professional architecture
- Improved error handling across all components
- Enhanced logging with structured format
- Optimized database queries with indexes
- Improved API response times with caching

### Security

- API key authentication
- Rate limiting (60 requests/minute)
- Input validation with Pydantic
- SQL injection prevention
- XSS protection
- Security headers (HSTS, CSP, etc.)
- Secrets management with environment variables
- Dependency vulnerability scanning

### Performance

- Database connection pooling
- Redis caching
- API response caching
- Gzip compression
- Optimized Docker images
- Concurrent scraping
- Browser instance reuse

---

## [1.0.0] - 2025-XX-XX

### Initial Release

- Basic web scraping functionality
- Simple data storage
- Basic API endpoints

---

## Version History

| Version | Date | Description |
|---------|------|-------------|
| 3.0.0 | 2026-02-02 | Real-time WebSockets update |
| 2.0.0 | 2026-01-26 | Complete rewrite - Production ready |
| 1.0.0 | 2025-XX-XX | Initial release |

---

## Upgrade Guide

### From 1.0.0 to 2.0.0

This is a **major breaking change** with complete architecture rewrite.

**Migration Steps:**

1. **Backup existing data**

   ```bash
   # Export old data
   python legacy/export_data.py > data_backup.json
   ```

2. **Set up new environment**

   ```bash
   # Install dependencies
   pip install -r requirements.txt
   
   # Configure environment
   cp .env.example .env
   # Edit .env with your settings
   ```

3. **Initialize new database**

   ```bash
   # Run migrations
   alembic upgrade head
   ```

4. **Import old data (if applicable)**

   ```bash
   # Import script
   python scripts/import_legacy_data.py data_backup.json
   ```

5. **Deploy with Docker**

   ```bash
   docker-compose up -d
   ```

**Breaking Changes:**

- Complete API redesign
- New database schema
- Different configuration format
- New authentication system

---

**Maintained by:** GPU Price Scraper Team  
**License:** MIT
