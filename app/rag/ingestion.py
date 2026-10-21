from sqlalchemy import select
from sqlalchemy.orm import selectinload, joinedload, Session

from app.db.db import TicketAppSession, VectorDBSession
from app.logger import get_logger
from app.models.comments import Comment
from app.models.rag.ticket_chunks import TicketChunk
from app.models.rag.tickets import VDBTicket
from app.models.tickets import Ticket as TATicket
from app.rag.embedder import get_embedder, Embedder

logger = get_logger(__name__)


def _create_chunk(
        metadata_text: str,
        content: str,
        embedder: Embedder,
        chunk_index: int,
        section_type: str
) -> TicketChunk:
    chunk_content = f"{metadata_text}\n\n{content}"
    token_count = embedder.count(chunk_content)
    embedding = embedder.embed(chunk_content)
    return TicketChunk(
        chunk_index=chunk_index,
        section_type=section_type,
        content=chunk_content,
        token_count=token_count,
        embedding=embedding
    )


def _chunk_and_embed_ticket(ticket: TATicket) -> VDBTicket:
    embedder = get_embedder()

    metadata = f"ID: {ticket.id} | Title: {ticket.title} | Department: {ticket.department}"
    metadata += f" | Priority: {ticket.priority} | Ticket type: {ticket.template_key}"
    if ticket.reporter:
        metadata += f" | Reporter: {ticket.reporter.name}"
    if ticket.assignee:
        metadata += f" | Assignee: {ticket.assignee.name}"

    vdb_ticket = VDBTicket(id=ticket.id, title=ticket.title)
    chunks = []

    # Chunk ticket body
    body_chunk = _create_chunk(metadata, ticket.description, embedder, 1, "ticket_body")
    chunks.append(body_chunk)

    # Chunk ticket template data
    template_data_chunk = _create_chunk(metadata, ticket.template_data, embedder, 2, "template_data")
    chunks.append(template_data_chunk)

    # Chunk ticket comments
    for i, comment in enumerate(ticket.comments, 3):
        comment_chunk_content = f"---------COMMENT:---------"
        if comment.author:
            comment_chunk_content += f"\nAuthor: {comment.author.name}"
        comment_chunk_content += f"\nComment: {comment.body}"
        template_data_chunk = _create_chunk(metadata, comment_chunk_content, embedder, i, "comment")
        chunks.append(template_data_chunk)

    vdb_ticket.chunks = chunks
    return vdb_ticket


def _get_existing_ticket_ids(db: Session) -> set[int]:
    stmt = select(VDBTicket.id)
    ticket_ids = db.execute(stmt).scalars().all()
    return set(ticket_ids)


def ingest_new_tickets():
    with TicketAppSession() as db:
        with VectorDBSession() as vdb:
            existing_ticket_ids = _get_existing_ticket_ids(vdb)
            stmt = (
                select(TATicket)
                .options(
                    joinedload(TATicket.reporter),
                    joinedload(TATicket.assignee),
                    selectinload(TATicket.comments)
                    .joinedload(Comment.author)
                )
                .where(TATicket.id.notin_(list(existing_ticket_ids)))
            )
            results = db.execute(stmt)
            for row in results.scalars().yield_per(100):
                ticket: TATicket = row
                logger.debug(f"Ingesting ticket: {ticket.id}")
                vdb_ticket = _chunk_and_embed_ticket(ticket)
                vdb.add(vdb_ticket)
                vdb.commit()

            # TODO: TEMPLATE DATA IN GET TICKET BY ID
