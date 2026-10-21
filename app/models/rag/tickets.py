from typing import List

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.db import VDBBase


class VDBTicket(VDBBase):
    __tablename__ = "tickets"
    id: Mapped[int] = mapped_column(primary_key=True)
    chunks: Mapped[List["TicketChunk"]] = relationship(back_populates="ticket")
    title: Mapped[str]
