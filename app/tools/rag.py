from pprint import pformat
from typing import List

from app.db.db import VectorDBSession
from app.logger import get_logger
from app.models.rag.ticket_chunks import TicketChunk
from app.rag.search import hybrid_search, sparse_search

logger = get_logger(__name__)


def _serialize_ticket_chunks(chunks: List[TicketChunk]) -> str:
    output = ""
    for chunk in chunks:
        output += "-------TICKET CHUNK-------"
        output += f"\n\nSection Type: {chunk.section_type}"
        output += f"\nChunk: \n\n{chunk.content}\n\n"
    return output


def keyword_search_tool(keywords: List[str]) -> str:
    """
    Do keyword search only on a list of keywords.
    :param keywords: list of keywords
    :return: relevant chunks per keyword and chunk metadata
    """
    try:
        with VectorDBSession() as db:
            logger.debug(f"Fetching chunks for keywords: {keywords}")
            all_chunks = {}
            for keyword in keywords:
                results = sparse_search(db, keyword, limit=10)
                keyword_chunks: List[TicketChunk] = [t[0] for t in results]
                all_chunks[keyword] = _serialize_ticket_chunks(keyword_chunks)
            return pformat(all_chunks)
    except Exception as e:
        logger.exception(e)
        return f"Error in hybrid search: {e}"


def hybrid_search_tool(query_text: str) -> str:
    """
    Do hybrid search, semantic search and keyword search and rerank results.
    :param query_text: query text
    :return: relevant chunks and chunk metadata
    """
    try:
        with VectorDBSession() as db:
            logger.debug(f"Fetching chunks for query: {query_text}")
            chunks = hybrid_search(db, query_text)
            logger.debug(f"{len(chunks)} chunks returned")
            return _serialize_ticket_chunks(chunks)
    except Exception as e:
        logger.exception(e)
        return f"Error in hybrid search: {e}"
