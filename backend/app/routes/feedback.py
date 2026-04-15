from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy import select

from app.models.entities import Complaint, Order, Review
from app.services.async_db import get_session
from app.services.authz import permission_required
from app.services.response import fail, ok


feedback_bp = Blueprint("feedback", __name__, url_prefix="/api/feedback")


@feedback_bp.post("/reviews")
@jwt_required()
@permission_required("feedback:create")
async def create_review():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}

    order_id = data.get("order_id")
    rating = int(data.get("rating", 0))

    if not order_id or rating not in [1, 2, 3, 4, 5]:
        return fail(4001, "参数不合法")

    async with get_session() as session:
        order_result = await session.execute(
            select(Order).where(Order.id == order_id, Order.user_id == user_id)
        )
        order = order_result.scalar_one_or_none()
        if not order:
            return fail(4040, "订单不存在", 404)

        item = Review(
            order_id=order_id,
            user_id=user_id,
            rating=rating,
            comment=data.get("comment", ""),
        )
        session.add(item)
        await session.flush()
        review_id = item.id

    return ok({"id": review_id}, "评价提交成功")


@feedback_bp.get("/reviews")
@jwt_required()
@permission_required("feedback:create")
async def list_my_reviews():
    user_id = int(get_jwt_identity())

    async with get_session() as session:
        result = await session.execute(
            select(Review).where(Review.user_id == user_id).order_by(Review.id.desc())
        )
        items = result.scalars().all()

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
async def create_complaint():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}

    content = data.get("content", "").strip()
    if not content:
        return fail(4001, "投诉内容不能为空")

    async with get_session() as session:
        item = Complaint(
            order_id=data.get("order_id"),
            user_id=user_id,
            content=content,
        )
        session.add(item)
        await session.flush()
        complaint_id = item.id

    return ok({"id": complaint_id}, "投诉提交成功")


@feedback_bp.get("/complaints")
@jwt_required()
@permission_required("feedback:create")
async def list_my_complaints():
    user_id = int(get_jwt_identity())

    async with get_session() as session:
        result = await session.execute(
            select(Complaint).where(Complaint.user_id == user_id).order_by(Complaint.id.desc())
        )
        items = result.scalars().all()

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