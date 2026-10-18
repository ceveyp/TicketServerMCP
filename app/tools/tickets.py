from pprint import pformat
from typing import List

from app.crud.tickets import get_ticket, list_tickets, get_ticket_ids
from app.db.db import TicketAppSession
from app.logger import get_logger
from app.types import Priorities, Departments, TicketTypes, Statuses, SortDirections

logger = get_logger(__name__)


def get_ticket_tool(ticket_id: int) -> str:
    """
    Get full ticket including ticket body by ticket_id. Use the list_tickets_tool to get ticket IDs.
    :param ticket_id: ticket ID
    :return: ticket data
    """
    try:
        with TicketAppSession() as db:
            logger.debug(f"Fetching ticket for: {ticket_id}")
            ticket = get_ticket(db, ticket_id)
            return f"Ticket data: \n\n{pformat(ticket)}"
    except Exception as e:
        logger.exception(e)
        return f"Error reading ticket: {e}"


def get_ticket_ids_tool(ticket_ids: List[int]) -> str:
    """
    Get a batch of tickets at once. Use the list_tickets_tool to get ticket IDs.
    :param ticket_ids: ticket ID
    :return: ticket data
    """
    try:
        with TicketAppSession() as db:
            logger.debug(f"Fetching tickets for {len(ticket_ids)} IDs")
            tickets = get_ticket_ids(db, ticket_ids)
            logger.debug(f"{len(tickets)} tickets returned")
            return f"Ticket data: \n\n{pformat(tickets)}"
    except Exception as e:
        logger.exception(e)
        return f"Error reading ticket: {e}"


def list_tickets_tool(
        page: int = 1,
        page_size: int = 25,
        priority: Priorities | None = None,
        department: Departments | None = None,
        ticket_type: TicketTypes | None = None,
        status: Statuses | None = None,
        reporter_id: int | None = None,
        assignee_id: int | None = None,
        created_date_after: str | None = None,
        created_date_before: str | None = None,
        due_date_after: str | None = None,
        due_date_before: str | None = None,
        sort_direction: SortDirections = 'DESC'
) -> str:
    """
    List tickets. Paginated endpoint. Use search_users_tool or list_users_tool to get reporter/assignee IDs to filter on.
    created_at and due_date before/after accept UTC timestamps formatted in ISO 8601.
    :param page: page number
    :param page_size: page size, between 10 and 100
    :param priority: priority level (P1-P4)
    :param department: department name
    :param ticket_type: ticket type
    :param status: ticket status (open/closed/in_progress/waiting)
    :param reporter_id: ID of user creating ticket
    :param assignee_id: ID of user assigned ticket
    :param created_date_after: created after date
    :param created_date_before: created before date
    :param due_date_after: due after date
    :param due_date_before: due before date
    :param sort_direction: sort direction of results (ASC/DESC)
    :return: List of tickets with pagination data
    """
    try:
        with TicketAppSession() as db:
            logger.debug(f"Listing tickets")
            response = list_tickets(
                db=db,
                page=page,
                page_size=page_size,
                priority=priority,
                department=department,
                ticket_type=ticket_type,
                status=status,
                reporter_id=reporter_id,
                assignee_id=assignee_id,
                created_date_after=created_date_after,
                created_date_before=created_date_before,
                due_date_after=due_date_after,
                due_date_before=due_date_before,
                sort_direction=sort_direction
            )
            logger.debug(f"{len(response["items"])} tickets found")
            return f"Ticket list response data: \n\n{pformat(response)}"
    except Exception as e:
        logger.exception(e)
        return f"Error listing tickets: {e}"
