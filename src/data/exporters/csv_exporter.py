"""
CSV exporter

Exports product data to CSV format.
"""

import csv
from typing import List, Optional
from pathlib import Path
from datetime import datetime

from src.backend.core.models import ProductInDB
from src.utils.logger import get_logger

logger = get_logger(__name__)


class CSVExporter:
    """
    Exports data to CSV format

    Features:
    - Customizable columns
    - UTF-8 encoding
    - Excel compatibility
    """

    DEFAULT_COLUMNS = [
        "id",
        "title",
        "price",
        "url",
        "store",
        "chip_brand",
        "manufacturer",
        "model",
        "scraped_at",
        "created_at",
    ]

    @staticmethod
    def export(
        products: List[ProductInDB],
        output_path: str,
        columns: Optional[List[str]] = None,
    ) -> str:
        """
        Export products to CSV

        Args:
            products: List of products to export
            output_path: Path to output file
            columns: Optional list of columns to include

        Returns:
            Path to created file
        """
        if columns is None:
            columns = CSVExporter.DEFAULT_COLUMNS

        # Ensure directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        logger.info("exporting_csv", path=output_path, count=len(products))

        with open(output_path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=columns)
            writer.writeheader()

            for product in products:
                row = {}
                for col in columns:
                    if col == "price":
                        row[col] = float(product.price.value)
                    elif col == "url":
                        row[col] = str(product.url)
                    elif col == "chip_brand":
                        row[col] = product.chip_brand.value
                    elif col == "store":
                        row[col] = product.store.value
                    elif col in ["scraped_at", "created_at", "updated_at"]:
                        date_val = getattr(product, col)
                        row[col] = date_val.isoformat() if date_val else ""
                    else:
                        row[col] = getattr(product, col, "")

                writer.writerow(row)

        logger.info("csv_exported", path=output_path, rows=len(products))

        return output_path

    @staticmethod
    def export_with_filters(
        products: List[ProductInDB],
        output_dir: str = "data/exports",
        filename_prefix: str = "products",
    ) -> str:
        """
        Export with automatic filename

        Args:
            products: List of products
            output_dir: Output directory
            filename_prefix: Filename prefix

        Returns:
            Path to created file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{filename_prefix}_{timestamp}.csv"
        output_path = f"{output_dir}/{filename}"

        return CSVExporter.export(products, output_path)
