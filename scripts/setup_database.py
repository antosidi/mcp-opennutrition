#!/usr/bin/env python3
"""Setup script to create the OpenNutrition SQLite database from the dataset."""

import csv
import json
import sqlite3
import zipfile
from pathlib import Path
from typing import Any, Dict


def decompress_dataset(data_dir: Path, temp_dir: Path) -> Path:
    """Decompress the OpenNutrition dataset.

    Args:
        data_dir: Directory containing the ZIP file
        temp_dir: Directory to extract files to

    Returns:
        Path to the extracted TSV file
    """
    zip_path = data_dir / "opennutrition-dataset-2025.1.zip"

    if not zip_path.exists():
        raise FileNotFoundError(f"Dataset not found: {zip_path}")

    print(f"Decompressing dataset from {zip_path}...")
    temp_dir.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)

    tsv_file = temp_dir / "opennutrition_foods.tsv"
    if not tsv_file.exists():
        raise FileNotFoundError(f"TSV file not found after extraction: {tsv_file}")

    print("Dataset decompressed successfully!")
    return tsv_file


def parse_json_field(value: str) -> Any:
    """Parse a JSON field value.

    Args:
        value: JSON string to parse

    Returns:
        Parsed JSON value or None
    """
    if not value or value == "":
        return None
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return None


def create_database(tsv_file: Path, db_path: Path):
    """Create SQLite database from TSV file.

    Args:
        tsv_file: Path to the TSV file
        db_path: Path where the database should be created
    """
    print(f"Reading TSV file: {tsv_file}...")

    # Read TSV file
    with open(tsv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        rows = list(reader)

    print(f"Found {len(reader.fieldnames)} columns and {len(rows)} data rows")

    # Create database directory
    db_path.parent.mkdir(parents=True, exist_ok=True)

    # Connect to database
    print(f"Creating database: {db_path}...")
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    # Create table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS foods (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            type TEXT,
            ean_13 TEXT,
            labels TEXT,
            nutrition_100g TEXT,
            alternate_names TEXT,
            source TEXT,
            serving TEXT,
            package_size TEXT,
            ingredient_analysis TEXT
        )
    """)

    print("Created foods table")

    # Insert data
    insert_count = 0
    for row in rows:
        # Convert JSON fields to strings
        labels = json.dumps(parse_json_field(row.get('labels', '')))
        nutrition_100g = json.dumps(parse_json_field(row.get('nutrition_100g', '')))
        alternate_names = json.dumps(parse_json_field(row.get('alternate_names', '')))
        source = json.dumps(parse_json_field(row.get('source', '')))
        serving = json.dumps(parse_json_field(row.get('serving', '')))
        package_size = json.dumps(parse_json_field(row.get('package_size', '')))
        ingredient_analysis = json.dumps(parse_json_field(row.get('ingredient_analysis', '')))

        cursor.execute("""
            INSERT OR REPLACE INTO foods (
                id, name, type, ean_13, labels, nutrition_100g,
                alternate_names, source, serving, package_size, ingredient_analysis
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            row.get('id', ''),
            row.get('name', ''),
            row.get('type', ''),
            row.get('ean_13', ''),
            labels,
            nutrition_100g,
            alternate_names,
            source,
            serving,
            package_size,
            ingredient_analysis
        ))

        insert_count += 1

    conn.commit()
    print(f"Inserted {insert_count} rows into database")

    conn.close()
    print("Database connection closed")


def main():
    """Main setup function."""
    # Get paths
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    data_dir = project_root / "data"
    temp_dir = project_root / "data_local_temp"
    db_dir = project_root / "data_local"
    db_path = db_dir / "opennutrition_foods.db"

    try:
        # Decompress dataset
        tsv_file = decompress_dataset(data_dir, temp_dir)

        # Create database
        create_database(tsv_file, db_path)

        print(f"\n✓ Successfully created database: {db_path}")
        print(f"✓ Database size: {db_path.stat().st_size / 1024 / 1024:.2f} MB")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        raise

    finally:
        # Clean up temp directory
        if temp_dir.exists():
            import shutil
            shutil.rmtree(temp_dir)
            print(f"✓ Cleaned up temporary files")


if __name__ == "__main__":
    main()
