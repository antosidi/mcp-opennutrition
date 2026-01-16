"""SQLite Database Adapter for OpenNutrition."""

import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional


class FoodItem:
    """Represents a food item from the database."""

    def __init__(self, row: sqlite3.Row):
        """Initialize FoodItem from database row.

        Args:
            row: SQLite row containing food data
        """
        self.id = row['id']
        self.name = row['name']
        self.type = row['type']
        self.ean_13 = row['ean_13'] or ""

        # Parse JSON fields
        self.labels = self._parse_json(row['labels'])
        self.nutrition_100g = self._parse_json(row['nutrition_100g'])
        self.alternate_names = self._parse_json(row['alternate_names'])
        self.source = self._parse_json(row['source'])
        self.serving = self._parse_json(row['serving'])
        self.package_size = self._parse_json(row['package_size'])
        self.ingredient_analysis = self._parse_json(row['ingredient_analysis'])

    @staticmethod
    def _parse_json(value: Any) -> Any:
        """Parse JSON string or return None.

        Args:
            value: Value to parse

        Returns:
            Parsed JSON or None
        """
        if isinstance(value, str) and value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return None
        return value

    def to_dict(self) -> Dict[str, Any]:
        """Convert food item to dictionary.

        Returns:
            Dictionary representation of the food item
        """
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'ean_13': self.ean_13,
            'labels': self.labels,
            'nutrition_100g': self.nutrition_100g,
            'alternate_names': self.alternate_names,
            'source': self.source,
            'serving': self.serving,
            'package_size': self.package_size,
            'ingredient_analysis': self.ingredient_analysis,
        }


class SQLiteDBAdapter:
    """Adapter for accessing the OpenNutrition SQLite database."""

    def __init__(self, db_path: Optional[str] = None):
        """Initialize the database adapter.

        Args:
            db_path: Path to the SQLite database file. If None, uses default location.
        """
        if db_path is None:
            # Default path: project_root/data_local/opennutrition_foods.db
            current_dir = Path(__file__).parent
            project_root = current_dir.parent.parent
            db_path = project_root / 'data_local' / 'opennutrition_foods.db'

        self.db_path = str(db_path)
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row

    def _get_food_item_select_clause(self) -> str:
        """Get the SELECT clause for food items.

        Returns:
            SQL SELECT clause string
        """
        return """
            foods.id,
            foods.name,
            foods.type,
            foods.ean_13,
            json_extract(foods.labels, '$') as labels,
            json_extract(foods.nutrition_100g, '$') as nutrition_100g,
            json_extract(foods.alternate_names, '$') as alternate_names,
            json_extract(foods.source, '$') as source,
            json_extract(foods.serving, '$') as serving,
            json_extract(foods.package_size, '$') as package_size,
            json_extract(foods.ingredient_analysis, '$') as ingredient_analysis
        """

    def search_by_name(
        self,
        query: str,
        page: int = 1,
        page_size: int = 25
    ) -> List[Dict[str, Any]]:
        """Search foods by name or alternate name (case-insensitive, partial match).

        Args:
            query: Search query string
            page: Page number (1-indexed)
            page_size: Number of results per page

        Returns:
            List of food items matching the query
        """
        offset = (page - 1) * page_size
        select_clause = self._get_food_item_select_clause()

        # Fuzzy search: split query into words and match all with LIKE
        terms = query.strip().split()
        where_clauses = []
        params = []

        for term in terms:
            where_clauses.append(
                "(LOWER(foods.name) LIKE LOWER(?) OR LOWER(alt.value) LIKE LOWER(?))"
            )
            search_term = f"%{term}%"
            params.extend([search_term, search_term])

        where_clause = " AND ".join(where_clauses)
        params.extend([page_size, offset])

        query_sql = f"""
            SELECT DISTINCT {select_clause}
            FROM foods
            LEFT JOIN json_each(foods.alternate_names) AS alt ON 1 = 1
            WHERE {where_clause}
            LIMIT ? OFFSET ?
        """

        cursor = self.conn.execute(query_sql, params)
        rows = cursor.fetchall()

        return [FoodItem(row).to_dict() for row in rows]

    def get_all(self, page: int = 1, page_size: int = 25) -> List[Dict[str, Any]]:
        """Get all foods with pagination.

        Args:
            page: Page number (1-indexed)
            page_size: Number of results per page

        Returns:
            List of food items
        """
        offset = (page - 1) * page_size
        select_clause = self._get_food_item_select_clause()

        query_sql = f"""
            SELECT {select_clause}
            FROM foods
            LIMIT ? OFFSET ?
        """

        cursor = self.conn.execute(query_sql, [page_size, offset])
        rows = cursor.fetchall()

        return [FoodItem(row).to_dict() for row in rows]

    def get_by_id(self, food_id: str) -> Optional[Dict[str, Any]]:
        """Get a food by its ID.

        Args:
            food_id: The food ID (must start with 'fd_')

        Returns:
            Food item or None if not found
        """
        select_clause = self._get_food_item_select_clause()

        query_sql = f"""
            SELECT {select_clause}
            FROM foods
            WHERE id = ?
        """

        cursor = self.conn.execute(query_sql, [food_id])
        row = cursor.fetchone()

        return FoodItem(row).to_dict() if row else None

    def get_by_ean13(self, ean_13: str) -> Optional[Dict[str, Any]]:
        """Get a food by its EAN-13 barcode.

        Args:
            ean_13: The EAN-13 barcode (13 characters)

        Returns:
            Food item or None if not found
        """
        select_clause = self._get_food_item_select_clause()

        query_sql = f"""
            SELECT {select_clause}
            FROM foods
            WHERE ean_13 = ?
        """

        cursor = self.conn.execute(query_sql, [ean_13])
        row = cursor.fetchone()

        return FoodItem(row).to_dict() if row else None

    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
