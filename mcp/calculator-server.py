from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

load_dotenv()

transport = "stdio"
#transport = "sse"

# Create an MCP server
mcp = FastMCP(
    name="Calculator",
    #host="0.0.0.0",
    #port=8000, 
)


# Add a simple calculator tool
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b


# Run the server
if __name__ == "__main__":
    if transport == "stdio":
        print("Running server with stdio transport")
        mcp.run(transport="stdio")
    elif transport == "sse":
        print("Running server with SSE transport")
        mcp.run(transport="sse")
    else:
        raise ValueError(f"Unknown transport: {transport}")