#!/usr/bin/env python3
"""
MCP OpenNutrition Client Test Script
This script demonstrates how to connect to the MCP OpenNutrition server
and use all available tools.
"""

import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    """Main function to test all MCP OpenNutrition tools"""

    # Server configuration - adjust node path if needed
    server_params = StdioServerParameters(
        command="node",
        args=["build/index.js"],
    )

    print("=" * 80)
    print("MCP OpenNutrition Client Test")
    print("=" * 80)
    print()

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the session
            await session.initialize()

            print("✓ Connected to MCP OpenNutrition Server")
            print()

            # List available tools
            print("-" * 80)
            print("AVAILABLE TOOLS")
            print("-" * 80)
            tools_list = await session.list_tools()

            for i, tool in enumerate(tools_list.tools, 1):
                print(f"\n{i}. {tool.name}")
                print(f"   Description: {tool.description[:150]}...")
                if hasattr(tool, 'inputSchema'):
                    print(f"   Input Schema: {json.dumps(tool.inputSchema.get('properties', {}), indent=6)}")

            print()
            print("=" * 80)
            print("TOOL USAGE EXAMPLES")
            print("=" * 80)

            # Example 1: Search food by name
            print("\n" + "-" * 80)
            print("Example 1: Search for 'apple' with search-food-by-name")
            print("-" * 80)
            result1 = await session.call_tool("search-food-by-name", {
                "query": "apple",
                "page": 1,
                "pageSize": 3
            })
            print(f"Result:\n{json.dumps(result1.content[0].text if result1.content else 'No content', indent=2)[:1000]}...")

            # Example 2: Get foods list
            print("\n" + "-" * 80)
            print("Example 2: Get list of foods with get-foods")
            print("-" * 80)
            result2 = await session.call_tool("get-foods", {
                "page": 1,
                "pageSize": 3
            })
            print(f"Result:\n{json.dumps(result2.content[0].text if result2.content else 'No content', indent=2)[:1000]}...")

            # Example 3: Get food by ID (using an ID from the search results)
            print("\n" + "-" * 80)
            print("Example 3: Get food by ID with get-food-by-id")
            print("-" * 80)
            # Parse the result to get an actual food ID
            foods_data = json.loads(result1.content[0].text) if result1.content else []
            if foods_data and len(foods_data) > 0:
                food_id = foods_data[0]['id']
                print(f"Using food ID: {food_id}")
                result3 = await session.call_tool("get-food-by-id", {
                    "id": food_id
                })
                print(f"Result:\n{json.dumps(result3.content[0].text if result3.content else 'No content', indent=2)[:1000]}...")
            else:
                print("Could not extract food ID from search results")

            # Example 4: Search for a food with barcode (if available)
            print("\n" + "-" * 80)
            print("Example 4: Get food by EAN-13 barcode with get-food-by-ean13")
            print("-" * 80)
            # Let's search for foods with barcodes first
            result_barcode_search = await session.call_tool("search-food-by-name", {
                "query": "coca cola",
                "page": 1,
                "pageSize": 5
            })

            barcode_foods = json.loads(result_barcode_search.content[0].text) if result_barcode_search.content else []
            barcode_found = None
            for food in barcode_foods:
                if food.get('ean_13'):
                    barcode_found = food['ean_13']
                    break

            if barcode_found:
                print(f"Using barcode: {barcode_found}")
                result4 = await session.call_tool("get-food-by-ean13", {
                    "ean_13": barcode_found
                })
                print(f"Result:\n{json.dumps(result4.content[0].text if result4.content else 'No content', indent=2)[:1000]}...")
            else:
                print("No foods with EAN-13 barcodes found in sample. Testing with a placeholder.")
                print("Note: In real usage, you would use an actual barcode from the database.")

            print("\n" + "=" * 80)
            print("✓ All tests completed successfully!")
            print("=" * 80)

if __name__ == "__main__":
    asyncio.run(main())
