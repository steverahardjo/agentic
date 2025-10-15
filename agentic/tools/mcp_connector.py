import asyncio
from typing import Optional
from fastmcp import Client


class MCPClient:
    """
    MCP Client adapter to convert MCP into a tool usable
    within an agentic agent instance.

    Inspired by Google ADK and DSPy MCP integrations.
    """

    def __init__(self, mcp_client_name: str, url: str, auth_token: Optional[str] = None):
        self.mcp_client_name = mcp_client_name
        self.url = url
        self.auth_token = auth_token
        self.client: Optional[Client] = None

    async def connect(self):
        """Initialize and connect the MCP client."""
        self.client = Client(url=self.url, auth_token=self.auth_token)
        await self.client.connect()
        print(f"[MCPClient] Connected to {self.url}")

    async def disconnect(self):
        """Gracefully disconnect the MCP client."""
        if self.client:
            await self.client.close()
            print(f"[MCPClient] Disconnected from {self.url}")

    async def ping(self) -> bool:
        """Ping the MCP server to verify connectivity."""
        if not self.client:
            raise RuntimeError("Client not connected. Call connect() first.")
        try:
            response = await self.client.ping()
            return response.get("status") == "ok"
        except Exception as e:
            print(f"[MCPClient] Ping failed: {e}")
            return False
        
    async def list_tools(self):
        return self.client.list_tools

    async def call_tool(self, tool_name: str, **kwargs):
        """
        Call a specific tool on the MCP server.
        """
        if not self.client:
            raise RuntimeError("Client not connected. Call connect() first.")
        try:
            result = await self.client.call(tool_name, **kwargs)
            return result
        except Exception as e:
            return None
        


async def main():
    # Replace these with real MCP endpoint & credentials
    client = MCPClient("demo-client", "https://mcp.pipedream.net/v2")

    await client.connect()

    alive = await client.ping()
    print(f"Server alive: {alive}")

    result = await client.call_tool("echo", message="Hello from FastMCP!")
    print(f"Tool call result: {result}")

    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())