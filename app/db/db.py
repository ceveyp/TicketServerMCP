from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.settings import get_settings

settings = get_settings()

TicketAppSession = sessionmaker(create_engine(settings.ticket_app_db_url))
VectorDBSession = sessionmaker(create_engine(settings.pgvector_db_url))


class Base(DeclarativeBase):
    pass


class VDBBase(DeclarativeBase):
    pass
