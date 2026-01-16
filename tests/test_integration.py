"""Integration tests for the full MCP OpenNutrition system."""

import asyncio
import json
import sys
from pathlib import Path

import pytest

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


@pytest.fixture
def server_params():
    """Create server parameters for testing."""
    project_root = Path(__file__).parent.parent
    return StdioServerParameters(
        command="python3",
        args=["-m", "mcp_opennutrition"],
        env={"PYTHONPATH": str(project_root / "src")}
    )


@pytest.mark.asyncio
async def test_full_workflow(server_params):
    """Test a complete workflow using all tools."""
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # Step 1: Search for a food
            search_result = await session.call_tool("search-food-by-name", {
                "query": "banana",
                "page": 1,
                "pageSize": 1
            })

            foods = json.loads(search_result.content[0].text)
            assert len(foods) > 0

            food_id = foods[0]['id']
            food_name = foods[0]['name']

            # Step 2: Get detailed info by ID
            detail_result = await session.call_tool("get-food-by-id", {
                "id": food_id
            })

            food_detail = json.loads(detail_result.content[0].text)
            assert food_detail['id'] == food_id
            assert food_detail['name'] == food_name
            assert 'nutrition_100g' in food_detail

            # Step 3: Browse foods
            browse_result = await session.call_tool("get-foods", {
                "page": 1,
                "pageSize": 5
            })

            all_foods = json.loads(browse_result.content[0].text)
            assert len(all_foods) == 5
            assert all(isinstance(f, dict) for f in all_foods)


@pytest.mark.asyncio
async def test_nutritional_data_completeness(server_params):
    """Test that nutritional data is comprehensive."""
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            result = await session.call_tool("search-food-by-name", {
                "query": "apple",
                "page": 1,
                "pageSize": 1
            })

            foods = json.loads(result.content[0].text)
            food = foods[0]

            # Check for key nutritional fields
            nutrition = food.get('nutrition_100g', {})
            expected_fields = ['calories', 'protein', 'carbohydrates', 'fat']

            for field in expected_fields:
                assert field in nutrition, f"Missing nutritional field: {field}"


@pytest.mark.asyncio
async def test_search_relevance(server_params):
    """Test that search returns relevant results."""
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            result = await session.call_tool("search-food-by-name", {
                "query": "organic apple",
                "page": 1,
                "pageSize": 5
            })

            foods = json.loads(result.content[0].text)

            # All results should contain "apple" in name or alternate names
            for food in foods:
                name_lower = food['name'].lower()
                alt_names = food.get('alternate_names', []) or []
                alt_names_lower = [n.lower() for n in alt_names]

                assert 'apple' in name_lower or any('apple' in n for n in alt_names_lower)
