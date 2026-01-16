#!/usr/bin/env python3
"""
Simple test client for MCP OpenNutrition Server using streamable-http transport.
Demonstrates connecting to the server, listing tools, and calling functions.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from mcp import ClientSession
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


async def main():
    """Main test function."""
    server_url = "http://127.0.0.1:8000/mcp/v1"

    print_header("MCP OpenNutrition HTTP Client Test")
    print_info(f"Connecting to server at {server_url}...")
    print_info("Make sure the server is running with:")
    print_info("  export PYTHONPATH=\"$(pwd)/src:$PYTHONPATH\"")
    print_info("  python3 -m mcp_opennutrition --transport streamable-http")
    print()

    try:
        async with streamable_http_client(server_url) as client:
            async with ClientSession(*client) as session:
                # Initialize session
                await session.initialize()
                print_success("Connected to MCP OpenNutrition Server (HTTP)")

                # List available tools
                print_section("Available Tools")
                tools_list = await session.list_tools()

                for i, tool in enumerate(tools_list.tools, 1):
                    print(f"\n{i}. \033[1m{tool.name}\033[0m")
                    print(f"   {tool.description[:80]}...")

                print_success(f"Found {len(tools_list.tools)} tools")

                # Test 1: Search for foods by name
                print_section("Test 1: Search for 'banana'")
                print_info("Calling search-food-by-name...")

                result1 = await session.call_tool("search-food-by-name", {
                    "query": "banana",
                    "page": 1,
                    "pageSize": 2
                })

                foods = json.loads(result1.content[0].text)
                print_success(f"Found {len(foods)} foods")

                for food in foods:
                    print(f"\n  • \033[1m{food['name']}\033[0m")
                    print(f"    ID: {food['id']}")
                    if food.get('nutrition_100g'):
                        calories = food['nutrition_100g'].get('calories', 'N/A')
                        protein = food['nutrition_100g'].get('protein', 'N/A')
                        print(f"    Nutrition: {calories} kcal, {protein}g protein (per 100g)")

                # Test 2: Get foods list
                print_section("Test 2: Browse foods (get-foods)")
                print_info("Calling get-foods...")

                result2 = await session.call_tool("get-foods", {
                    "page": 1,
                    "pageSize": 3
                })

                all_foods = json.loads(result2.content[0].text)
                print_success(f"Retrieved {len(all_foods)} foods")

                for i, food in enumerate(all_foods, 1):
                    print(f"  {i}. {food['name']} (ID: {food['id']})")

                # Test 3: Get food by ID
                print_section("Test 3: Get food by ID")

                food_id = foods[0]['id'] if foods else None
                if food_id:
                    print_info(f"Retrieving food with ID: {food_id}...")

                    result3 = await session.call_tool("get-food-by-id", {
                        "id": food_id
                    })

                    food_detail = json.loads(result3.content[0].text)
                    print_success("Retrieved detailed food information")

                    print(f"\n  \033[1m{food_detail['name']}\033[0m")
                    print(f"  ID: {food_detail['id']}")
                    print(f"  Type: {food_detail.get('type', 'N/A')}")

                    if food_detail.get('nutrition_100g'):
                        print("\n  Key Nutrients (per 100g):")
                        nutrition = food_detail['nutrition_100g']
                        for nutrient in ['calories', 'protein', 'carbohydrates', 'fat']:
                            if nutrient in nutrition:
                                print(f"    - {nutrient.capitalize()}: {nutrition[nutrient]}")

                # Summary
                print_header("Test Summary", "=")
                print_success("All HTTP transport tests completed successfully!")
                print()
                print("Tests executed:")
                print("  ✓ Connected to server via streamable-http")
                print("  ✓ Listed all available tools")
                print("  ✓ search-food-by-name: Found foods matching query")
                print("  ✓ get-foods: Retrieved paginated food list")
                print("  ✓ get-food-by-id: Retrieved detailed food information")
                print()

    except Exception as e:
        print(f"\n\033[0;91m✗ Error: {e}\033[0m")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
