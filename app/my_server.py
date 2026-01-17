from fastmcp import FastMCP

mcp = FastMCP("My MCP Server")


@mcp.tool
def greet(name: str) -> str:
    """シンプルな挨拶を返す"""
    return f"Hello, {name}!"


@mcp.tool
def add(a: int, b: int) -> int:
    """2つの数値を足し算する"""
    return a + b


if __name__ == "__main__":
    mcp.run(transport="http", port=8000)
