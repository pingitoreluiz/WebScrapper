# Data Flow Documentation

## 🔄 Overview

This document describes how data flows through the GPU Price Scraper system, from initial scraping to final presentation in the dashboard.

---

## 📊 Scraping Pipeline

### Complete Scraping Flow

```mermaid
sequenceDiagram
    participant User
    participant API
    participant Factory
    participant Scraper
    participant Browser
    participant Store
    participant Processor
    participant Database
    
    User->>API: POST /api/v1/scrapers/run
    API->>Factory: create_scraper("Pichau")
    Factory->>Scraper: Initialize PichauScraper
    Scraper->>Browser: Launch Playwright
    
    loop For each page
        Scraper->>Browser: Navigate to page
        Browser->>Store: HTTP Request
        Store-->>Browser: HTML Response
        Browser-->>Scraper: Page content
        Scraper->>Scraper: Extract products
    end
    
    Scraper->>Processor: Raw products list
    Processor->>Processor: Clean data
    Processor->>Processor: Validate data
    Processor->>Processor: Enrich data
    Processor->>Database: Bulk insert products
    Database-->>Processor: Success
    Processor-->>API: Scraping metrics
    API-->>User: {products_found: 50, success: true}
```

---

## 🧹 Data Processing Pipeline

### Transformation Stages

```mermaid
graph LR
    A[Raw Product Data] --> B[Data Cleaner]
    B --> C{Valid?}
    C -->|No| D[Reject]
    C -->|Yes| E[Data Validator]
    E --> F{Passes Validation?}
    F -->|No| D
    F -->|Yes| G[Data Enricher]
    G --> H[Enriched Product]
    H --> I[(Database)]
    
    style A fill:#f9f,stroke:#333
    style H fill:#9f9,stroke:#333
    style D fill:#f99,stroke:#333
```

### Stage Details

**1. Data Cleaner**

```python
Input:  {"title": "  RTX 4090  ", "price": "R$ 10.000,00"}
Output: {"title": "RTX 4090", "price": 10000.00}
```

**Operations:**

- Trim whitespace
- Normalize price format (remove currency symbols)
- Fix character encoding
- Standardize text case

**2. Data Validator**

```python
Checks:
- Price > 0 and < 100000
- URL is valid HTTP/HTTPS
- Title length > 5 characters
- Store is in allowed list
```

**3. Data Enricher**

```python
Input:  {"title": "ASUS ROG RTX 4090"}
Output: {
  "title": "ASUS ROG RTX 4090",
  "chip_brand": "NVIDIA",
  "manufacturer": "ASUS",
  "model": "RTX 4090"
}
```

---

## 📈 Analytics Pipeline

### Price Trends Calculation

```mermaid
graph TB
    A[Product Data] --> B[Group by Product]
    B --> C[Calculate Moving Average]
    C --> D[Detect Outliers]
    D --> E[Identify Trends]
    E --> F[Generate Insights]
    
    G[Historical Prices] --> C
    
    F --> H[Trend Report]
    F --> I[Price Alerts]
    F --> J[Recommendations]
```

### Analytics Flow

```mermaid
sequenceDiagram
    participant API
    participant Analytics
    participant Database
    participant Cache
    
    API->>Cache: Check cached results
    Cache-->>API: Cache miss
    API->>Analytics: calculate_trends()
    Analytics->>Database: Query price history
    Database-->>Analytics: Historical data
    Analytics->>Analytics: Calculate moving average
    Analytics->>Analytics: Detect outliers
    Analytics->>Analytics: Identify trends
    Analytics->>Cache: Store results (TTL: 1h)
    Analytics-->>API: Trend data
    API-->>Client: JSON response
```

---

## 🔍 API Request Flow

### GET /api/v1/products

```mermaid
sequenceDiagram
    participant Client
    participant Nginx
    participant FastAPI
    participant Auth
    participant RateLimit
    participant Cache
    participant Database
    
    Client->>Nginx: GET /api/v1/products?chip_brand=NVIDIA
    Nginx->>FastAPI: Forward request
    FastAPI->>Auth: Validate API key
    Auth-->>FastAPI: ✓ Valid
    FastAPI->>RateLimit: Check rate limit
    RateLimit-->>FastAPI: ✓ Within limit
    FastAPI->>Cache: Check cache
    Cache-->>FastAPI: Cache miss
    FastAPI->>Database: SELECT * FROM products WHERE chip_brand='NVIDIA'
    Database-->>FastAPI: Product list
    FastAPI->>Cache: Store result
    FastAPI-->>Nginx: JSON response
    Nginx-->>Client: Compressed response
```

---

## 💾 Database Operations

### Product Insert Flow

```mermaid
graph TD
    A[New Product Data] --> B{Product exists?}
    B -->|Yes| C[Update price]
    B -->|No| D[Insert new product]
    C --> E[Create price history entry]
    D --> E
    E --> F[Update scraper metrics]
    F --> G[Commit transaction]
```

### Query Optimization Flow

```mermaid
graph LR
    A[API Request] --> B{Cached?}
    B -->|Yes| C[Return cached data]
    B -->|No| D{Simple query?}
    D -->|Yes| E[Direct DB query]
    D -->|No| F[Use indexed columns]
    F --> G[Apply filters]
    G --> H[Paginate results]
    H --> I[Cache result]
    I --> J[Return data]
    E --> I
```

---

## 🔄 Real-Time Updates

### Dashboard Data Refresh

```mermaid
sequenceDiagram
    participant Dashboard
    participant API
    participant Database
    
    loop Every 30 seconds
        Dashboard->>API: GET /api/v1/products/stats
        API->>Database: Query latest stats
        Database-->>API: Stats data
        API-->>Dashboard: JSON response
        Dashboard->>Dashboard: Update UI
    end
```

---

## 📤 Data Export Flow

### CSV Export

```mermaid
graph LR
    A[Export Request] --> B[Query Database]
    B --> C[Apply Filters]
    C --> D[Format as CSV]
    D --> E[Stream to Client]
    
    style A fill:#bbf
    style E fill:#bfb
```

### JSON Export

```mermaid
graph LR
    A[Export Request] --> B[Query Database]
    B --> C[Apply Filters]
    C --> D[Serialize to JSON]
    D --> E[Compress]
    E --> F[Stream to Client]
    
    style A fill:#bbf
    style F fill:#bfb
```

---

## 🔐 Authentication Flow

```mermaid
sequenceDiagram
    participant Client
    participant API
    participant Auth
    participant Database
    
    Client->>API: Request with X-API-Key header
    API->>Auth: Validate key
    Auth->>Database: Check API key
    Database-->>Auth: Key valid
    Auth-->>API: Authorized
    API->>API: Process request
    API-->>Client: Response
```

---

## ⚡ Caching Strategy

### Multi-Level Cache

```mermaid
graph TB
    A[API Request] --> B{Browser Cache?}
    B -->|Hit| C[Return 304 Not Modified]
    B -->|Miss| D{Redis Cache?}
    D -->|Hit| E[Return from Redis]
    D -->|Miss| F{Database Query}
    F --> G[Store in Redis]
    G --> H[Return to Client]
    H --> I[Set Cache Headers]
    
    style C fill:#9f9
    style E fill:#9f9
```

### Cache Invalidation

```mermaid
sequenceDiagram
    participant Scraper
    participant Database
    participant Cache
    participant API
    
    Scraper->>Database: Insert new products
    Database-->>Scraper: Success
    Scraper->>Cache: Invalidate product cache
    Cache-->>Scraper: Cache cleared
    
    Note over API: Next request will fetch fresh data
```

---

## 🚨 Error Handling Flow

```mermaid
graph TD
    A[Request] --> B{Valid?}
    B -->|No| C[400 Bad Request]
    B -->|Yes| D{Authenticated?}
    D -->|No| E[401 Unauthorized]
    D -->|Yes| F{Rate Limited?}
    F -->|Yes| G[429 Too Many Requests]
    F -->|No| H[Process Request]
    H --> I{Success?}
    I -->|No| J[500 Internal Error]
    I -->|Yes| K[200 OK]
    
    style C fill:#f99
    style E fill:#f99
    style G fill:#f99
    style J fill:#f99
    style K fill:#9f9
```

---

## 📊 Data Lifecycle

```mermaid
stateDiagram-v2
    [*] --> Scraped: Scraper extracts
    Scraped --> Validated: Passes validation
    Scraped --> Rejected: Fails validation
    Validated --> Enriched: Add metadata
    Enriched --> Stored: Save to DB
    Stored --> Cached: Add to cache
    Cached --> Served: API response
    Served --> Updated: Price changes
    Updated --> Stored
    Stored --> Archived: After 90 days
    Archived --> [*]
    Rejected --> [*]
```

---

## 🔄 Batch Processing

### Nightly Analytics Job

```mermaid
graph LR
    A[Cron Trigger] --> B[Fetch all products]
    B --> C[Calculate trends]
    C --> D[Detect outliers]
    D --> E[Generate insights]
    E --> F[Update cache]
    F --> G[Send alerts]
    G --> H[Log completion]
```

---

**Last Updated:** 2026-01-26  
**Version:** 2.0.0
