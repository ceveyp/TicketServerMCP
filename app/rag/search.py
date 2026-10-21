import re
from collections import defaultdict

from sqlalchemy import select, func, or_
from sqlalchemy.orm import Session

from app.models.rag.ticket_chunks import TicketChunk
from app.rag.embedder import get_embedder

STOP = {"a", "an", "the", "and", "or", "with", "for", "to", "in", "on"}


def _keywords(text: str, max_terms: int = 6) -> list[str]:
    words = re.findall(r"[A-Za-z0-9]+", text)
    seen = set()
    out = []
    for w in words:
        key = w.lower()
        if key in STOP or key in seen:
            continue
        seen.add(key)
        out.append(w)
        if len(out) >= max_terms:
            break
    return out


def reciprocal_rank_fusion(
        ranked_lists: list[list[int]],
        k: int = 60,
) -> list[tuple[int, float]]:
    scores: dict[int, float] = defaultdict(float)
    for ids in ranked_lists:
        for rank, chunk_id in enumerate(ids, start=1):
            scores[chunk_id] += 1.0 / (k + rank)
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)


def dense_search(
        session: Session,
        query: str,
        limit: int = 20
) -> list[tuple[TicketChunk, float]]:
    embedder = get_embedder()
    query_embedding = embedder.embed(query)
    distance = TicketChunk.embedding.cosine_distance(query_embedding)
    stmt = (
        select(TicketChunk, distance.label("distance"))
        .order_by(distance)
        .limit(limit)
    )
    rows = session.execute(stmt).all()
    return [(chunk, float(dist)) for chunk, dist in rows]


def sparse_search(
        session: Session,
        query_text: str,
        limit: int = 20,
) -> list[tuple[TicketChunk, float]]:
    terms = _keywords(query_text)
    if not terms:
        return []
    term_queries = [func.plainto_tsquery("english", t) for t in terms]
    match_any = or_(*[TicketChunk.content_tsv.op("@@")(tq) for tq in term_queries])
    rank = func.ts_rank_cd(TicketChunk.content_tsv, term_queries[0])
    for tq in term_queries[1:]:
        rank = rank + func.ts_rank_cd(TicketChunk.content_tsv, tq)
    stmt = (
        select(TicketChunk, rank.label("rank"))
        .where(match_any)
        .order_by(rank.desc())
        .limit(limit)
    )
    rows = session.execute(stmt).all()
    return [(chunk, float(r)) for chunk, r in rows]


def hybrid_search(
        session: Session,
        query_text: str,
        retrieve_k: int = 20,
        final_k: int = 8
) -> list[TicketChunk]:
    dense = dense_search(session, query_text, limit=retrieve_k)
    sparse = sparse_search(session, query_text, limit=retrieve_k)
    dense_ids = [c.id for c, _ in dense]
    sparse_ids = [c.id for c, _ in sparse]
    fused = reciprocal_rank_fusion([dense_ids, sparse_ids])[:final_k]
    if not fused:
        return []
    id_to_chunk = {c.id: c for c, _ in dense}
    id_to_chunk.update({c.id: c for c, _ in sparse})
    return [id_to_chunk[cid] for cid, _ in fused if cid in id_to_chunk]
