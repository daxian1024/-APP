from flask import Blueprint
from sqlalchemy import func
from app.models.entities import Order, Review, Complaint, ServiceItem


analytics_bp = Blueprint("analytics", __name__, url_prefix="/api/analytics")


@analytics_bp.get("/summary")
def summary():
    total_orders = Order.query.count()
    completed_orders = Order.query.filter_by(status="completed").count()
    avg_rating = db_avg_rating()
    complaints = Complaint.query.count()

    service_counts = (
        Order.query.with_entities(Order.service_item_id, func.count(Order.id))
        .group_by(Order.service_item_id)
        .all()
    )
    service_map = {s.id: s.name for s in ServiceItem.query.all()}

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


def db_avg_rating():
    value = Review.query.with_entities(func.avg(Review.rating)).scalar()
    if value is None:
        return 0
    return round(float(value), 2)
