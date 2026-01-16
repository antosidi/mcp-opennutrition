"""Tests for the MCP OpenNutrition server."""

import asyncio
import json

import pytest
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


@pytest.fixture
def server_params():
    """Create server parameters for testing."""
    return StdioServerParameters(
        command="python3",
        args=["-m", "mcp_opennutrition"],
    )


@pytest.mark.asyncio
async def test_server_connection(server_params):
    """Test that the server can be connected to."""
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            # If we get here without exception, connection succeeded
            assert True


@pytest.mark.asyncio
async def test_list_tools(server_params):
    """Test that all expected tools are listed."""
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools_list = await session.list_tools()

            tool_names = [tool.name for tool in tools_list.tools]
            assert "search-food-by-name" in tool_names
            assert "get-foods" in tool_names
            assert "get-food-by-id" in tool_names
            assert "get-food-by-ean13" in tool_names
            assert len(tools_list.tools) == 4


@pytest.mark.asyncio
async def test_search_food_by_name(server_params):
    """Test searching for foods by name."""
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            result = await session.call_tool("search-food-by-name", {
                "query": "banana",
                "page": 1,
                "pageSize": 3
            })

            assert result.content
            foods = json.loads(result.content[0].text)
            assert isinstance(foods, list)
            assert len(foods) > 0
            assert all('id' in food for food in foods)
            assert all('name' in food for food in foods)


@pytest.mark.asyncio
async def test_get_foods(server_params):
    """Test getting paginated list of foods."""
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            result = await session.call_tool("get-foods", {
                "page": 1,
                "pageSize": 3
            })

            assert result.content
            foods = json.loads(result.content[0].text)
            assert isinstance(foods, list)
            assert len(foods) == 3


@pytest.mark.asyncio
async def test_get_food_by_id(server_params):
    """Test getting a food by ID."""
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # First search for a food to get an ID
            search_result = await session.call_tool("search-food-by-name", {
                "query": "apple",
                "page": 1,
                "pageSize": 1
            })

            foods = json.loads(search_result.content[0].text)
            assert len(foods) > 0

            food_id = foods[0]['id']

            # Now get by ID
            result = await session.call_tool("get-food-by-id", {
                "id": food_id
            })

            assert result.content
            food = json.loads(result.content[0].text)
            assert food is not None
            assert food['id'] == food_id


@pytest.mark.asyncio
async def test_get_food_by_ean13(server_params):
    """Test getting a food by EAN-13 barcode."""
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # Search for foods with barcodes
            search_result = await session.call_tool("search-food-by-name", {
                "query": "coca cola",
                "page": 1,
                "pageSize": 10
            })

            foods = json.loads(search_result.content[0].text)

            # Find a food with a barcode
            barcode_food = None
            for food in foods:
                if food.get('ean_13') and len(food['ean_13']) == 13:
                    barcode_food = food
                    break

            if barcode_food:
                # Test barcode lookup
                result = await session.call_tool("get-food-by-ean13", {
                    "ean_13": barcode_food['ean_13']
                })

                assert result.content
                food = json.loads(result.content[0].text)
                assert food is not None
                assert food['ean_13'] == barcode_food['ean_13']


@pytest.mark.asyncio
async def test_pagination(server_params):
    """Test that pagination works correctly."""
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # Get page 1
            page1 = await session.call_tool("search-food-by-name", {
                "query": "apple",
                "page": 1,
                "pageSize": 2
            })

            # Get page 2
            page2 = await session.call_tool("search-food-by-name", {
                "query": "apple",
                "page": 2,
                "pageSize": 2
            })

            foods_page1 = json.loads(page1.content[0].text)
            foods_page2 = json.loads(page2.content[0].text)

            # Pages should have different foods
            page1_ids = {food['id'] for food in foods_page1}
            page2_ids = {food['id'] for food in foods_page2}

            assert page1_ids.isdisjoint(page2_ids)


@pytest.mark.asyncio
async def test_invalid_food_id(server_params):
    """Test that invalid food ID raises appropriate error."""
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            with pytest.raises(Exception):
                await session.call_tool("get-food-by-id", {
                    "id": "invalid_id"  # Doesn't start with fd_
                })


@pytest.mark.asyncio
async def test_invalid_ean13(server_params):
    """Test that invalid EAN-13 raises appropriate error."""
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            with pytest.raises(Exception):
                await session.call_tool("get-food-by-ean13", {
                    "ean_13": "123"  # Too short
                })
