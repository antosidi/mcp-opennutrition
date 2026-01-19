#!/usr/bin/env python3

import asyncio
from contextlib import AsyncExitStack
import json
import sys
from typing import Optional, Any, Dict, List

from mcp import ClientSession
from mcp.types import CallToolResult
from mcp.client.streamable_http import streamable_http_client


async def main():
    
    server_url = "http://127.0.0.1:8000/mcp"
    exit_stack = AsyncExitStack()
    
    try:
        http_transport = await exit_stack.enter_async_context(
            streamable_http_client(server_url)
        )
        read_stream, write_stream, _ = http_transport
        session = await exit_stack.enter_async_context(
            ClientSession(read_stream, write_stream)
        )
        await session.initialize()

        tools_result = await session.list_tools()
        tools = [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema,
                },
            }
            for tool in tools_result.tools
        ]

        print('----------------- Tools ----------------')
        print(json.dumps(tools, indent=2))
        print()

    except Exception as e:
        print(f"\n\033[0;91m✗ Error: {e}\033[0m")
        import traceback
        traceback.print_exc()
        sys.exit(1)
        
    finally:
        await exit_stack.aclose()


if __name__ == "__main__":
    asyncio.run(main())
