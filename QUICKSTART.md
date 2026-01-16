# Quick Start Guide

Get up and running with MCP OpenNutrition in 5 minutes.

## Prerequisites

- Python 3.10 or higher
- pip package manager

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/mcp-opennutrition.git
cd mcp-opennutrition
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Up the Database

```bash
python scripts/setup_database.py
```

This will extract and process the OpenNutrition dataset (~2-3 minutes).

## Running the Server

### Option 1: Direct Execution

```bash
export PYTHONPATH="$(pwd)/src:$PYTHONPATH"
python3 -m mcp_opennutrition
```

### Option 2: With Claude Desktop

Add to your Claude config (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "mcp-opennutrition": {
      "command": "python3",
      "args": ["-m", "mcp_opennutrition"],
      "env": {
        "PYTHONPATH": "/absolute/path/to/mcp-opennutrition/src"
      }
    }
  }
}
```

## Testing

```bash
# Set Python path
export PYTHONPATH="$(pwd)/src:$PYTHONPATH"

# Run tests
pytest tests/

# Or use the test script
./run_tests.sh
```

## Using as a Library

```python
import sys
sys.path.insert(0, '/path/to/mcp-opennutrition/src')

from mcp_opennutrition import SQLiteDBAdapter

with SQLiteDBAdapter() as db:
    # Search for foods
    foods = db.search_by_name("banana", page=1, page_size=5)
    print(foods)

    # Get food by ID
    food = db.get_by_id("fd_AjQa9nlOUTns")
    print(food)
```

## Example Queries

### Search for Foods

```python
# Multi-term search
foods = db.search_by_name("organic whole milk")

# Simple search with pagination
foods = db.search_by_name("apple", page=2, page_size=10)
```

### Get Nutritional Data

```python
# Get detailed food info
food = db.get_by_id("fd_MJM2sOkBTOdx")
calories = food['nutrition_100g']['calories']
protein = food['nutrition_100g']['protein']
```

### Barcode Lookup

```python
# Find food by barcode
food = db.get_by_ean13("0049000042566")
print(f"Found: {food['name']}")
```

## Common Issues

### Database Not Found

**Error**: `unable to open database file`

**Solution**: Run the database setup script:
```bash
python scripts/setup_database.py
```

### Module Not Found

**Error**: `No module named 'mcp_opennutrition'`

**Solution**: Add src to Python path:
```bash
export PYTHONPATH="$(pwd)/src:$PYTHONPATH"
```

### MCP Package Not Installed

**Error**: `No module named 'mcp'`

**Solution**: Install dependencies:
```bash
pip install -r requirements.txt
```

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check [tests/](tests/) for more usage examples
- Explore the API in [src/mcp_opennutrition/](src/mcp_opennutrition/)

## Support

- **Issues**: https://github.com/yourusername/mcp-opennutrition/issues
- **Documentation**: See [docs/](docs/) for detailed guides
