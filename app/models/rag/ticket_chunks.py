from sqlalchemy import ForeignKey, Computed
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector

from app.db.db import VDBBase
from app.models.rag.tickets import VDBTicket
from app.settings import get_settings

EMBEDDING_SIZE = get_settings().embedding_size


class TicketChunk(VDBBase):
    __tablename__ = "ticket_chunks"
    id: Mapped[int] = mapped_column(primary_key=True)
    ticket_id: Mapped[int] = mapped_column(ForeignKey("tickets.id"))
    ticket: Mapped["VDBTicket"] = relationship(back_populates="chunks")
    chunk_index: Mapped[int]
    section_type: Mapped[str]
    content: Mapped[str]
    embedding: Mapped[str] = mapped_column(Vector(EMBEDDING_SIZE))
    token_count: Mapped[int]
    content_tsv: Mapped[str] = mapped_column(
        TSVECTOR,
        Computed("to_tsvector('english', content)", persisted=True)
    )
