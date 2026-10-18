from app.crud.users import search_users
from app.db.db import TicketAppSession
from app.logger import get_logger

logger = get_logger(__name__)


def search_users_tool(name: str) -> str:
    try:
        logger.debug(f"Searching for users by name: {name}")
        if not isinstance(name, str) or not name.strip():
            logger.debug(f"No users found: {name}")
            return "No users found by this name"
        with TicketAppSession() as db:
            users = search_users(db, name)
            if not users:
                logger.debug(f"No users found: {name}")
                return "No users found by this name"
            users = [{
                "id": user.id,
                "name": user.name,
                "title": user.title,
                "email": user.email
            } for user in users]
            logger.debug(f"{len(users)} user(s) found: {name}")
            if len(users) > 1:
                return f"Multiple users found by this name: \n\n{users}"
            return f"User: \n\n{users}"
    except Exception as e:
        logger.exception(e)
        return f"Error searching users: {e}"
