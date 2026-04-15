from sqlalchemy import select

from app.models.entities import Complaint, Order, Review
from app.services.async_db import get_session


async def fetch_reporting_data():
    async with get_session() as session:
        orders_result = await session.execute(select(Order))
        orders = orders_result.scalars().all()

        reviews_result = await session.execute(select(Review))
        reviews = reviews_result.scalars().all()

        complaints_result = await session.execute(select(Complaint))
        complaints = complaints_result.scalars().all()

    return {
        "orders": orders,
        "reviews": reviews,
        "complaints": complaints,
    }