import asyncio
from typing import Optional, Union, List
from fastmcp import Client, Tool, Types
from mcp.types import Tool, Prompt, Resource

class MCPClient:
    """
    MCP Client adapter to convert MCP into a tool usable
    within an agentic agent instance.

    Inspired by Google ADK and DSPy MCP integrations.
    """

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
        
    async def lists(self) -> List[Union[Tool, Resource, Prompt]]:
        """
        Fetch all Tools, Resources, and Prompts from FastMCP.
        Skips any items that are malformed.
        """
        async with self.client:
            all_items: List[Union[Tool, Resource, Prompt]] = []
            try:
                tools = await self.client.list_tools()
                all_items.extend([t for t in tools if isinstance(t, Tool)])
            except Exception:
                pass
            try:
                resources = await self.client.list_resources()
                all_items.extend([r for r in resources if isinstance(r, Resource)])
            except Exception:
                pass
            try:
                prompts = await self.client.list_prompts()
                all_items.extend([p for p in prompts if isinstance(p, Prompt)])
            except Exception:
                pass

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
        except Exception as e:
            return None
        
async def main():
    # Create client against the remote MCP server
    client = Client("https://mcp.exa.ai/mcp")

    async with client:
        # you can inspect available tools
        tools = await client.list_tools()

        # Call a tool (depending on what Exa offers, e.g. "web_search_exa")
        print(tools)