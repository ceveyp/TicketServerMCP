from typing import List, Dict

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.users import User


def list_users(db: Session) -> List[Dict]:
    stmt = select(User.id, User.name)
    results = db.execute(stmt)
    return [dict(result) for result in results.mappings()]


def search_users(db: Session, name: str) -> List[User]:
    if not isinstance(name, str) or not name.strip():
        return []
    stmt = select(User).where(User.name.ilike(f"%{name}%"))
    users = db.execute(stmt).scalars()
    if not users:
        return []
    return list(users.all())
