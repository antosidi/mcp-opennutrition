#!/usr/bin/env python3
"""
Test client for MCP OpenNutrition Server using streamable-http transport.
Demonstrates connecting to the server, listing tools, and calling functions.
"""

import asyncio
from contextlib import AsyncExitStack
import json
import sys
from pathlib import Path
from typing import Optional, Any

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


class TestClient:
    """MCP OpenNutrition Test Client."""
    
    def __init__(self) -> None:
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.read_stream: Optional[Any] = None
        self.write_stream: Optional[Any] = None
        
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
        
    async def test_search_food_by_name(self) -> None:
        """Test search_food_by_name tool."""
        
        if not self.session:
            raise RuntimeError("Client is not connected to a session.")
        
        print_section("Test: Search for 'banana'")
        print_info("Calling search-food-by-name...")

        result: CallToolResult = await self.session.call_tool(
            "search-food-by-name", 
            {"query": "banana", "page": 1, "pageSize": 2}
        )
        validate_toolcall_result(result, "search-food-by-name")

        foods = result.structuredContent["result"]
        
        print_success(f"Found {len(foods)} foods")

        for food in foods:
            print(f"\n  • \033[1m{food['name']}\033[0m")
            print(f"    ID: {food['id']}")
            print(f"    Type: {food.get('type', 'N/A')}")
            if food.get('nutrition_100g'):
                calories = food['nutrition_100g'].get('calories', 'N/A')
                protein = food['nutrition_100g'].get('protein', 'N/A')
                print(f"    Calories: {calories} kcal/100g")
                print(f"    Protein: {protein} g/100g")
                
    async def test_get_foods(self) -> None:
        """Test get_foods tool."""
        
        if not self.session:
            raise RuntimeError("Client is not connected to a session.")
        
        print_section("Test: Browse foods (get-foods)")
        print_info("Calling get-foods...")

        result = await self.session.call_tool(
            "get-foods", {"page": 1, "pageSize": 3}
        )
        
        validate_toolcall_result(result, "get-foods")

        all_foods = result.structuredContent["result"]
        
        print_success(f"Retrieved {len(all_foods)} foods")

        for i, food in enumerate(all_foods, 1):
            print(f"\n  {i}. \033[1m{food['name']}\033[0m (ID: {food['id']})")

    async def test_get_food_by_id(self) -> None:
        """Test get_food_by_id tool."""
        
        if not self.session:
            raise RuntimeError("Client is not connected to a session.")
        
        print_section("Test: Get food by ID (get-food-by-id)")

        food_id = "fd_AjQa9nlOUTns" # banana
        print_info(f"Calling get-food-by-id with ID: {food_id}...")

        result = await self.session.call_tool(
            "get-food-by-id", {"id": food_id}
        )
        validate_toolcall_result(result, "get-food-by-id")
        
        food_detail = result.structuredContent["result"]
        
        print_success("Retrieved detailed food information")

        print(f"\n  \033[1m{food_detail['name']}\033[0m")
        print(f"  ID: {food_detail['id']}")
        print(f"  Type: {food_detail.get('type', 'N/A')}")

        if food_detail.get('nutrition_100g'):
            print("\n  Nutritional Information (per 100g):")
            nutrition = food_detail['nutrition_100g']
            key_nutrients = ['calories', 'protein', 'carbohydrates', 'fat', 'fiber']

            for nutrient in key_nutrients:
                if nutrient in nutrition:
                    value = nutrition[nutrient]
                    print(f"    - {nutrient.capitalize()}: {value}")

        if food_detail.get('labels'):
            print(f"\n  Labels: {', '.join(food_detail['labels'])}")
        
    async def test_get_food_by_ean13(self) -> None:
        """Test get_food_by_ean13 tool."""
        
        if not self.session:
            raise RuntimeError("Client is not connected to a session.")

        barcode = "0049000042566" # coca cola

        print_info("Calling get-food-by-ean13...")

        result = await self.session.call_tool("get-food-by-ean13", {
            "ean_13": barcode
        })
        validate_toolcall_result(result, "get-food-by-ean13")
        food = result.structuredContent["result"]
        if food:
            print_success("Retrieved food by barcode")
            print(f"\n  \033[1m{food['name']}\033[0m")
            print(f"  Barcode: {food['ean_13']}")
            print(f"  Type: {food.get('type', 'N/A')}")

    async def test_pagination(self) -> None:
        """Test pagination of search results."""
        
        if not self.session:
            raise RuntimeError("Client is not connected to a session.")
        
        # Pagination test
        print_section("Test: Pagination Test")
        print_info("Testing pagination with multiple pages...")

        page1 = await self.session.call_tool("search-food-by-name", {
            "query": "apple",
            "page": 1,
            "pageSize": 2
        })
        validate_toolcall_result(page1, "search-food-by-name (page 1)")

        page2 = await self.session.call_tool("search-food-by-name", {
            "query": "apple",
            "page": 2,
            "pageSize": 2
        })
        validate_toolcall_result(page2, "search-food-by-name (page 2)")

        page1_foods = page1.structuredContent["result"]
        page2_foods = page2.structuredContent["result"]

        print_success(f"Page 1: {len(page1_foods)} results")
        for food in page1_foods:
            print(f"  - {food['name']} ({food['id']})")

        print_success(f"Page 2: {len(page2_foods)} results")
        for food in page2_foods:
            print(f"  - {food['name']} ({food['id']})")


async def main():
    
    server_url = "http://127.0.0.1:8000/mcp"

    print_header("MCP OpenNutrition HTTP Client Test")
    print_info(f"Connecting to server at {server_url}...")
    print_info("Make sure the server is running with:")
    print_info("  python3 -m mcp_opennutrition --transport streamable-http")
    print()
    
    client = TestClient()
    
    try:
        await client.connect(server_url)

        await client.print_tools()
        await client.test_search_food_by_name()
        await client.test_get_foods()
        await client.test_get_food_by_id()
        await client.test_get_food_by_ean13()
        await client.test_pagination()

        # Summary
        print_header("Test Summary", "=")
        print_success("All HTTP transport tests completed successfully!")
        print()
        print("Tests executed:")
        print("  ✓ Connected to server via streamable-http")
        print("  ✓ Listed all available tools (4 tools)")
        print("  ✓ search-food-by-name: Found foods matching query")
        print("  ✓ get-foods: Retrieved paginated food list")
        print("  ✓ get-food-by-id: Retrieved detailed food information")
        print("  ✓ get-food-by-ean13: Looked up food by barcode")
        print("  ✓ Pagination: Tested multiple pages of results")
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
