from collections import Counter
from app import create_app
from app.models.entities import Order, ServiceItem


app = create_app()


def recommend_services_for_user(user_id: int, top_k: int = 3):
    with app.app_context():
        orders = Order.query.filter_by(user_id=user_id).all()
        if not orders:
            return cold_start_recommend(top_k)

        freq = Counter([o.service_item_id for o in orders])
        service_ids = [sid for sid, _ in freq.most_common(top_k)]
        services = ServiceItem.query.filter(ServiceItem.id.in_(service_ids)).all()
        return [
            {"id": s.id, "name": s.name, "price": s.price, "reason": "基于历史下单偏好"}
            for s in services
        ]


def cold_start_recommend(top_k: int = 3):
    services = ServiceItem.query.order_by(ServiceItem.id.desc()).limit(top_k).all()
    return [{"id": s.id, "name": s.name, "price": s.price, "reason": "热门服务"} for s in services]
