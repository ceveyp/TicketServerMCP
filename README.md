# TicketServerMCP

An MCP server that connects LLMs to a support ticket app. Clients can query tickets and users, load full ticket records (including comments), and search ticket content using a hybrid of semantic and keyword retrieval.

The server is built with [FastMCP](https://github.com/jlowin/fastmcp). It reads data from PostgreSQL via SQLAlchemy, generates embeddings through OpenRouter, and stores searchable chunks in a separate PostgreSQL database with pgvector.

## Capabilities

**Tickets.** Paginated listing with filters for priority, department, status, reporter, assignee, and date ranges. Individual tickets can be loaded by ID, or several at once in a batch request.

**Users.** List all users, search by name (case-insensitive substring), or fetch specific users by ID.

**Search.** Ticket text is chunked and embedded for retrieval. The hybrid search tool combines vector similarity with full-text search and reranks the combined results. A separate keyword-only tool is available when semantic search is not needed.

## How the data is split

Operational data lives in the ticket application database: users, tickets, and comments. MCP tools that list or fetch tickets and users use this database (`TicketAppSession`, models under `app/models/`).

Search runs against a second database (`VectorDBSession`, models under `app/models/rag/`). A background ingestion process reads tickets from the app database, splits each ticket into chunks (body, template fields, comments), embeds the chunks, and writes them to `ticket_chunks`. Keyword search uses a persisted `tsvector` column derived from chunk text.

Ingestion is implemented in `app.rag.ingestion.ingest_new_tickets`. 