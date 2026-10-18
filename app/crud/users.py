from typing import List, Dict

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.crud.common import _serialize_item, _serialize_response
from app.models.users import User


def list_users(db: Session) -> List[Dict]:
    stmt = select(User.id, User.name)
    results = db.execute(stmt)
    return [dict(result) for result in results.mappings()]


def get_user(db: Session, user_id: int) -> Dict:
    stmt = select(User).where(User.id == user_id)
    user = db.execute(stmt).scalar_one_or_none()
    if not user:
        return {}
    return _serialize_item(user.__dict__)


def get_user_ids(db: Session, user_ids: List[int]) -> List[Dict]:
    if not user_ids:
        return []
    for user_id in user_ids:
        if not isinstance(user_id, int):
            raise ValueError(f"User IDs format error")
    stmt = select(User).where(User.id.in_(user_ids))
    users = db.execute(stmt).scalars().all()
    return _serialize_response([user.__dict__ for user in users])


def search_users(db: Session, name: str) -> List[User]:
    if not isinstance(name, str) or not name.strip():
        return []
    stmt = select(User).where(User.name.ilike(f"%{name}%"))
    users = db.execute(stmt).scalars()
    if not users:
        return []
    return list(users.all())
