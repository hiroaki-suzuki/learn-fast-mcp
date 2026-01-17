import asyncio

from fastmcp import Client

client = Client("http://localhost:8000/mcp")


async def main():
    async with client:
        # Call the "greet" tool
        greet_result = await client.call_tool("greet", {"name": "Gemini"})
        print(f"Result from greet: {greet_result}")

        # Call the "add" tool
        add_result = await client.call_tool("add", {"a": 5, "b": 7})
        print(f"Result from add: {add_result}")


if __name__ == "__main__":
    asyncio.run(main())
