# API Endpoints Reference

## 📖 Overview

Complete reference for all API endpoints in the GPU Price Scraper API.

**Base URL:** `http://localhost:8000/api/v1`

**Authentication:** API key in header `X-API-Key: your-key-here`

---

## 🛍️ Products

### List Products

```http
GET /api/v1/products
```

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | int | 50 | Max results (1-100) |
| `offset` | int | 0 | Skip results |
| `chip_brand` | string | - | Filter by NVIDIA/AMD |
| `store` | string | - | Filter by store |
| `min_price` | float | - | Minimum price |
| `max_price` | float | - | Maximum price |
| `available` | bool | - | In stock only |

**Response:**

```json
{
  "items": [
    {
      "id": 1,
      "title": "RTX 4090 ASUS ROG",
      "price": 10000.00,
      "store": "Pichau",
      "url": "https://...",
      "chip_brand": "NVIDIA",
      "manufacturer": "ASUS",
      "available": true,
      "scraped_at": "2026-01-26T10:00:00"
    }
  ],
  "total": 150,
  "limit": 50,
  "offset": 0
}
```

**Example:**

```bash
curl -H "X-API-Key: your-key" \
  "http://localhost:8000/api/v1/products?chip_brand=NVIDIA&limit=10"
```

---

### Search Products

```http
GET /api/v1/products/search
```

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | Yes | Search term |
| `limit` | int | No | Max results |

**Example:**

```bash
curl "http://localhost:8000/api/v1/products/search?query=RTX+4090"
```

---

### Get Product by ID

```http
GET /api/v1/products/{id}
```

**Response:**

```json
{
  "id": 1,
  "title": "RTX 4090 ASUS ROG",
  "price": 10000.00,
  "store": "Pichau",
  "price_history": [
    {"price": 10500.00, "date": "2026-01-20"},
    {"price": 10000.00, "date": "2026-01-26"}
  ]
}
```

---

### Best Deals

```http
GET /api/v1/products/best-deals
```

Returns products sorted by lowest price.

---

### Product Statistics

```http
GET /api/v1/products/stats/overview
```

**Response:**

```json
{
  "total_products": 150,
  "average_price": 7500.00,
  "by_store": {
    "Pichau": 50,
    "Kabum": 60,
    "Terabyte": 40
  },
  "by_chip_brand": {
    "NVIDIA": 100,
    "AMD": 50
  }
}
```

---

## 🕷️ Scrapers

### Run Scraper

```http
POST /api/v1/scrapers/run
```

**Authentication Required:** Yes

**Request Body:**

```json
{
  "stores": ["Pichau", "Kabum"],
  "headless": true,
  "max_pages": 5
}
```

**Response:**

```json
{
  "status": "started",
  "job_id": "abc123",
  "stores": ["Pichau", "Kabum"]
}
```

---

### Scraper Status

```http
GET /api/v1/scrapers/status
```

**Response:**

```json
{
  "status": "idle",
  "last_run": "2026-01-26T10:00:00",
  "next_scheduled": "2026-01-27T00:00:00"
}
```

---

### Scraper History

```http
GET /api/v1/scrapers/history
```

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | int | 10 | Max results |
| `store` | string | - | Filter by store |

**Response:**

```json
[
  {
    "id": 1,
    "store": "Pichau",
    "started_at": "2026-01-26T10:00:00",
    "completed_at": "2026-01-26T10:05:00",
    "products_found": 50,
    "success": true
  }
]
```

---

### Scraper Metrics

```http
GET /api/v1/scrapers/metrics
```

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `days` | int | 7 | Days to analyze |

**Response:**

```json
{
  "total_runs": 21,
  "success_rate": 95.2,
  "avg_products_per_run": 48,
  "by_store": {
    "Pichau": {"runs": 7, "success_rate": 100},
    "Kabum": {"runs": 7, "success_rate": 85.7},
    "Terabyte": {"runs": 7, "success_rate": 100}
  }
}
```

---

## 📊 Analytics

### Price Trends

```http
GET /api/v1/analytics/trends
```

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `days` | int | 30 | Days to analyze |
| `chip_brand` | string | - | Filter by brand |

---

### Price History

```http
GET /api/v1/analytics/price-history/{product_id}
```

**Response:**

```json
{
  "product_id": 1,
  "title": "RTX 4090",
  "history": [
    {"price": 10500.00, "date": "2026-01-20"},
    {"price": 10000.00, "date": "2026-01-26"}
  ],
  "trend": "decreasing",
  "avg_price": 10250.00
}
```

---

## 📤 Export

### Export CSV

```http
GET /api/v1/export/csv
```

Returns CSV file with all products.

---

### Export JSON

```http
GET /api/v1/export/json
```

Returns JSON file with all products.

---

## ❤️ Health

### Health Check

```http
GET /health
```

**Response:**

```json
{
  "status": "healthy",
  "timestamp": "2026-01-26T10:00:00",
  "version": "2.0.0"
}
```

---

## ⚠️ Error Responses

### 400 Bad Request

```json
{
  "detail": "Invalid query parameter"
}
```

### 401 Unauthorized

```json
{
  "detail": "Invalid or missing API key"
}
```

### 404 Not Found

```json
{
  "detail": "Product not found"
}
```

### 429 Too Many Requests

```json
{
  "detail": "Rate limit exceeded. Try again in 60 seconds."
}
```

### 500 Internal Server Error

```json
{
  "detail": "Internal server error"
}
```

---

**Last Updated:** 2026-01-26  
**Version:** 2.0.0
