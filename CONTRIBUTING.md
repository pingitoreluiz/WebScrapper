# Contributing to GPU Price Scraper

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to the project.

---

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Code Standards](#code-standards)
- [Testing Requirements](#testing-requirements)
- [Pull Request Process](#pull-request-process)
- [Project Structure](#project-structure)

---

## 🤝 Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inspiring community for all.

### Our Standards

**Positive behavior includes:**

- Using welcoming and inclusive language
- Being respectful of differing viewpoints
- Gracefully accepting constructive criticism
- Focusing on what is best for the community

**Unacceptable behavior includes:**

- Trolling, insulting/derogatory comments
- Public or private harassment
- Publishing others' private information
- Other conduct which could reasonably be considered inappropriate

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- Git
- Node.js 18+ (for frontend development)

### Fork and Clone

```bash
# Fork the repository on GitHub
# Then clone your fork
git clone https://github.com/YOUR_USERNAME/WebScrapper.git
cd WebScrapper

# Add upstream remote
git remote add upstream https://github.com/ORIGINAL_OWNER/WebScrapper.git
```

### Setup Development Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install

# Copy environment file
cp .env.example .env

# Start services
docker-compose up -d
```

### Verify Setup

```bash
# Run tests
pytest

# Check code style
black --check src/
flake8 src/

# Start development server
uvicorn src.backend.api.app:app --reload
```

---

## 🔄 Development Workflow

### Branch Naming

Use descriptive branch names:

```bash
feature/add-new-scraper       # New features
bugfix/fix-price-parsing      # Bug fixes
hotfix/critical-security-fix  # Urgent fixes
docs/update-api-docs          # Documentation
refactor/improve-caching      # Code refactoring
test/add-integration-tests    # Test additions
```

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```bash
feat: add Terabyte scraper
fix: correct price parsing for Kabum
docs: update API documentation
test: add integration tests for scrapers
refactor: improve data processor performance
chore: update dependencies
```

**Format:**

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Example:**

```
feat(scrapers): add support for Terabyte store

- Implement TerabyteScraper class
- Add selectors for product extraction
- Update scraper factory

Closes #123
```

### Workflow Steps

1. **Create Branch**

   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**
   - Write code
   - Add tests
   - Update documentation

3. **Test Locally**

   ```bash
   pytest
   black src/
   flake8 src/
   ```

4. **Commit Changes**

   ```bash
   git add .
   git commit -m "feat: your feature description"
   ```

5. **Push to Fork**

   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create Pull Request**
   - Go to GitHub
   - Click "New Pull Request"
   - Fill out PR template

---

## 📝 Code Standards

### Python Style

**Follow PEP 8** with these tools:

```bash
# Format code
black src/

# Check style
flake8 src/

# Type checking
mypy src/
```

**Configuration:**

`.flake8`:

```ini
[flake8]
max-line-length = 100
exclude = .git,__pycache__,venv
ignore = E203,W503
```

`pyproject.toml`:

```toml
[tool.black]
line-length = 100
target-version = ['py311']
```

### Code Quality

**Good Practices:**

- ✅ Use type hints
- ✅ Write docstrings
- ✅ Keep functions small (<50 lines)
- ✅ Use meaningful variable names
- ✅ Handle errors gracefully
- ✅ Log important events

**Example:**

```python
def calculate_price_trend(
    product_id: int,
    days: int = 30
) -> dict[str, float]:
    """
    Calculate price trend for a product.
    
    Args:
        product_id: Product database ID
        days: Number of days to analyze
        
    Returns:
        Dictionary with trend metrics
        
    Raises:
        ValueError: If product not found
    """
    # Implementation
    pass
```

### JavaScript Style

```javascript
// Use ES6+ features
const fetchProducts = async () => {
    try {
        const response = await fetch('/api/v1/products');
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error fetching products:', error);
        throw error;
    }
};
```

---

## 🧪 Testing Requirements

### Test Coverage

- **Minimum:** 80% overall coverage
- **New code:** 90%+ coverage
- **Critical paths:** 100% coverage

### Writing Tests

**Unit Test Example:**

```python
import pytest
from src.data.processors.cleaner import DataCleaner

class TestDataCleaner:
    def test_clean_price(self):
        cleaner = DataCleaner()
        result = cleaner.clean_price("R$ 10.000,00")
        assert result == 10000.00
    
    def test_clean_price_invalid(self):
        cleaner = DataCleaner()
        with pytest.raises(ValueError):
            cleaner.clean_price("invalid")
```

**Integration Test Example:**

```python
def test_scraper_to_database(db_session):
    scraper = PichauScraper(config)
    products = scraper.run()
    
    for product in products:
        db_session.add(product)
    db_session.commit()
    
    assert db_session.query(Product).count() > 0
```

### Running Tests

```bash
# All tests
pytest

# Specific type
pytest -m unit
pytest -m integration
pytest -m e2e

# With coverage
pytest --cov=src --cov-report=html

# Specific file
pytest tests/unit/test_scrapers.py
```

---

## 🔍 Pull Request Process

### Before Submitting

**Checklist:**

- [ ] Code follows style guidelines
- [ ] Tests added/updated
- [ ] All tests pass
- [ ] Documentation updated
- [ ] Commit messages follow convention
- [ ] No merge conflicts

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added
- [ ] Integration tests added
- [ ] Manual testing completed

## Screenshots (if applicable)
Add screenshots here

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests pass locally
```

### Review Process

1. **Automated Checks**
   - CI/CD pipeline runs
   - Tests must pass
   - Code coverage checked

2. **Code Review**
   - At least 1 approval required
   - Address review comments
   - Update as needed

3. **Merge**
   - Squash and merge
   - Delete branch after merge

---

## 📁 Project Structure

```
WebScrapper/
├── src/
│   ├── backend/          # Backend API
│   │   ├── api/         # FastAPI routes
│   │   └── core/        # Core models
│   ├── scrapers/        # Web scrapers
│   │   ├── base.py      # Base scraper
│   │   └── stores/      # Store-specific
│   ├── data/            # Data processing
│   │   ├── processors/  # Data processors
│   │   └── analytics/   # Analytics engine
│   └── utils/           # Utilities
├── frontend/            # Web dashboard
│   ├── static/         # CSS, JS
│   └── templates/      # HTML
├── tests/              # All tests
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── docs/               # Documentation
└── .github/            # CI/CD workflows
```

---

## 💡 Tips for Contributors

### Finding Issues

- Check [Issues](https://github.com/project/issues) page
- Look for `good first issue` label
- Ask questions in issue comments

### Getting Help

- Read documentation first
- Search existing issues
- Ask in discussions
- Be specific about your problem

### Best Practices

1. **Start Small:** Begin with documentation or small bug fixes
2. **Ask Questions:** Don't hesitate to ask for clarification
3. **Be Patient:** Reviews may take time
4. **Stay Updated:** Keep your fork synced with upstream

---

## 📞 Contact

- **Issues:** [GitHub Issues](https://github.com/project/issues)
- **Discussions:** [GitHub Discussions](https://github.com/project/discussions)
- **Email:** <support@example.com>

---

## 📜 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing! 🎉**

---

**Last Updated:** 2026-01-26  
**Version:** 2.0.0
