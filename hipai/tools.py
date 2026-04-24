from fastmcp import FastMCP
from datetime import datetime


mcp = FastMCP("HiPAI MCP Server")

@mcp.tool()
def get_current_date_and_time() -> str:
    """
    Get the current time and date.

    Returns:
        The current time and date as a string.
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


if __name__ == "__main__":
    mcp.run()
