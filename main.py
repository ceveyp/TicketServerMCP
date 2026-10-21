from fastmcp import FastMCP

from app.tools import tools

instructions = """

This MCP is for access to an internal support ticket server. 
A user will ask questions about tickets, orders and users.
You will use the tools available to you to answer questions about tickets.
Use the list_tickets_tool with filters to fetch the list of tickets. 
Use the get_ticket_tool to fetch entire ticket, including body, metadata and assigned users.
The tickets are vectorized for semantic search.
Use the hybrid_search_tool to do semantic search and keyword_search_tool for keyword search.

"""

mcp = FastMCP("Ticket App MCP", tools=tools)

if __name__ == "__main__":
    mcp.run()
