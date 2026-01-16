"""MCP OpenNutrition Server - Model Context Protocol server for food data."""

import argparse
import asyncio
import json
import sys
from typing import Any, Literal

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from .db_adapter import SQLiteDBAdapter

TransportType = Literal["stdio", "streamable-http"]


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

    async def run_stdio(self):
        """Run the MCP server with stdio transport."""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )

    async def run_http(self, host: str = "127.0.0.1", port: int = 8000):
        """Run the MCP server with streamable HTTP transport.

        Args:
            host: Host address to bind to
            port: Port to listen on
        """
        from mcp.server.streamable_http import StreamableHTTPServerTransport
        from starlette.applications import Starlette
        from starlette.routing import Route
        from starlette.responses import Response

        # Create HTTP transport
        transport = StreamableHTTPServerTransport("/mcp/v1")

        # Create Starlette routes
        async def handle_sse(request):
            async with transport.connect_sse(
                request.scope, request.receive, request._send
            ) as streams:
                await self.server.run(
                    streams[0], streams[1], self.server.create_initialization_options()
                )
            return Response()

        async def handle_messages(request):
            async with transport.connect_messages(
                request.scope, request.receive, request._send
            ) as streams:
                await self.server.run(
                    streams[0], streams[1], self.server.create_initialization_options()
                )
            return Response()

        app = Starlette(
            routes=[
                Route("/mcp/v1/sse", endpoint=handle_sse),
                Route("/mcp/v1/messages", endpoint=handle_messages, methods=["POST"]),
            ]
        )

        import uvicorn
        config = uvicorn.Config(app, host=host, port=port, log_level="info")
        server = uvicorn.Server(config)
        await server.serve()

    async def run(self, transport: TransportType = "streamable-http", host: str = "127.0.0.1", port: int = 8000):
        """Run the MCP server with specified transport.

        Args:
            transport: Transport type ("stdio" or "streamable-http")
            host: Host address for HTTP transport
            port: Port for HTTP transport
        """
        if transport == "stdio":
            await self.run_stdio()
        elif transport == "streamable-http":
            await self.run_http(host, port)
        else:
            raise ValueError(f"Unknown transport: {transport}")


async def main():
    """Main entry point for the server."""
    parser = argparse.ArgumentParser(
        description="MCP OpenNutrition Server - Food database via Model Context Protocol"
    )
    parser.add_argument(
        "--transport",
        type=str,
        choices=["stdio", "streamable-http"],
        default="streamable-http",
        help="Transport protocol to use (default: streamable-http)"
    )
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Host address for HTTP transport (default: 127.0.0.1)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port for HTTP transport (default: 8000)"
    )

    args = parser.parse_args()

    server = OpenNutritionServer()

    if args.transport == "stdio":
        print("MCP OpenNutrition Server running on stdio", file=sys.stderr)
    else:
        print(f"MCP OpenNutrition Server running on http://{args.host}:{args.port}", file=sys.stderr)

    await server.run(transport=args.transport, host=args.host, port=args.port)


if __name__ == "__main__":
    asyncio.run(main())
