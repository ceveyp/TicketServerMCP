from fastmcp import FastMCP

from app.tools import tools

instructions = """

This MCP is for access to an internal ticket server. 
A user will ask questions about tickets, 

"""

mcp = FastMCP("Ticket App MCP", tools=tools)

if __name__ == "__main__":
    mcp.run()
