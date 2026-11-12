"""Promote a registered user to admin.

Usage: uv run python -m scripts.make_admin <email>
"""

import asyncio
import sys

from sqlalchemy import update

from app.db.session import SessionLocal
from app.modules.users.models import Role, User


async def main(email: str) -> None:
    async with SessionLocal() as session:
        result = await session.execute(
            update(User).where(User.email == email.lower()).values(role=Role.ADMIN)
        )
        await session.commit()
    if result.rowcount:
        print(f"{email} is now an admin.")
    else:
        print(f"No user with email {email}. Register first.")


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1]))
