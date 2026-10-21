from datetime import datetime
from typing import List

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.db import Base
from app.models.users import User


class Ticket(Base):
    __tablename__ = "tickets"
    id: Mapped[int] = mapped_column(primary_key=True)
    comments: Mapped[List["Comment"]] = relationship(back_populates="ticket")
    title: Mapped[str]
    description: Mapped[str]
    department: Mapped[str] = mapped_column(default=None, nullable=True)
    priority: Mapped[str]
    status: Mapped[str]
    source: Mapped[str]
    template_key: Mapped[str]
    template_data: Mapped[str]
    rule_key: Mapped[str]
    reporter_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    reporter: Mapped["User"] = relationship(foreign_keys=[reporter_id])
    assignee_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    assignee: Mapped["User"] = relationship(foreign_keys=[assignee_id])
    erp_context: Mapped[str]
    due_date: Mapped[datetime]
    created_at: Mapped[datetime]
    updated_at: Mapped[datetime]
    resolved_at: Mapped[datetime]
