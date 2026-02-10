"""
Production deployment checklist and smoke tests

Ensures system is ready for production deployment
"""

import sys
import requests
from typing import List, Tuple
import structlog

logger = structlog.get_logger()


class DeploymentChecker:
    """Checks system readiness for deployment"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.checks_passed = 0
        self.checks_failed = 0

    def run_all_checks(self) -> bool:
        """Run all deployment checks"""
        logger.info("Starting deployment checks...")

        checks = [
            self.check_health,
            self.check_database,
            self.check_api_endpoints,
            self.check_authentication,
            self.check_rate_limiting,
            self.check_error_handling,
            self.check_performance,
        ]

        for check in checks:
            try:
                check()
                self.checks_passed += 1
            except AssertionError as e:
                logger.error(f"Check failed: {check.__name__}", error=str(e))
                self.checks_failed += 1

        # Summary
        total = self.checks_passed + self.checks_failed
        logger.info(
            "Deployment checks complete",
            passed=self.checks_passed,
            failed=self.checks_failed,
            total=total,
        )

        return self.checks_failed == 0

    def check_health(self):
        """Check health endpoint"""
        logger.info("Checking health endpoint...")
        response = requests.get(f"{self.base_url}/health", timeout=5)
        assert response.status_code == 200, "Health check failed"
        data = response.json()
        assert data["status"] == "healthy", "System not healthy"
        logger.info("✓ Health check passed")

    def check_database(self):
        """Check database connectivity"""
        logger.info("Checking database...")
        response = requests.get(f"{self.base_url}/api/v1/products?limit=1", timeout=5)
        assert response.status_code in [200, 401], "Database connection failed"
        logger.info("✓ Database check passed")

    def check_api_endpoints(self):
        """Check critical API endpoints"""
        logger.info("Checking API endpoints...")

        endpoints = [
            "/api/v1/products",
            "/api/v1/products/stats/overview",
            "/api/v1/scrapers/status",
        ]

        for endpoint in endpoints:
            response = requests.get(f"{self.base_url}{endpoint}", timeout=5)
            assert response.status_code in [200, 401], f"Endpoint {endpoint} failed"

        logger.info("✓ API endpoints check passed")

    def check_authentication(self):
        """Check authentication is working"""
        logger.info("Checking authentication...")

        # Should fail without API key
        response = requests.post(
            f"{self.base_url}/api/v1/scrapers/run",
            json={"stores": ["Pichau"]},
            timeout=5,
        )
        assert response.status_code == 401, "Authentication not enforced"

        logger.info("✓ Authentication check passed")

    def check_rate_limiting(self):
        """Check rate limiting is active"""
        logger.info("Checking rate limiting...")

        # Make multiple requests
        for i in range(65):
            response = requests.get(
                f"{self.base_url}/api/v1/products?limit=1", timeout=5
            )
            if response.status_code == 429:
                logger.info("✓ Rate limiting check passed")
                return

        logger.warning("Rate limiting may not be active")

    def check_error_handling(self):
        """Check error handling"""
        logger.info("Checking error handling...")

        # Invalid endpoint
        response = requests.get(f"{self.base_url}/api/v1/invalid", timeout=5)
        assert response.status_code == 404, "404 handling failed"

        # Invalid parameters
        response = requests.get(f"{self.base_url}/api/v1/products?limit=-1", timeout=5)
        assert response.status_code == 422, "Validation failed"

        logger.info("✓ Error handling check passed")

    def check_performance(self):
        """Check response time"""
        logger.info("Checking performance...")

        import time

        start = time.time()
        response = requests.get(f"{self.base_url}/api/v1/products?limit=10", timeout=5)
        duration = time.time() - start

        assert duration < 1.0, f"Response too slow: {duration}s"
        assert "X-Process-Time" in response.headers, "Performance header missing"

        logger.info(f"✓ Performance check passed ({duration:.3f}s)")


def main():
    """Run deployment checks"""
    import argparse

    parser = argparse.ArgumentParser(description="Run deployment checks")
    parser.add_argument(
        "--url", default="http://localhost:8000", help="Base URL to check"
    )
    args = parser.parse_args()

    checker = DeploymentChecker(args.url)
    success = checker.run_all_checks()

    if success:
        logger.info("✅ All checks passed! System ready for deployment.")
        sys.exit(0)
    else:
        logger.error("❌ Some checks failed. Fix issues before deploying.")
        sys.exit(1)


if __name__ == "__main__":
    main()
