from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column

from app.db.db import Base


class Ticket(Base):
    __tablename__ = "tickets"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    description: Mapped[str]
    department: Mapped[str]
    priority: Mapped[str]
    status: Mapped[str]
    source: Mapped[str]
    template_key: Mapped[str]
    template_data: Mapped[str]
    rule_key: Mapped[str]
    reporter_id: Mapped[int]
    assignee_id: Mapped[int]
    erp_context: Mapped[str]
    due_date: Mapped[datetime]
    created_at: Mapped[datetime]
    updated_at: Mapped[datetime]
    resolved_at: Mapped[datetime]
