"""MCP OpenNutrition Server - Model Context Protocol server for food data."""

import asyncio
import json
import sys
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from .db_adapter import SQLiteDBAdapter


class OpenNutritionServer:
    """MCP Server for OpenNutrition database."""

    def __init__(self):
        """Initialize the MCP OpenNutrition server."""
        self.server = Server("mcp-opennutrition")
        self.db = SQLiteDBAdapter()
        self._register_handlers()

    def _register_handlers(self):
        """Register all tool handlers."""

        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List all available tools.

            Returns:
                List of available MCP tools
            """
            return [
                Tool(
                    name="search-food-by-name",
                    description=(
                        "Search for foods by name, synonym, or partial name. "
                        "Supports fuzzy matching and pagination. "
                        "Use this tool when searching for foods by common, brand, or alternate names."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query for food name",
                                "minLength": 1
                            },
                            "page": {
                                "type": "number",
                                "description": "Page number (1-indexed)",
                                "minimum": 1,
                                "default": 1
                            },
                            "pageSize": {
                                "type": "number",
                                "description": "Number of results per page",
                                "default": 5
                            }
                        },
                        "required": ["query"]
                    }
                ),
                Tool(
                    name="get-foods",
                    description=(
                        "Get a paginated list of all available foods. "
                        "Use this tool when browsing foods or requesting an overview."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "page": {
                                "type": "number",
                                "description": "Page number (1-indexed)",
                                "minimum": 1,
                                "default": 1
                            },
                            "pageSize": {
                                "type": "number",
                                "description": "Number of results per page",
                                "default": 5
                            }
                        }
                    }
                ),
                Tool(
                    name="get-food-by-id",
                    description=(
                        "Get detailed information for a specific food by its ID. "
                        "Use this tool when you have a food ID and need complete nutritional data."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "id": {
                                "type": "string",
                                "description": "Food ID (must start with 'fd_')",
                                "pattern": "^fd_"
                            }
                        },
                        "required": ["id"]
                    }
                ),
                Tool(
                    name="get-food-by-ean13",
                    description=(
                        "Look up food by EAN-13 barcode. "
                        "Use this tool when identifying foods from barcodes."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "ean_13": {
                                "type": "string",
                                "description": "EAN-13 barcode (exactly 13 characters)",
                                "minLength": 13,
                                "maxLength": 13
                            }
                        },
                        "required": ["ean_13"]
                    }
                )
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Any) -> list[TextContent]:
            """Handle tool calls.

            Args:
                name: Tool name
                arguments: Tool arguments

            Returns:
                List of text content responses

            Raises:
                ValueError: If tool parameters are invalid
            """
            if name == "search-food-by-name":
                query = arguments.get("query")
                page = arguments.get("page", 1)
                page_size = arguments.get("pageSize", 5)

                if not query:
                    raise ValueError("query parameter is required")

                foods = self.db.search_by_name(query, page, page_size)

                return [
                    TextContent(
                        type="text",
                        text=json.dumps(foods, indent=2)
                    )
                ]

            elif name == "get-foods":
                page = arguments.get("page", 1)
                page_size = arguments.get("pageSize", 5)

                foods = self.db.get_all(page, page_size)

                return [
                    TextContent(
                        type="text",
                        text=json.dumps(foods, indent=2)
                    )
                ]

            elif name == "get-food-by-id":
                food_id = arguments.get("id")

                if not food_id:
                    raise ValueError("id parameter is required")

                if not food_id.startswith("fd_"):
                    raise ValueError("Food ID must start with 'fd_'")

                food = self.db.get_by_id(food_id)

                return [
                    TextContent(
                        type="text",
                        text=json.dumps(food, indent=2)
                    )
                ]

            elif name == "get-food-by-ean13":
                ean_13 = arguments.get("ean_13")

                if not ean_13:
                    raise ValueError("ean_13 parameter is required")

                if len(ean_13) != 13:
                    raise ValueError("EAN-13 must be exactly 13 characters long")

                food = self.db.get_by_ean13(ean_13)

                return [
                    TextContent(
                        type="text",
                        text=json.dumps(food, indent=2)
                    )
                ]

            else:
                raise ValueError(f"Unknown tool: {name}")

    async def run(self):
        """Run the MCP server."""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


async def main():
    """Main entry point for the server."""
    server = OpenNutritionServer()

    # Log to stderr so it doesn't interfere with stdio communication
    print("MCP OpenNutrition Server running on stdio", file=sys.stderr)

    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
