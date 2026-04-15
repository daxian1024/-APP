import asyncio
from collections.abc import Callable
from typing import TypeVar

T = TypeVar("T")


async def run_db(fn: Callable[[], T]) -> T:
    return await asyncio.to_thread(fn)
