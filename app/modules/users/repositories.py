import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.users.models import User


class UserRepository:
    """All SQL for users lives here"""

    def __init__(self, session: AsyncSession) -> None:
        self.db_session = session

    async def add(self, user: User) -> User:
        self.db_session.add(user)
        await self.db_session.flush()
        await self.db_session.refresh(user)
        return user

    async def get_by_email(self, email: str) -> User | None:
        return await self.db_session.scalar(select(User).where(User.email == email))

    async def get_by_id(self, user_id: uuid.UUID) -> User | None:
        return await self.db_session.get(User, user_id)
