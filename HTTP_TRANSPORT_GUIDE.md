# HTTP Transport Guide

This guide explains how to use MCP OpenNutrition with the streamable-http transport.

## Overview

The MCP OpenNutrition server supports two transport protocols:

1. **stdio** - Standard input/output (for CLI and IDE integrations)
2. **streamable-http** - HTTP-based transport (for web applications and APIs)

## Starting the Server

### Streamable HTTP (Default)

```bash
# Start with default settings (http://127.0.0.1:8000)
export PYTHONPATH="$(pwd)/src:$PYTHONPATH"
python3 -m mcp_opennutrition

# Or specify custom host/port
python3 -m mcp_opennutrition --transport streamable-http --host 0.0.0.0 --port 3000
```

### Standard I/O

```bash
# Start with stdio transport
python3 -m mcp_opennutrition --transport stdio
```

## Command-Line Options

```
usage: mcp_opennutrition [-h] [--transport {stdio,streamable-http}]
                         [--host HOST] [--port PORT]

MCP OpenNutrition Server - Food database via Model Context Protocol

optional arguments:
  -h, --help            show this help message and exit
  --transport {stdio,streamable-http}
                        Transport protocol to use (default: streamable-http)
  --host HOST           Host address for HTTP transport (default: 127.0.0.1)
  --port PORT           Port for HTTP transport (default: 8000)
```

## Using HTTP Transport

### Starting the Server

```bash
# Terminal 1: Start the server
export PYTHONPATH="$(pwd)/src:$PYTHONPATH"
python3 -m mcp_opennutrition --transport streamable-http

# Output:
# MCP OpenNutrition Server running on http://127.0.0.1:8000
```

### Testing with Python Client

```bash
# Terminal 2: Run the test client
export PYTHONPATH="$(pwd)/src:$PYTHONPATH"
python3 tests/test_http_client.py
```

The test client will:
- Connect to the HTTP server
- List all available tools
- Execute example calls for each tool
- Display results in pretty format

### Example Client Code

```python
import asyncio
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

async def main():
    server_url = "http://127.0.0.1:8000/mcp/v1"

    async with streamable_http_client(server_url) as client:
        async with ClientSession(*client) as session:
            # Initialize
            await session.initialize()

            # List tools
            tools = await session.list_tools()
            print(f"Available tools: {len(tools.tools)}")

            # Call a tool
            result = await session.call_tool("search-food-by-name", {
                "query": "banana",
                "page": 1,
                "pageSize": 5
            })

            # Process result
            import json
            foods = json.loads(result.content[0].text)
            for food in foods:
                print(f"- {food['name']}")

asyncio.run(main())
```

## HTTP Endpoints

When running with streamable-http transport, the server exposes:

- **Base URL**: `http://{host}:{port}/mcp/v1`
- **Protocol**: MCP over HTTP with Server-Sent Events (SSE)

## Integration Examples

### With Web Application

```javascript
// JavaScript example using fetch API
async function searchFoods(query) {
    const response = await fetch('http://127.0.0.1:8000/mcp/v1', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            tool: 'search-food-by-name',
            arguments: {
                query: query,
                page: 1,
                pageSize: 10
            }
        })
    });

    return await response.json();
}
```

### With FastAPI

```python
from fastapi import FastAPI
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

app = FastAPI()

@app.get("/search/{query}")
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

### With Streamlit

```python
import streamlit as st
import asyncio
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

st.title("Food Nutrition Search")

query = st.text_input("Search for a food:")

if query:
    async def search():
        async with streamable_http_client("http://127.0.0.1:8000/mcp/v1") as client:
            async with ClientSession(*client) as session:
                await session.initialize()
                result = await session.call_tool("search-food-by-name", {
                    "query": query,
                    "page": 1,
                    "pageSize": 5
                })
                import json
                return json.loads(result.content[0].text)

    foods = asyncio.run(search())

    for food in foods:
        st.write(f"**{food['name']}**")
        st.write(f"Calories: {food['nutrition_100g'].get('calories', 'N/A')} kcal/100g")
```

## Comparing Transports

### stdio Transport

**Use when:**
- Integrating with CLI tools
- Using with Claude Desktop or similar IDEs
- Building command-line applications
- Need process isolation

**Pros:**
- Simple and lightweight
- Good for process-based integrations
- Standard Unix pipes

**Cons:**
- Limited to single process communication
- Not suitable for web applications

### streamable-http Transport

**Use when:**
- Building web applications
- Need remote access
- Multiple clients connecting
- RESTful API integration

**Pros:**
- Web-friendly
- Multiple concurrent clients
- Easy to test with curl/Postman
- Works across network

**Cons:**
- Requires running web server
- More complex setup
- Network overhead

## Production Deployment

### With Docker

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ ./src/
COPY data_local/ ./data_local/

ENV PYTHONPATH=/app/src

CMD ["python3", "-m", "mcp_opennutrition", "--transport", "streamable-http", "--host", "0.0.0.0", "--port", "8000"]
```

### With Docker Compose

```yaml
version: '3.8'

services:
  mcp-opennutrition:
    build: .
    ports:
      - "8000:8000"
    environment:
      - PYTHONPATH=/app/src
    volumes:
      - ./data_local:/app/data_local
```

### Behind Nginx

```nginx
server {
    listen 80;
    server_name nutrition.example.com;

    location /mcp/ {
        proxy_pass http://127.0.0.1:8000/mcp/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Security Considerations

### For Production Use

1. **Authentication**: Add authentication middleware
2. **CORS**: Configure CORS headers appropriately
3. **Rate Limiting**: Implement rate limiting
4. **HTTPS**: Use HTTPS in production
5. **Firewall**: Restrict access to trusted IPs

### Example with Authentication

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials != "your-secret-token":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    return credentials.credentials

# Add to your route
@app.get("/search/{query}", dependencies=[Depends(verify_token)])
async def search_foods(query: str):
    # Your code here
    pass
```

## Monitoring

### Health Check Endpoint

```python
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "mcp-opennutrition"}
```

### Logging

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("mcp_opennutrition")
logger.info("Server started on http://127.0.0.1:8000")
```

## Troubleshooting

### Server won't start

**Error**: `Address already in use`

**Solution**: Port 8000 is already in use. Try a different port:
```bash
python3 -m mcp_opennutrition --port 8001
```

### Can't connect from client

**Error**: `Connection refused`

**Solution**: Make sure server is running and accessible:
```bash
# Check if server is running
curl http://127.0.0.1:8000/health

# Try binding to all interfaces
python3 -m mcp_opennutrition --host 0.0.0.0
```

### Import errors

**Error**: `No module named 'mcp_opennutrition'`

**Solution**: Set PYTHONPATH:
```bash
export PYTHONPATH="$(pwd)/src:$PYTHONPATH"
```

## Testing

### Quick Test with curl

```bash
# Note: MCP uses a custom protocol, so curl won't work directly
# Use the provided test client instead:
python3 tests/test_http_client.py
```

### Load Testing

```bash
# Install locust
pip install locust

# Create locustfile.py for load testing
# Then run:
locust -f locustfile.py --host http://127.0.0.1:8000
```

## Summary

The streamable-http transport makes MCP OpenNutrition easy to integrate with web applications, APIs, and distributed systems. Use it when you need:

- ✅ Web-based access
- ✅ Multiple concurrent clients
- ✅ Remote connections
- ✅ RESTful API integration

For command-line tools and IDE integrations, use the stdio transport instead.
