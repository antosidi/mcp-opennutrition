# MCP OpenNutrition Client Documentation

This document provides comprehensive documentation for the MCP OpenNutrition server, including setup, architecture, available tools, and examples of using a Python client to interact with the server.

## Table of Contents
- [Overview](#overview)
- [Architecture](#architecture)
- [Setup and Installation](#setup-and-installation)
- [Available Tools](#available-tools)
- [Python Client Implementation](#python-client-implementation)
- [Usage Examples](#usage-examples)
- [Database Information](#database-information)

---

## Overview

MCP OpenNutrition is a Model Context Protocol (MCP) server that provides access to a comprehensive food and nutrition database containing over 326,000 food items. The server offers nutritional data, barcode lookups, and search capabilities for foods from authoritative public sources including USDA, CNF, FRIDA, and AUSNUT.

### Key Features
- Search foods by name with fuzzy matching
- Browse foods with pagination
- Retrieve detailed nutritional information by food ID
- Lookup foods using EAN-13 barcodes
- Runs locally with no external API calls
- Fast SQLite-based data storage

---

## Architecture

### Server Components

The MCP server is built using TypeScript and consists of the following main components:

1. **index.ts** (src/index.ts:1)
   - Main server implementation
   - Defines 4 MCP tools with Zod schema validation
   - Uses stdio transport for communication

2. **SQLiteDBAdapter.ts** (src/SQLiteDBAdapter.ts:1)
   - Database adapter for SQLite operations
   - Handles all database queries and data serialization
   - Supports fuzzy search with multi-term matching

3. **Database**
   - SQLite database located at `data_local/opennutrition_foods.db`
   - Contains 326,759 food items
   - Stores nutritional data as JSON columns for flexible schema

### Communication Protocol

The server uses the Model Context Protocol (MCP) over stdio:
- **Transport**: StdioServerTransport
- **Communication**: JSON-RPC messages over stdin/stdout
- **Schema Validation**: Zod schemas for request parameters

---

## Setup and Installation

### Prerequisites
- Node.js (v20 or higher recommended)
- npm
- Python 3.10+ (for client usage)

### Building the Server

```bash
# Install dependencies
npm install

# Build the project (includes database setup)
npm run build
```

The build process:
1. Compiles TypeScript to JavaScript
2. Decompresses the dataset from the ZIP file
3. Converts TSV data to SQLite database
4. Makes the build/index.js file executable

Build output:
```
✓ Compiled TypeScript
✓ Decompressed dataset
✓ Created SQLite database with 326,759 rows
```

### Installing Python MCP Client

```bash
pip3 install mcp
```

The MCP Python library provides:
- ClientSession for managing connections
- StdioServerParameters for server configuration
- stdio_client context manager for stdio transport

---

## Available Tools

The MCP OpenNutrition server provides 4 tools:

### 1. search-food-by-name

Search for foods by name, brand, or partial matches with fuzzy matching.

**Parameters:**
```json
{
  "query": "string (required, min length: 1)",
  "page": "number (optional, default: 1, min: 1)",
  "pageSize": "number (optional, default: 5)"
}
```

**Features:**
- Case-insensitive search
- Multi-term matching (all terms must match)
- Searches both primary name and alternate names
- Results ordered by relevance
- Pagination support

**Example:**
```python
result = await session.call_tool("search-food-by-name", {
    "query": "apple",
    "page": 1,
    "pageSize": 3
})
```

**Response Structure:**
```json
[
  {
    "id": "fd_MJM2sOkBTOdx",
    "name": "Apples",
    "type": "everyday",
    "labels": ["fresh"],
    "nutrition_100g": {
      "calories": 52,
      "protein": 0.26,
      "carbohydrates": 13.81,
      "fiber": 2.4,
      "sugars": 10.39,
      "fat": 0.17,
      "sodium": 1,
      "calcium": 6,
      "iron": 0.12,
      ...
    },
    "alternate_names": ["Apple", "Red apple", ...],
    ...
  }
]
```

---

### 2. get-foods

Get paginated lists of all available foods for browsing.

**Parameters:**
```json
{
  "page": "number (optional, default: 1, min: 1)",
  "pageSize": "number (optional, default: 5)"
}
```

**Features:**
- Simple pagination through entire dataset
- No filtering applied
- Consistent ordering

**Example:**
```python
result = await session.call_tool("get-foods", {
    "page": 1,
    "pageSize": 10
})
```

**Response Structure:**
Same as search-food-by-name, returns array of food items.

---

### 3. get-food-by-id

Retrieve detailed nutritional information for a specific food using its ID.

**Parameters:**
```json
{
  "id": "string (required, must start with 'fd_')"
}
```

**Features:**
- Direct lookup by unique food ID
- Returns complete food object
- Fast indexed query

**Example:**
```python
result = await session.call_tool("get-food-by-id", {
    "id": "fd_MJM2sOkBTOdx"
})
```

**Response Structure:**
Returns single food object (same structure as array items above).

---

### 4. get-food-by-ean13

Find foods using EAN-13 barcode numbers.

**Parameters:**
```json
{
  "ean_13": "string (required, exactly 13 characters)"
}
```

**Features:**
- Lookup by standard EAN-13 barcode
- Useful for product identification
- Returns null if barcode not found

**Example:**
```python
result = await session.call_tool("get-food-by-ean13", {
    "ean_13": "0049000042566"
})
```

**Response Structure:**
Returns single food object with matching barcode.

**Example Response:**
```json
{
  "id": "fd_8IqTuBfjgeoF",
  "name": "Zero by Coca-Cola",
  "type": "grocery",
  "ean_13": "0049000042566",
  "labels": ["caffeine"],
  "nutrition_100g": {
    "calories": 0,
    "caffeine": 9.5775,
    "sodium": 11,
    ...
  }
}
```

---

## Python Client Implementation

### Basic Client Structure

```python
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    # Configure server parameters
    server_params = StdioServerParameters(
        command="node",
        args=["build/index.js"],
    )

    # Connect to server
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize session
            await session.initialize()

            # List available tools
            tools_list = await session.list_tools()

            # Call tools
            result = await session.call_tool("search-food-by-name", {
                "query": "apple"
            })

if __name__ == "__main__":
    asyncio.run(main())
```

### Client Components

1. **StdioServerParameters**
   - Configures the server process
   - Specifies command and arguments
   - Can include environment variables and working directory

2. **stdio_client**
   - Context manager that spawns server process
   - Handles stdio communication streams
   - Automatically cleans up on exit

3. **ClientSession**
   - Manages MCP session lifecycle
   - Provides methods for listing and calling tools
   - Handles JSON-RPC communication

---

## Usage Examples

### Complete Test Script

The repository includes `test_client.py` which demonstrates all tools:

```bash
python3 test_client.py
```

### Example 1: Search for Foods

```python
# Search for apple products
result = await session.call_tool("search-food-by-name", {
    "query": "apple",
    "page": 1,
    "pageSize": 3
})

# Parse results
import json
foods = json.loads(result.content[0].text)
for food in foods:
    print(f"{food['name']} (ID: {food['id']})")
    print(f"Calories: {food['nutrition_100g']['calories']} per 100g")
```

**Output:**
```
Apples (ID: fd_MJM2sOkBTOdx)
Calories: 52 per 100g
```

---

### Example 2: Get Detailed Food Information

```python
# Get detailed info for a specific food
result = await session.call_tool("get-food-by-id", {
    "id": "fd_MJM2sOkBTOdx"
})

food = json.loads(result.content[0].text)
print(f"Food: {food['name']}")
print(f"Type: {food['type']}")
print(f"Labels: {', '.join(food['labels'])}")
print("\nNutrition per 100g:")
for nutrient, value in food['nutrition_100g'].items():
    print(f"  {nutrient}: {value}")
```

---

### Example 3: Browse Foods with Pagination

```python
# Get first page
page1 = await session.call_tool("get-foods", {
    "page": 1,
    "pageSize": 5
})

# Get next page
page2 = await session.call_tool("get-foods", {
    "page": 2,
    "pageSize": 5
})
```

---

### Example 4: Barcode Lookup

```python
# Look up by barcode
result = await session.call_tool("get-food-by-ean13", {
    "ean_13": "0049000042566"
})

food = json.loads(result.content[0].text)
if food:
    print(f"Found: {food['name']}")
    print(f"Barcode: {food['ean_13']}")
else:
    print("Barcode not found in database")
```

---

### Example 5: Multi-term Search

```python
# Search with multiple terms (all must match)
result = await session.call_tool("search-food-by-name", {
    "query": "organic whole milk",
    "page": 1,
    "pageSize": 5
})

# Returns foods matching all three terms: organic, whole, and milk
```

---

## Database Information

### Database Schema

The SQLite database has a single `foods` table:

```sql
CREATE TABLE foods (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT,
    ean_13 TEXT,
    labels TEXT,  -- JSON array
    nutrition_100g TEXT,  -- JSON object
    alternate_names TEXT,  -- JSON array
    source TEXT,  -- JSON array
    serving TEXT,  -- JSON object
    package_size TEXT,  -- JSON object
    ingredient_analysis TEXT  -- JSON object
);
```

### Statistics
- Total foods: 326,759
- Database size: ~200 MB
- Location: `data_local/opennutrition_foods.db`

### Food Types
- **everyday**: Common everyday foods (e.g., fruits, vegetables, meats)
- **grocery**: Branded grocery products with barcodes
- **prepared**: Prepared or processed foods
- **restaurant**: Restaurant menu items

### Nutritional Data

Each food item includes comprehensive nutritional data per 100g:

**Macronutrients:**
- calories, protein, carbohydrates, fiber, sugars, fat

**Minerals:**
- calcium, iron, magnesium, phosphorus, potassium, sodium, zinc, copper, manganese, selenium

**Vitamins:**
- vitamin A, C, D, E, K, B vitamins (thiamin, riboflavin, niacin, etc.)

**Amino Acids:**
- All essential and non-essential amino acids

**Fatty Acids:**
- omega-3, omega-6, omega-9, saturated, monounsaturated, polyunsaturated

**Other:**
- caffeine, alcohol, water content, cholesterol

---

## Test Results

### Successful Test Run Output

```
================================================================================
MCP OpenNutrition Client Test
================================================================================

✓ Connected to MCP OpenNutrition Server

--------------------------------------------------------------------------------
AVAILABLE TOOLS
--------------------------------------------------------------------------------

1. search-food-by-name
   Input Schema: query (string), page (number), pageSize (number)

2. get-foods
   Input Schema: page (number), pageSize (number)

3. get-food-by-id
   Input Schema: id (string, pattern: ^fd_)

4. get-food-by-ean13
   Input Schema: ean_13 (string, length: 13)

================================================================================
TOOL USAGE EXAMPLES
================================================================================

Example 1: Search for 'apple' with search-food-by-name
✓ Found: Apples (fd_MJM2sOkBTOdx)

Example 2: Get list of foods with get-foods
✓ Retrieved: Chicken Breast, Boneless Skinless, Cooked

Example 3: Get food by ID with get-food-by-id
✓ Retrieved: Apples by ID fd_MJM2sOkBTOdx

Example 4: Get food by EAN-13 barcode with get-food-by-ean13
✓ Retrieved: Zero by Coca-Cola (barcode: 0049000042566)

================================================================================
✓ All tests completed successfully!
================================================================================
```

---

## Troubleshooting

### Common Issues

1. **Server won't start**
   - Ensure `npm run build` completed successfully
   - Check that `data_local/opennutrition_foods.db` exists
   - Verify Node.js version is compatible (v20+)

2. **Database not found**
   - Run `npm run convert-data` to rebuild database
   - Check file permissions on `data_local` directory

3. **Python client connection fails**
   - Verify `mcp` library is installed: `pip3 list | grep mcp`
   - Check that node path in StdioServerParameters is correct
   - Ensure build/index.js is executable

4. **Empty search results**
   - Database may not be properly populated
   - Try broader search terms
   - Check spelling and case (search is case-insensitive)

---

## Performance Considerations

- **Search Performance**: SQLite with LIKE queries. Multi-term searches may be slower.
- **Memory Usage**: Database is ~200MB, loaded into memory for queries
- **Concurrency**: Single SQLite connection, readonly mode
- **Response Times**:
  - ID lookup: < 10ms
  - Search queries: 50-200ms depending on complexity
  - Pagination: Minimal overhead

---

## License

The OpenNutrition dataset is provided under:
- Database Contents License (DbCL)
- Open Database License (ODbL)

See LICENSE-DbCL.txt and LICENSE-ODbL.txt for details.

The MCP server code is provided under GNU General Public License v3.

---

## Additional Resources

- [OpenNutrition Dataset](https://www.opennutrition.app/)
- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)

---

## Summary

The MCP OpenNutrition server provides a powerful, local-first solution for accessing comprehensive nutritional data. With 326,000+ food items from authoritative sources, it offers:

- ✅ Fast, local queries with no external API calls
- ✅ Comprehensive nutritional data including macros, vitamins, minerals, and amino acids
- ✅ Flexible search with fuzzy matching and pagination
- ✅ Barcode lookup support for grocery products
- ✅ Easy integration via MCP protocol
- ✅ Python client library with async support

The included test client demonstrates all functionality and can be used as a starting point for integration into your own applications.
