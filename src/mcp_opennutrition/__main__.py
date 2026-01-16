"""Command-line interface for MCP OpenNutrition server."""

import asyncio
import sys

# Ensure server module can parse arguments when called as module
if __name__ == "__main__":
    from .server import main
    asyncio.run(main())
