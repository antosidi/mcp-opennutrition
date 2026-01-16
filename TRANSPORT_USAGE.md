# Transport Usage Guide

This guide shows how to use the MCP OpenNutrition server with different transports.

## Starting the Server

### Default (Streamable HTTP)

```bash
export PYTHONPATH="$(pwd)/src:$PYTHONPATH"
python3 -m mcp_opennutrition
```

Output:
```
MCP OpenNutrition Server running on http://127.0.0.1:8000
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

### With Custom Host/Port

```bash
python3 -m mcp_opennutrition --host 0.0.0.0 --port 3000
```

### Standard I/O Transport

```bash
python3 -m mcp_opennutrition --transport stdio
```

Output:
```
MCP OpenNutrition Server running on stdio
```

## Command-Line Options

```
$ python3 -m mcp_opennutrition --help

usage: __main__.py [-h] [--transport {stdio,streamable-http}] [--host HOST] [--port PORT]

MCP OpenNutrition Server - Food database via Model Context Protocol

options:
  -h, --help            show this help message and exit
  --transport {stdio,streamable-http}
                        Transport protocol to use (default: streamable-http)
  --host HOST           Host address for HTTP transport (default: 127.0.0.1)
  --port PORT           Port for HTTP transport (default: 8000)
```

## HTTP Transport Endpoints

When running with `--transport streamable-http`, the server exposes:

- **Base URL**: `http://{host}:{port}/mcp/v1`
- **SSE Endpoint**: `http://{host}:{port}/mcp/v1/sse`
- **Messages Endpoint**: `http://{host}:{port}/mcp/v1/messages`

## Usage Examples

### 1. With Claude Desktop (stdio)

Add to your Claude config file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "mcp-opennutrition": {
      "command": "python3",
      "args": ["-m", "mcp_opennutrition", "--transport", "stdio"],
      "env": {
        "PYTHONPATH": "/absolute/path/to/mcp-opennutrition/src"
      }
    }
  }
}
```

### 2. With HTTP Transport (Web Applications)

```python
import asyncio
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

async def main():
    server_url = "http://127.0.0.1:8000/mcp/v1"

    async with streamable_http_client(server_url) as client:
        async with ClientSession(*client) as session:
            await session.initialize()

            # List tools
            tools = await session.list_tools()
            for tool in tools.tools:
                print(f"Tool: {tool.name}")

            # Call a tool
            result = await session.call_tool("search-food-by-name", {
                "query": "banana",
                "page": 1,
                "pageSize": 5
            })

            import json
            foods = json.loads(result.content[0].text)
            for food in foods:
                print(f"- {food['name']}: {food['nutrition_100g'].get('calories')} kcal")

asyncio.run(main())
```

### 3. Direct Database Access (No Server)

```python
import sys
sys.path.insert(0, '/path/to/mcp-opennutrition/src')

from mcp_opennutrition import SQLiteDBAdapter

# Use database directly
with SQLiteDBAdapter() as db:
    # Search
    foods = db.search_by_name("apple", page=1, page_size=5)
    for food in foods:
        print(f"{food['name']}: {food['nutrition_100g'].get('calories')} kcal")

    # Get by ID
    food = db.get_by_id("fd_MJM2sOkBTOdx")
    print(f"Food: {food['name']}")

    # Get by barcode
    food = db.get_by_ean13("0049000042566")
    if food:
        print(f"Barcode food: {food['name']}")
```

## Testing the Server

### Test stdio Transport

```bash
# Terminal 1: Start server
export PYTHONPATH="$(pwd)/src:$PYTHONPATH"
python3 -m mcp_opennutrition --transport stdio

# Terminal 2: Run tests
export PYTHONPATH="$(pwd)/src:$PYTHONPATH"
pytest tests/test_server.py -v
```

### Test HTTP Transport

```bash
# Terminal 1: Start HTTP server
export PYTHONPATH="$(pwd)/src:$PYTHONPATH"
python3 -m mcp_opennutrition --transport streamable-http --port 8000

# The server is now running and ready to accept connections
# You can connect to it using the MCP HTTP client
```

## Choosing a Transport

### Use stdio when:
- Integrating with Claude Desktop or IDEs
- Building command-line tools
- Need process isolation
- Single client usage

### Use streamable-http when:
- Building web applications
- Need multiple concurrent clients
- Remote access required
- RESTful API integration
- Microservices architecture

## Production Deployment

### Systemd Service (stdio)

```ini
[Unit]
Description=MCP OpenNutrition Server (stdio)
After=network.target

[Service]
Type=simple
User=mcp
WorkingDirectory=/opt/mcp-opennutrition
Environment="PYTHONPATH=/opt/mcp-opennutrition/src"
ExecStart=/usr/bin/python3 -m mcp_opennutrition --transport stdio
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

### Systemd Service (HTTP)

```ini
[Unit]
Description=MCP OpenNutrition Server (HTTP)
After=network.target

[Service]
Type=simple
User=mcp
WorkingDirectory=/opt/mcp-opennutrition
Environment="PYTHONPATH=/opt/mcp-opennutrition/src"
ExecStart=/usr/bin/python3 -m mcp_opennutrition --transport streamable-http --host 127.0.0.1 --port 8000
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

### Docker (HTTP)

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY data_local/ ./data_local/

ENV PYTHONPATH=/app/src

EXPOSE 8000

CMD ["python3", "-m", "mcp_opennutrition", "--transport", "streamable-http", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t mcp-opennutrition .
docker run -p 8000:8000 mcp-opennutrition
```

## Performance Comparison

| Aspect | stdio | streamable-http |
|--------|-------|-----------------|
| Latency | Low (~1-5ms) | Medium (~10-50ms) |
| Throughput | Single client | Multiple clients |
| Network | Local only | Network accessible |
| Setup | Simple | Requires web server |
| Security | Process isolation | Requires auth/HTTPS |

## Troubleshooting

### Server Won't Start

**Error**: `Address already in use`

```bash
# Find process using the port
lsof -i :8000
# Kill it or use different port
python3 -m mcp_opennutrition --port 8001
```

### Module Not Found

**Error**: `No module named 'mcp_opennutrition'`

```bash
# Set PYTHONPATH
export PYTHONPATH="$(pwd)/src:$PYTHONPATH"
# Or install in development mode
pip install -e .
```

### HTTP Connection Refused

```bash
# Check if server is running
ps aux | grep mcp_opennutrition

# Check server logs
# Look at stderr output from the server process
```

## Summary

The MCP OpenNutrition server provides flexible transport options:

- **stdio**: Best for CLI/IDE integrations
- **streamable-http** (default): Best for web applications and APIs

Both transports provide identical functionality with the same 4 tools:
- search-food-by-name
- get-foods
- get-food-by-id
- get-food-by-ean13
