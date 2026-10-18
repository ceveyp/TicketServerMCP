from datetime import datetime
from typing import Dict, Literal, List

from pydantic import BaseModel, Field
from sqlalchemy import select, func, and_
from sqlalchemy.orm import Session

from app.crud.common import _serialize_response, _serialize_item
from app.models.comments import Comment
from app.models.tickets import Ticket

Priorities = Literal['P1', 'P2', 'P3', 'P4']

SortDirections = Literal['ASC', 'DESC']

Departments = Literal[
    'operations',
    'sales',
    'marketing',
    'it',
    'merchandising',
    'accounting',
    'screen_print',
    'art'
]

Statuses = Literal[
    'open',
    'in_progress',
    'waiting',
    'closed'
]

TicketTypes = Literal[
    'generic',
    'linesheet_update',
    'credit_memo',
    'order_modification',
    'rma_request',
    'payroll_discrepancy',
    'recruiting_request',
    'po_item_inquiry',
    'accounting_close',
    'customer_billing_inquiry',
    'system_access_request'
]


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


def get_ticket_comments(db: Session, ticket_id: int) -> List[Dict]:
    stmt = (
        select(
            Comment.author_id,
            Comment.body,
            Comment.is_system,
            Comment.created_at
        )
        .where(Comment.ticket_id == ticket_id)
        .limit(100)
    )
    results = db.execute(stmt)
    return _serialize_response([dict(row) for row in results.mappings()])


def get_ticket(db: Session, ticket_id: int) -> Dict:
    stmt = select(Ticket).where(Ticket.id == ticket_id)
    ticket: Ticket | None = db.execute(stmt).scalar_one_or_none()
    if not ticket:
        return {}
    comments = get_ticket_comments(db, ticket_id)
    response = ticket.__dict__
    response.update({"comments": comments})
    _serialize_item(response)
    return response


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
        select(
            Ticket.id,
            Ticket.title,
            Ticket.priority,
            Ticket.status,
            Ticket.department,
            Ticket.template_key,
            Ticket.reporter_id,
            Ticket.assignee_id,
            Ticket.due_date,
            Ticket.created_at
        )
        .limit(args.page_size)
        .offset(offset_value)
        .order_by(order_by)
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
    tickets = [dict(row) for row in results.mappings()]
    tickets = _serialize_response(tickets)
    response = {"pagination": pagination, "items": tickets}
    return response
