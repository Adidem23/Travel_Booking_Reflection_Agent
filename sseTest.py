import asyncio
from mcp.client.sse import sse_client
from mcp.client.session import ClientSession

async def main():
    async with sse_client("http://localhost:1820/sse") as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            print("✅ Session initialized")

            tools = await session.list_tools()
            print("Connected to server with tools:", [t.name for t in tools.tools])

            result = await session.call_tool(
                name="get_weather",
                arguments={"destination": "Pune"}
            )
            print("🌦 Tool result:", result)

asyncio.run(main())