from typing import Union
from fastmcp import Client

class MCPConnector:
    def __init__(self, mcp_client_name: str, url_or_config: Union[str, dict]):        
        self.mcp_client_name = mcp_client_name
        self.url = url_or_config

    async def connect(self):
        """Initialize and connect the MCP client."""
        self.client = Client(url=self.url)
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
    
    def lists(self):
        """
        Fetch all Tools, Resources, and Prompts from FastMCP.
        Skips any items that are malformed.
        """
        all_items= []
        try:
            tools = self.client.list_tools()
            all_items.extend([t for t in tools])
        except Exception:
            pass
        try:
            resources =self.client.list_resources()
            all_items.extend([r for r in resources])
        except Exception:
            pass
        try:
            prompts = self.client.list_prompts()
            all_items.extend([p for p in prompts])
        except:
            return all_items


    async def call(self, tool_name: str, **kwargs):
        """
        Call a specific tool on the MCP server.
        """
        if not self.client:
            raise RuntimeError("Client not connected. Call connect() first.")
        try:
            result = await self.client.call(tool_name, **kwargs)
            return result
        except Exception:
            return None
        