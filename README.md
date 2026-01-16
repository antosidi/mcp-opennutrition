# MCP OpenNutrition

A Model Context Protocol (MCP) server providing access to the comprehensive OpenNutrition food database with 300,000+ food items, nutritional data, and barcode lookups.

## Features

- 🔍 **Search by Name**: Find foods with fuzzy matching and pagination
- 📋 **Browse Foods**: Get paginated lists of all available foods
- 🆔 **Get by ID**: Retrieve detailed nutritional information using food IDs
- 📱 **Barcode Lookup**: Find foods using EAN-13 barcodes
- 🗄️ **Local Database**: Runs fully locally with no external API calls
- ⚡ **Fast**: SQLite-based with optimized queries
- 🐍 **Pure Python**: No Node.js or JavaScript dependencies

## Installation

### Quick Install

```bash
# Clone the repository
git clone https://github.com/antosidi/mcp-opennutrition.git
cd mcp-opennutrition

# Install the package
pip install -e .
```

### Development Install

```bash
# Install with development dependencies
pip install -e ".[dev]"
```

## Database Setup

The first time you use the server, you need to set up the database:

```bash
# Run the database setup script
python scripts/setup_database.py
```

This will:
1. Extract the OpenNutrition dataset from `data/opennutrition-dataset-2025.1.zip`
2. Create a SQLite database at `data_local/opennutrition_foods.db`
3. Import 326,759 food items with complete nutritional data

## Usage

### Running the Server

```bash
# Run the MCP server
python -m mcp_opennutrition
```

Or use the installed command:

```bash
mcp-opennutrition
```

### Using with Claude Desktop

Add to your Claude desktop config file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "mcp-opennutrition": {
      "command": "python3",
      "args": ["-m", "mcp_opennutrition"]
    }
  }
}
```

### Using as a Python Library

```python
from mcp_opennutrition import SQLiteDBAdapter

# Use the database adapter directly
with SQLiteDBAdapter() as db:
    # Search for foods
    foods = db.search_by_name("apple", page=1, page_size=10)

    # Get food by ID
    food = db.get_by_id("fd_MJM2sOkBTOdx")

    # Get food by barcode
    food = db.get_by_ean13("0049000042566")
```

## Available Tools

### 1. search-food-by-name

Search for foods by name with fuzzy matching.

**Parameters:**
- `query` (string, required): Search query
- `page` (number, optional, default: 1): Page number
- `pageSize` (number, optional, default: 5): Results per page

**Example:**
```python
{
    "query": "organic apple",
    "page": 1,
    "pageSize": 10
}
```

### 2. get-foods

Get paginated list of all foods.

**Parameters:**
- `page` (number, optional, default: 1): Page number
- `pageSize` (number, optional, default: 5): Results per page

### 3. get-food-by-id

Get detailed information for a specific food.

**Parameters:**
- `id` (string, required): Food ID (must start with "fd_")

**Example:**
```python
{
    "id": "fd_MJM2sOkBTOdx"
}
```

### 4. get-food-by-ean13

Look up food by EAN-13 barcode.

**Parameters:**
- `ean_13` (string, required): 13-character barcode

**Example:**
```python
{
    "ean_13": "0049000042566"
}
```

## Development

### Running Tests

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=mcp_opennutrition

# Run tests with verbose output
pytest -v
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint code
ruff check src/ tests/

# Type checking
mypy src/
```

### Project Structure

```
mcp-opennutrition/
├── src/
│   └── mcp_opennutrition/      # Main package
│       ├── __init__.py          # Package initialization
│       ├── __main__.py          # CLI entry point
│       ├── server.py            # MCP server implementation
│       └── db_adapter.py        # Database adapter
├── tests/                       # Test suite
│   ├── __init__.py
│   ├── conftest.py              # Pytest configuration
│   └── test_server.py           # Server tests
├── scripts/                     # Utility scripts
│   └── setup_database.py        # Database setup
├── data/                        # Dataset files
│   └── opennutrition-dataset-2025.1.zip
├── data_local/                  # Generated database
│   └── opennutrition_foods.db
├── docs/                        # Documentation
├── pyproject.toml               # Project configuration
├── requirements.txt             # Core dependencies
├── requirements-dev.txt         # Development dependencies
└── README.md                    # This file
```

## Data Source

This server uses the [OpenNutrition dataset](https://www.opennutrition.app/), which provides:

- 326,759 food items
- Comprehensive nutritional profiles
- Data from authoritative sources (USDA, CNF, FRIDA, AUSNUT)
- Transparent and accurate nutritional data
- Free and open access

## License

- **Code**: GNU General Public License v3.0 or later (GPL-3.0-or-later)
- **Database**: Database Contents License (DbCL) and Open Database License (ODbL)

See [LICENSE](LICENSE) for code license details.
See [data/LICENSE-DbCL.txt](data/LICENSE-DbCL.txt) and [data/LICENSE-ODbL.txt](data/LICENSE-ODbL.txt) for database license details.

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass (`pytest`)
6. Format code (`black`, `ruff`)
7. Submit a pull request

## Support

- **Issues**: Report bugs or request features on [GitHub Issues](https://github.com/yourusername/mcp-opennutrition/issues)
- **Documentation**: See [docs/](docs/) for detailed documentation
- **Examples**: Check [tests/](tests/) for usage examples

## Acknowledgments

- OpenNutrition team for the comprehensive food database
- Model Context Protocol for the standardized protocol
- Python MCP SDK for the server implementation

## Changelog

### Version 1.0.0

- Initial release
- Python-only implementation
- 4 MCP tools for food data access
- 326,759 food items in database
- Comprehensive test suite
- Full documentation
