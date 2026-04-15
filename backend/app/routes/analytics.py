from datetime import date, timedelta

from flask import Blueprint, request
from sqlalchemy import func, select

from app.models.entities import Complaint, Order, Review, ServiceItem, User
from app.services.async_db import get_session


analytics_bp = Blueprint("analytics", __name__, url_prefix="/api/analytics")


def _parse_days():
    try:
        days = int(request.args.get("days", 7))
    except ValueError:
        days = 7
    return max(1, min(days, 90))


@analytics_bp.get("/overview")
async def overview():
    async with get_session() as session:
        total_orders_result = await session.execute(select(func.count(Order.id)))
        total_orders = total_orders_result.scalar_one()

        completed_orders_result = await session.execute(
            select(func.count(Order.id)).where(Order.status == "completed")
        )
        completed_orders = completed_orders_result.scalar_one()

        pending_orders_result = await session.execute(
            select(func.count(Order.id)).where(Order.status == "pending")
        )
        pending_orders = pending_orders_result.scalar_one()

        complaints_result = await session.execute(select(func.count(Complaint.id)))
        complaint_count = complaints_result.scalar_one()

        avg_rating_result = await session.execute(select(func.avg(Review.rating)))
        avg_rating = avg_rating_result.scalar_one()

    return {
        "total_orders": total_orders,
        "completed_orders": completed_orders,
        "pending_orders": pending_orders,
        "completion_rate": round(completed_orders / total_orders, 4) if total_orders else 0,
        "avg_rating": round(float(avg_rating), 2) if avg_rating is not None else 0,
        "complaint_count": complaint_count,
    }


@analytics_bp.get("/summary")
async def summary():
    data = await overview()
    return data


@analytics_bp.get("/orders-trend")
async def orders_trend():
    days = _parse_days()
    end_date = date.today()
    start_date = end_date - timedelta(days=days - 1)

    async with get_session() as session:
        result = await session.execute(
            select(
                func.date(Order.created_at).label("day"),
                func.count(Order.id).label("count"),
            )
            .where(Order.created_at >= start_date)
            .group_by(func.date(Order.created_at))
            .order_by(func.date(Order.created_at))
        )
        rows = result.all()

    counts = {str(day): int(count) for day, count in rows}
    items = []
    for i in range(days):
        d = start_date + timedelta(days=i)
        key = d.isoformat()
        items.append({"date": key, "count": counts.get(key, 0)})

    return {"days": days, "items": items}


@analytics_bp.get("/service-distribution")
async def service_distribution():
    async with get_session() as session:
        result = await session.execute(
            select(
                Order.service_item_id,
                ServiceItem.name,
                func.count(Order.id).label("count"),
            )
            .join(ServiceItem, ServiceItem.id == Order.service_item_id)
            .group_by(Order.service_item_id, ServiceItem.name)
            .order_by(func.count(Order.id).desc())
        )
        rows = result.all()

    return {
        "items": [
            {
                "service_item_id": service_item_id,
                "service_name": service_name,
                "count": int(count),
            }
            for service_item_id, service_name, count in rows
        ]
    }


@analytics_bp.get("/order-status-distribution")
async def order_status_distribution():
    async with get_session() as session:
        result = await session.execute(
            select(
                Order.status,
                func.count(Order.id).label("count"),
            )
            .group_by(Order.status)
            .order_by(func.count(Order.id).desc())
        )
        rows = result.all()

    return {
        "items": [
            {"status": status, "count": int(count)}
            for status, count in rows
        ]
    }


@analytics_bp.get("/nurse-ranking")
async def nurse_ranking():
    async with get_session() as session:
        result = await session.execute(
            select(
                User.id,
                User.username,
                func.count(Order.id).label("count"),
            )
            .join(Order, Order.assigned_nurse_id == User.id)
            .where(User.role == "nurse")
            .group_by(User.id, User.username)
            .order_by(func.count(Order.id).desc())
        )
        rows = result.all()

    return {
        "items": [
            {
                "nurse_id": nurse_id,
                "nurse_name": nurse_name,
                "count": int(count),
            }
            for nurse_id, nurse_name, count in rows
        ]
    }


@analytics_bp.get("/complaint-trend")
async def complaint_trend():
    days = _parse_days()
    end_date = date.today()
    start_date = end_date - timedelta(days=days - 1)

    async with get_session() as session:
        result = await session.execute(
            select(
                func.date(Complaint.created_at).label("day"),
                func.count(Complaint.id).label("count"),
            )
            .where(Complaint.created_at >= start_date)
            .group_by(func.date(Complaint.created_at))
            .order_by(func.date(Complaint.created_at))
        )
        rows = result.all()

    counts = {str(day): int(count) for day, count in rows}
    items = []
    for i in range(days):
        d = start_date + timedelta(days=i)
        key = d.isoformat()
        items.append({"date": key, "count": counts.get(key, 0)})

    return {"days": days, "items": items}