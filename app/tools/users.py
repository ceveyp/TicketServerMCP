from pprint import pformat
from typing import List

from app.crud.users import search_users, list_users, get_user, get_user_ids
from app.db.db import TicketAppSession
from app.logger import get_logger

logger = get_logger(__name__)


def list_users_tool() -> str:
    """
    List all user IDs and names.
    :return: list of all users
    """
    try:
        with TicketAppSession() as db:
            users = list_users(db)
            return f"All users: \n\n{pformat(users)}"
    except Exception as e:
        logger.exception(e)
        return f"Error fetching users list: {e}"


def get_users_tool(user_id: int) -> str:
    """
    Get a user by ID.
    :param user_id: user ID
    :return: user data
    """
    try:
        with TicketAppSession() as db:
            logger.debug(f"Fetching user by ID: {user_id}")
            user = get_user(db, user_id)
            return f"User: \n\n{pformat(user)}"
    except Exception as e:
        logger.exception(e)
        return f"Error fetching user: {e}"


def get_user_ids_tool(user_ids: List[int]) -> str:
    """
    Get a user by ID.
    :param user_ids: list of user IDS
    :return: user data
    """
    try:
        with TicketAppSession() as db:
            logger.debug(f"Fetching users for {len(user_ids)} user IDs")
            users = get_user_ids(db, user_ids)
            return f"User data: \n\n{pformat(users)}"
    except Exception as e:
        logger.exception(e)
        return f"Error fetching user: {e}"


def search_users_tool(name: str) -> str:
    """
    Search for user by name. If no users or multiple users are found with this name, ask the user for clarification.
    Alternatively use the list_users_tool to get all user IDs and names.
    :param name: user's name
    :return: list of users
    """
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
