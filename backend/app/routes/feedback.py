from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.extensions import db
from app.models.entities import Review, Complaint, Order
from app.services.authz import permission_required
from app.services.response import ok, fail


feedback_bp = Blueprint("feedback", __name__, url_prefix="/api/feedback")


@feedback_bp.post("/reviews")
@jwt_required()
@permission_required("feedback:create")
def create_review():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}

    order_id = data.get("order_id")
    rating = int(data.get("rating", 0))

    if not order_id or rating not in [1, 2, 3, 4, 5]:
        return fail(4001, "参数不合法")

    order = Order.query.filter_by(id=order_id, user_id=user_id).first()
    if not order:
        return fail(4040, "订单不存在", 404)

    item = Review(order_id=order_id, user_id=user_id, rating=rating, comment=data.get("comment", ""))
    db.session.add(item)
    db.session.commit()
    return ok({"id": item.id}, "评价提交成功")


@feedback_bp.get("/reviews")
@jwt_required()
@permission_required("feedback:create")
def list_my_reviews():
    user_id = int(get_jwt_identity())
    items = Review.query.filter_by(user_id=user_id).order_by(Review.id.desc()).all()
    return ok(
        {
            "items": [
                {
                    "id": r.id,
                    "order_id": r.order_id,
                    "rating": r.rating,
                    "comment": r.comment,
                    "created_at": r.created_at.isoformat(),
                }
                for r in items
            ]
        }
    )


@feedback_bp.post("/complaints")
@jwt_required()
@permission_required("feedback:create")
def create_complaint():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}

    content = data.get("content", "").strip()
    if not content:
        return fail(4001, "投诉内容不能为空")

    item = Complaint(order_id=data.get("order_id"), user_id=user_id, content=content)
    db.session.add(item)
    db.session.commit()
    return ok({"id": item.id}, "投诉提交成功")


@feedback_bp.get("/complaints")
@jwt_required()
@permission_required("feedback:create")
def list_my_complaints():
    user_id = int(get_jwt_identity())
    items = Complaint.query.filter_by(user_id=user_id).order_by(Complaint.id.desc()).all()
    return ok(
        {
            "items": [
                {
                    "id": c.id,
                    "order_id": c.order_id,
                    "content": c.content,
                    "status": c.status,
                    "created_at": c.created_at.isoformat(),
                }
                for c in items
            ]
        }
    )
