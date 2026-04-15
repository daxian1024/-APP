from flask import Blueprint
from sqlalchemy import func, select

from app.models.entities import Complaint, Order, Review, ServiceItem
from app.services.async_db import get_session


analytics_bp = Blueprint("analytics", __name__, url_prefix="/api/analytics")


@analytics_bp.get("/summary")
async def summary():
    async with get_session() as session:
        total_orders_result = await session.execute(select(func.count(Order.id)))
        total_orders = total_orders_result.scalar_one()

        completed_orders_result = await session.execute(
            select(func.count(Order.id)).where(Order.status == "completed")
        )
        completed_orders = completed_orders_result.scalar_one()

        complaints_result = await session.execute(select(func.count(Complaint.id)))
        complaints = complaints_result.scalar_one()

        avg_rating = await db_avg_rating(session)

        service_counts_result = await session.execute(
            select(Order.service_item_id, func.count(Order.id))
            .group_by(Order.service_item_id)
        )
        service_counts = service_counts_result.all()

        services_result = await session.execute(select(ServiceItem))
        service_map = {s.id: s.name for s in services_result.scalars().all()}

    return {
        "total_orders": total_orders,
        "completed_orders": completed_orders,
        "completion_rate": round(completed_orders / total_orders, 4) if total_orders else 0,
        "avg_rating": avg_rating,
        "complaint_count": complaints,
        "service_order_count": [
            {"service_item_id": sid, "service_name": service_map.get(sid, ""), "count": cnt}
            for sid, cnt in service_counts
        ],
    }


async def db_avg_rating(session):
    value_result = await session.execute(select(func.avg(Review.rating)))
    value = value_result.scalar_one()
    if value is None:
        return 0
    return round(float(value), 2)