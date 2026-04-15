import asyncio
from collections.abc import Callable
from contextlib import asynccontextmanager
from typing import TypeVar

from app.extensions import AsyncSessionLocal

T = TypeVar("T")


@asynccontextmanager
async def get_session():
    if AsyncSessionLocal is None:
        raise RuntimeError("AsyncSessionLocal has not been initialized")
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def run_db(fn: Callable[[], T]) -> T:
    return await asyncio.to_thread(fn)
