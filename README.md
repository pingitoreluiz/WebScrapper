# GPU Price Scraper 🕷️

A robust, containerized web scraper for monitoring GPU prices across major Brazilian retailers (Pichau, Kabum, Terabyte). Built with FastAPI, Playwright, and Vanilla JS.

![Dashboard Preview](docs/dashboard-preview.png)

## 🚀 Features

- **Multi-Store Support:** Monitors Pichau, Kabum, and Terabyte.
- **Anti-Detection:** Uses `playwright-stealth` and human-like interactions to bypass bot protections.
- **Robust Backend:** FastAPI architecture with Pydantic validation and SQLAlchemy persistence.
- **Modern Dashboard:** Real-time statistics, product search, and scraper control via a responsive UI.
- **Docker Ready:** Full containerization with `docker-compose` for easy deployment.

## 🛠️ Tech Stack

- **Backend:** Python 3.10+, FastAPI, SQLAlchemy, Playwright
- **Frontend:** HTML5, CSS3, Vanilla JS (No build steps required!)
- **Database:** SQLite (Default) / PostgreSQL (Supported)
- **Infrastructure:** Docker, Docker Compose, Nginx

## 📦 Installation & Usage

### Prerequisites

- Docker Desktop installed
- Git

### Quick Start (Production/Release)

1. **Clone the repository:**

    ```bash
    git clone https://github.com/yourusername/gpu-price-scraper.git
    cd gpu-price-scraper
    ```

2. **Configure Environment:**

    ```bash
    cp .env.example .env
    # Edit .env if needed (Default settings work out of the box)
    ```

3. **Run with Docker Compose:**

    ```bash
    docker-compose up -d --build
    ```

4. **Access the Dashboard:**
    Open [http://localhost](http://localhost) in your browser.

    - **Run Scraper:** Click "Executar Scraper" on the dashboard.
    - **API Docs:** Available at [http://localhost:8000/docs](http://localhost:8000/docs).

## 📂 Project Structure

```
├── data/               # Database storage (mounted volume)
├── logs/               # Application logs (mounted volume)
├── scripts/            # Helper scripts (e.g., verification)
├── src/
│   ├── backend/        # FastAPI Application
│   ├── frontend/       # Static Website (HTML/JS/CSS)
│   └── scrapers/       # Scraper Mechanics & Factory
├── docker-compose.yml  # Container Orchestration
└── Dockerfile          # Backend Image Definition
```

## 🤝 Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## 📄 License

[MIT](https://choosealicense.com/licenses/mit/)
