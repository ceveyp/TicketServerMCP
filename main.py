from fastmcp import FastMCP

instructions = """

This MCP is for access to an internal ticket server. 
A user will ask questions about tickets, 

"""

mcp = FastMCP(
    name="Ticket App MCP"
)


if __name__ == "__main__":
    mcp.run()
