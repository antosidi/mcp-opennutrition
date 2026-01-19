"""
MCP OpenNutrition - Model Context Protocol server for OpenNutrition database.

Provides access to comprehensive food and nutrition data through MCP tools.
"""

from .server import mcp
from .db_adapter import SQLiteDBAdapter, FoodItem

__version__ = "1.0.0"
__all__ = ["mcp", "SQLiteDBAdapter", "FoodItem"]
