"""
JSON exporter

Exports product data to JSON format.
"""

import json
from typing import List, Optional
from pathlib import Path
from datetime import datetime

from src.backend.core.models import ProductInDB, ProductResponse
from src.utils.logger import get_logger

logger = get_logger(__name__)


class JSONExporter:
    """
    Exports data to JSON format
    
    Features:
    - Pretty printing
    - Nested data support
    - Pydantic model serialization
    """
    
    @staticmethod
    def export(
        products: List[ProductInDB],
        output_path: str,
        pretty: bool = True
    ) -> str:
        """
        Export products to JSON
        
        Args:
            products: List of products to export
            output_path: Path to output file
            pretty: Whether to pretty-print JSON
            
        Returns:
            Path to created file
        """
        # Ensure directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        logger.info("exporting_json", path=output_path, count=len(products))
        
        # Convert to response models for clean serialization
        data = [ProductResponse.from_db_model(p).model_dump() for p in products]
        
        with open(output_path, 'w', encoding='utf-8') as f:
            if pretty:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            else:
                json.dump(data, f, ensure_ascii=False, default=str)
        
        logger.info("json_exported", path=output_path, products=len(products))
        
        return output_path
    
    @staticmethod
    def export_with_metadata(
        products: List[ProductInDB],
        output_path: str,
        metadata: Optional[dict] = None
    ) -> str:
        """
        Export with metadata wrapper
        
        Args:
            products: List of products
            output_path: Path to output file
            metadata: Optional metadata to include
            
        Returns:
            Path to created file
        """
        # Ensure directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        data = [ProductResponse.from_db_model(p).model_dump() for p in products]
        
        output = {
            "metadata": metadata or {
                "exported_at": datetime.now().isoformat(),
                "count": len(products)
            },
            "products": data
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info("json_with_metadata_exported", path=output_path)
        
        return output_path
    
    @staticmethod
    def export_with_timestamp(
        products: List[ProductInDB],
        output_dir: str = "data/exports",
        filename_prefix: str = "products"
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
        filename = f"{filename_prefix}_{timestamp}.json"
        output_path = f"{output_dir}/{filename}"
        
        return JSONExporter.export(products, output_path)
