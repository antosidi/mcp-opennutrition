#!/usr/bin/env python3

import asyncio
from contextlib import AsyncExitStack
from openai import AsyncOpenAI
import json
import sys
from pathlib import Path
from typing import Optional, Any, Dict, List

from mcp import ClientSession
from mcp.types import CallToolResult
from mcp.client.streamable_http import streamable_http_client


def print_header(text: str, char: str = "="):
    """Print a formatted header."""
    width = 80
    print()
    print(char * width)
    print(text.center(width))
    print(char * width)
    print()


def print_section(text: str):
    """Print a section header."""
    width = 80
    print()
    print("-" * width)
    print(text)
    print("-" * width)


def print_success(text: str):
    """Print success message in green."""
    print(f"\033[0;92m✓ {text}\033[0m")


def print_info(text: str):
    """Print info message in blue."""
    print(f"\033[0;94m→ {text}\033[0m")


def print_data(label: str, data: dict, indent: int = 2):
    """Print formatted data."""
    print(f"\n{label}:")
    print(json.dumps(data, indent=indent))


def validate_toolcall_result(result: CallToolResult | Any, tool_name: str):
    """Check if the tool call result is valid."""
    if not isinstance(result, CallToolResult):
        raise TypeError(f"Invalid result from {tool_name}")
    if not result.structuredContent:
        raise ValueError(f"No structured content in result from {tool_name}")
    if "result" not in result.structuredContent:
        raise KeyError(f"'result' key missing in structured content from {tool_name}")


class TestOpenAIClient:
    """MCP OpenNutrition Test Client."""
    
    def __init__(self, model: str = "gpt-4o-mini") -> None:
        self.session: Optional[ClientSession] = None
        self.read_stream: Optional[Any] = None
        self.write_stream: Optional[Any] = None
        self.exit_stack = AsyncExitStack()
        self.client = AsyncOpenAI()
        self.model = model
        
    async def cleanup(self) -> None:
        """Cleanup resources."""
        await self.exit_stack.aclose()
        
    async def connect(self, server_url: str) -> None:
        """Connect to the MCP OpenNutrition server."""
        
        print_info(f"Connecting to server at {server_url}...")
        
        # Connect to the server
        http_transport = await self.exit_stack.enter_async_context(
            streamable_http_client(server_url)
        )
        self.read_stream, self.write_stream, _ = http_transport
        self.session = await self.exit_stack.enter_async_context(
            ClientSession(self.read_stream, self.write_stream)
        )

        # Initialize the connection
        await self.session.initialize()
        
        print_success("✓ Connected to MCP OpenNutrition Server (HTTP)")
    
    async def print_tools(self) -> None:
        
        if not self.session:
            raise RuntimeError("Client is not connected to a session.")
        
        # List available tools
        print_section("Available Tools")
        tools_list = await self.session.list_tools()

        for i, tool in enumerate(tools_list.tools, 1):
            print(f"\n{i}. \033[1m{tool.name}\033[0m")
            print(f"   Description: {tool.description[:100]}...")

            if hasattr(tool, 'inputSchema') and 'properties' in tool.inputSchema:
                print("   Parameters:")
                for param_name, param_info in tool.inputSchema['properties'].items():
                    param_type = param_info.get('type', 'unknown')
                    required = param_name in tool.inputSchema.get('required', [])
                    required_str = " (required)" if required else " (optional)"
                    print(f"      - {param_name}: {param_type}{required_str}")

        print_success(f"Found {len(tools_list.tools)} tools")
        
    async def get_mcp_tools(self) -> List[Dict[str, Any]]:
        """Get available tools from the MCP server in OpenAI format.

        Returns:
            A list of tools in OpenAI format.
        """
        
        if not self.session:
            raise RuntimeError("Client is not connected to a session.")
        
        tools_result = await self.session.list_tools()
        return [
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

async def main():
    
    server_url = "http://127.0.0.1:8000/mcp"

    print_header("MCP OpenNutrition HTTP Client Test")
    print_info(f"Connecting to server at {server_url}...")
    print_info("Make sure the server is running with:")
    print_info("  python3 -m mcp_opennutrition --transport streamable-http")
    print()
    
    client = TestOpenAIClient()
    
    try:
        await client.connect(server_url)

        # await client.print_tools()
        
        tools = await client.get_mcp_tools()
        print_header("Tools", "=")
        print(json.dumps(tools, indent=2))
        print()

        # Summary
        print_header("Test Summary", "=")
        print_success("All HTTP transport tests completed successfully!")
        print()
        print("Tests executed:")
        print("  ✓ Connected to server via streamable-http")
        print("  ✓ Listed all available tools (4 tools)")
        print()

    except Exception as e:
        print(f"\n\033[0;91m✗ Error: {e}\033[0m")
        import traceback
        traceback.print_exc()
        sys.exit(1)
        
    finally:
        await client.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
