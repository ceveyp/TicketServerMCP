from app.tools.rag import hybrid_search_tool, keyword_search_tool
from app.tools.tickets import list_tickets_tool, get_ticket_tool, get_ticket_ids_tool
from app.tools.users import list_users_tool, search_users_tool, get_user_ids_tool, get_users_tool

tools = [
    list_users_tool,
    search_users_tool,
    get_ticket_tool,
    list_tickets_tool,
    get_users_tool,
    get_user_ids_tool,
    get_ticket_ids_tool,
    hybrid_search_tool,
    keyword_search_tool
]
