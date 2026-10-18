from datetime import datetime
from typing import Dict, List, Sequence

from pydantic import BaseModel, Field
from sqlalchemy import select, func, and_
from sqlalchemy.orm import Session, joinedload

from app.crud.common import _serialize_item
from app.models.comments import Comment
from app.models.tickets import Ticket
from app.types import Priorities, Departments, TicketTypes, Statuses, SortDirections


class ListTicketArgs(BaseModel):
    page: int = Field(default=1, ge=1, le=500, description="Page number between 1 and 500")
    page_size: int = Field(default=25, ge=10, le=100, description="Items per page between 10 and 100")
    priority: Priorities | None = None
    department: Departments | None = None
    ticket_type: TicketTypes | None = None
    status: Statuses | None = None
    reporter_id: int | None = None
    assignee_id: int | None = None
    created_date_after: datetime | None = None
    created_date_before: datetime | None = None
    due_date_after: datetime | None = None
    due_date_before: datetime | None = None
    sort_direction: SortDirections = 'DESC'


def _serialize_ticket(ticket: Ticket, full: bool = False) -> Dict:
    data = _serialize_item(ticket.__dict__)
    if not full:
        del data["description"]
        del data["template_data"]
        del data["rule_key"]
        del data["erp_context"]
    if ticket.assignee:
        data["assignee"] = {
            "id": ticket.assignee.id,
            "name": ticket.assignee.name,
        }
    if ticket.reporter:
        data["reporter"] = {
            "id": ticket.reporter.id,
            "name": ticket.reporter.name
        }
    return data


def _serialize_tickets(tickets: Sequence[Ticket]) -> List[Dict]:
    return [_serialize_ticket(ticket) for ticket in tickets]


def get_ticket_comments(db: Session, ticket_id: int) -> List[Dict]:
    stmt = (
        select(Comment)
        .where(Comment.ticket_id == ticket_id)
        .limit(100)
        .options(joinedload(Comment.author))
    )
    results = db.execute(stmt)
    comments = results.scalars().all()
    return [_serialize_item({
        "author": {
            "id": comment.author.id,
            "name": comment.author.name
        },
        "body": comment.body,
        "created_at": comment.created_at,
        "is_system": comment.is_system
    }) for comment in comments]


def get_ticket(db: Session, ticket_id: int) -> Dict:
    stmt = (
        select(Ticket)
        .where(Ticket.id == ticket_id)
        .options(
            joinedload(Ticket.reporter),
            joinedload(Ticket.assignee)
        )
    )
    ticket: Ticket | None = db.execute(stmt).scalar_one_or_none()
    if not ticket:
        return {}
    comments = get_ticket_comments(db, ticket_id)
    response = _serialize_ticket(ticket, True)
    response.update({"comments": comments})
    return response


def get_ticket_ids(db: Session, ticket_ids: List[int]) -> List[Dict]:
    if len(ticket_ids) > 50:
        raise ValueError("Between 1 and 50 tickets can be queried at once")
    for ticket_id in ticket_ids:
        if not isinstance(ticket_id, int):
            raise ValueError("Could not validate ticket IDs")
    stmt = (
        select(Ticket)
        .where(Ticket.id.in_(ticket_ids))
        .options(
            joinedload(Ticket.reporter),
            joinedload(Ticket.assignee)
        )
    )
    tickets = db.execute(stmt).scalars().all()
    return _serialize_tickets(tickets)


def list_tickets(
        db: Session,
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
) -> Dict:
    args = ListTicketArgs(
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
    offset_value = (args.page - 1) * args.page_size
    order_by = Ticket.id.desc() if sort_direction == 'DESC' else Ticket.id.asc()
    stmt = (
        select(Ticket)
        .limit(args.page_size)
        .offset(offset_value)
        .order_by(order_by)
        .options(
            joinedload(Ticket.reporter),
            joinedload(Ticket.assignee)
        )
    )
    count_stmt = select(func.count(Ticket.id))
    filters = []
    if args.priority:
        filters.append(Ticket.priority == args.priority)
    if args.department:
        filters.append(Ticket.department == args.department)
    if args.status:
        filters.append(Ticket.status == args.status)
    if args.reporter_id:
        filters.append(Ticket.reporter_id == args.reporter_id)
    if args.assignee_id:
        filters.append(Ticket.assignee_id == args.assignee_id)
    if args.ticket_type:
        filters.append(Ticket.template_key == args.ticket_type)
    if args.created_date_after:
        filters.append(Ticket.created_at > args.created_date_after)
    if args.created_date_before:
        filters.append(Ticket.created_at < args.created_date_before)
    if args.due_date_after:
        filters.append(Ticket.due_date < args.due_date_after)
    if args.due_date_before:
        filters.append(Ticket.due_date < args.due_date_before)
    stmt = stmt.where(and_(*filters))
    count_stmt = count_stmt.where(and_(*filters))
    count = db.scalar(count_stmt) or 0
    total_pages = (count + args.page_size - 1) // args.page_size if count > 0 else 0
    pagination = {
        "page": args.page,
        "page_size": args.page_size,
        "total": count,
        "total_pages": total_pages
    }
    results = db.execute(stmt)
    tickets = results.scalars().all()
    tickets = _serialize_tickets(tickets)
    response = {"pagination": pagination, "items": tickets}
    return response
