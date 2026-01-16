# Changes Summary - Transport Support

This document summarizes the changes made to add transport selection support.

## What Was Added

### 1. Command-Line Transport Selection

Added `--transport` argument to choose between:
- `stdio` - Standard input/output transport
- `streamable-http` - HTTP-based transport (default)

### 2. Server Updates

**File**: `src/mcp_opennutrition/server.py`

**Changes:**
- Added `argparse` for command-line argument parsing
- Added `TransportType` type hint
- Split `run()` method into:
  - `run_stdio()` - For stdio transport
  - `run_http()` - For HTTP transport
  - `run()` - Main method that dispatches to appropriate transport
- Added `--host` and `--port` options for HTTP transport
- Updated `main()` to parse arguments and configure server

**New imports:**
```python
import argparse
from typing import Literal
from mcp.server.streamable_http import StreamableHTTPServerTransport
from starlette.applications import Starlette
from starlette.routing import Route
import uvicorn
```

### 3. Dependencies

**Updated**: `requirements.txt`

**Added:**
- `uvicorn>=0.31.1` - ASGI web server for HTTP transport
- `starlette>=0.27.0` - Web framework for HTTP routes

### 4. Documentation

**New Files:**
- `HTTP_TRANSPORT_GUIDE.md` - Comprehensive guide for HTTP transport
- `TRANSPORT_USAGE.md` - Quick reference for using both transports
- `CHANGES_SUMMARY.md` - This file

**Updated Files:**
- `README.md` - Added transport information
- `QUICKSTART.md` - Updated with transport options

### 5. Test Files

**Created:**
- `tests/test_http_client.py` - Full HTTP client test suite
- `test_http_simple.py` - Simplified HTTP client test

## Usage

### Starting Server with stdio (for Claude Desktop)

```bash
export PYTHONPATH="$(pwd)/src:$PYTHONPATH"
python3 -m mcp_opennutrition --transport stdio
```

### Starting Server with HTTP (default)

```bash
export PYTHONPATH="$(pwd)/src:$PYTHONPATH"
python3 -m mcp_opennutrition

# Or explicitly:
python3 -m mcp_opennutrition --transport streamable-http --host 127.0.0.1 --port 8000
```

### View Help

```bash
python3 -m mcp_opennutrition --help
```

Output:
```
usage: __main__.py [-h] [--transport {stdio,streamable-http}] [--host HOST] [--port PORT]

MCP OpenNutrition Server - Food database via Model Context Protocol

options:
  -h, --help            show this help message and exit
  --transport {stdio,streamable-http}
                        Transport protocol to use (default: streamable-http)
  --host HOST           Host address for HTTP transport (default: 127.0.0.1)
  --port PORT           Port for HTTP transport (default: 8000)
```

## Technical Details

### HTTP Transport Implementation

The HTTP transport uses:
1. **Starlette** - ASGI web framework for routing
2. **Uvicorn** - ASGI server for serving HTTP
3. **StreamableHTTPServerTransport** - MCP's HTTP transport layer

Routes:
- `/mcp/v1/sse` - Server-Sent Events endpoint
- `/mcp/v1/messages` - Messages endpoint (POST)

### Architecture

```
┌─────────────────────────────────────────┐
│          MCP OpenNutrition              │
│                Server                   │
├─────────────────────────────────────────┤
│                                         │
│  ┌──────────────┐   ┌──────────────┐   │
│  │    stdio     │   │    HTTP      │   │
│  │  Transport   │   │  Transport   │   │
│  └──────────────┘   └──────────────┘   │
│         │                  │            │
│         └──────┬───────────┘            │
│                │                        │
│        ┌───────▼────────┐               │
│        │  MCP Server    │               │
│        │   (4 tools)    │               │
│        └───────┬────────┘               │
│                │                        │
│        ┌───────▼────────┐               │
│        │  SQLite DB     │               │
│        │  Adapter       │               │
│        └────────────────┘               │
└─────────────────────────────────────────┘
```

### Default Transport Change

The default transport is now `streamable-http` instead of `stdio` because:

1. **Web-friendly** - Easier to integrate with web applications
2. **Testing** - Easier to test with HTTP clients
3. **Multiple clients** - Supports concurrent connections
4. **Modern** - Aligns with modern API patterns

For Claude Desktop and CLI usage, explicitly specify `--transport stdio`.

## Examples

### Claude Desktop Configuration

```json
{
  "mcpServers": {
    "mcp-opennutrition": {
      "command": "python3",
      "args": [
        "-m", "mcp_opennutrition",
        "--transport", "stdio"
      ],
      "env": {
        "PYTHONPATH": "/absolute/path/to/mcp-opennutrition/src"
      }
    }
  }
}
```

### Web Application Integration

```python
import asyncio
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

async def search_foods(query: str):
    async with streamable_http_client("http://127.0.0.1:8000/mcp/v1") as client:
        async with ClientSession(*client) as session:
            await session.initialize()
            result = await session.call_tool("search-food-by-name", {
                "query": query,
                "page": 1,
                "pageSize": 10
            })
            import json
            return json.loads(result.content[0].text)
```

### Direct Database Access (No Transport)

```python
from mcp_opennutrition import SQLiteDBAdapter

with SQLiteDBAdapter() as db:
    foods = db.search_by_name("banana", page=1, page_size=5)
    print(foods)
```

## Testing

### Test stdio Transport

```bash
export PYTHONPATH="$(pwd)/src:$PYTHONPATH"

# Terminal 1: Start server
python3 -m mcp_opennutrition --transport stdio

# Terminal 2: Run tests
pytest tests/test_server.py -v
```

### Test HTTP Transport

```bash
export PYTHONPATH="$(pwd)/src:$PYTHONPATH"

# Terminal 1: Start server
python3 -m mcp_opennutrition --transport streamable-http

# Terminal 2: Test with HTTP client
python3 test_http_simple.py
```

## Backward Compatibility

### Before (stdio only)

```bash
python3 -m mcp_opennutrition
# Defaulted to stdio
```

### After (HTTP default)

```bash
python3 -m mcp_opennutrition
# Defaults to streamable-http on port 8000

# To use stdio (old behavior):
python3 -m mcp_opennutrition --transport stdio
```

## Benefits

### For Developers

1. **Easier Testing** - HTTP is easier to test and debug
2. **Web Integration** - Direct HTTP API access
3. **Multiple Clients** - Support concurrent connections
4. **Standard Protocols** - Uses HTTP/SSE standards

### For Users

1. **Flexibility** - Choose the right transport for your use case
2. **Web Access** - Can access from web applications
3. **Remote Access** - HTTP allows network access (with proper security)
4. **Standard Tools** - Can use curl, Postman, etc. for testing

## Files Modified

1. `src/mcp_opennutrition/server.py` - Added transport selection
2. `src/mcp_opennutrition/__main__.py` - Updated for argument passing
3. `requirements.txt` - Added uvicorn and starlette
4. `README.md` - Updated with transport information
5. `QUICKSTART.md` - Added transport instructions

## Files Added

1. `HTTP_TRANSPORT_GUIDE.md` - HTTP transport guide
2. `TRANSPORT_USAGE.md` - Transport usage reference
3. `CHANGES_SUMMARY.md` - This file
4. `tests/test_http_client.py` - HTTP client tests
5. `test_http_simple.py` - Simple HTTP test

## Summary

The MCP OpenNutrition server now supports two transports:

- ✅ **stdio** - For CLI and IDE integrations
- ✅ **streamable-http** (default) - For web applications and APIs

Both provide identical functionality with the same 4 tools. The default is now HTTP for better web integration, but stdio remains fully supported for traditional use cases.
