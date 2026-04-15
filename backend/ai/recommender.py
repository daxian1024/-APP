from sqlalchemy import select

from app.models.entities import Order, ServiceItem
from app.services.async_db import get_session


async def recommend_services(user_id: int, top_k: int = 5):
    async with get_session() as session:
        order_result = await session.execute(
            select(Order).where(Order.user_id == user_id)
        )
        orders = order_result.scalars().all()

        service_ids = [order.service_item_id for order in orders]
        if service_ids:
            service_result = await session.execute(
                select(ServiceItem).where(ServiceItem.id.in_(service_ids))
            )
            services = service_result.scalars().all()
        else:
            service_result = await session.execute(
                select(ServiceItem).order_by(ServiceItem.id.desc()).limit(top_k)
            )
            services = service_result.scalars().all()

    if service_ids and services:
        return [
            {
                "id": service.id,
                "name": service.name,
                "description": service.description,
                "price": service.price,
                "duration_minutes": service.duration_minutes,
                "is_active": service.is_active,
            }
            for service in services[:top_k]
        ]

    return [
        {
            "id": service.id,
            "name": service.name,
            "description": service.description,
            "price": service.price,
            "duration_minutes": service.duration_minutes,
            "is_active": service.is_active,
        }
        for service in services
    ]