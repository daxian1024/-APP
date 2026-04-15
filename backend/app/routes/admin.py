from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy import select

from app.models.entities import Notification, Order, OrderTimeline, User
from app.services.async_db import get_session
from app.services.authz import ROLE_PERMISSIONS, permission_required
from app.services.response import fail, ok
from app.services.security import verify_signature


admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")

VALID_TRANSITIONS = {
    "pending": ["accepted"],
    "accepted": ["in_service"],
    "in_service": ["completed"],
    "completed": [],
}


def _serialize_order(item: Order) -> dict:
    return {
        "id": item.id,
        "order_no": item.order_no,
        "status": item.status,
        "payment_status": item.payment_status,
        "appointment_time": item.appointment_time,
        "user_id": item.user_id,
        "assigned_nurse_id": item.assigned_nurse_id,
        "service_name": item.service_item.name if item.service_item else "",
    }


@admin_bp.get("/orders")
@jwt_required()
@permission_required("admin:order:list")
async def list_all_orders():
    current_user_id = int(get_jwt_identity())

    async with get_session() as session:
        current_user_result = await session.execute(
            select(User).where(User.id == current_user_id)
        )
        current_user = current_user_result.scalar_one_or_none()

        query = select(Order).order_by(Order.id.desc())
        if current_user and current_user.role == "nurse":
            query = query.where(Order.assigned_nurse_id == current_user.id)

        result = await session.execute(query)
        data = result.scalars().all()

    return ok({"items": [_serialize_order(item) for item in data]})


@admin_bp.patch("/orders/<int:order_id>/assign")
@jwt_required()
@permission_required("admin:order:assign")
@verify_signature()
async def assign_nurse(order_id: int):
    data = request.get_json() or {}
    nurse_id = data.get("nurse_id")
    if not nurse_id:
        return fail(4001, "nurse_id 必填")

    async with get_session() as session:
        nurse_result = await session.execute(
            select(User).where(User.id == int(nurse_id), User.role == "nurse")
        )
        nurse = nurse_result.scalar_one_or_none()
        if not nurse:
            return fail(4042, "护士不存在", 404)

        order_result = await session.execute(select(Order).where(Order.id == order_id))
        order = order_result.scalar_one_or_none()
        if not order:
            return fail(4040, "订单不存在", 404)

        order.assigned_nurse_id = nurse.id
        session.add(
            Notification(
                user_id=nurse.id,
                channel="in_app",
                title="新订单分配",
                content=f"您有新订单待处理：{order.order_no}",
                sent=True,
            )
        )

    return ok({"order_id": order.id, "nurse_id": nurse.id}, "分配护士成功")


@admin_bp.patch("/orders/<int:order_id>/status")
@jwt_required()
@verify_signature()
async def update_order_status(order_id: int):
    user_id = int(get_jwt_identity())

    async with get_session() as session:
        user_result = await session.execute(select(User).where(User.id == user_id))
        user = user_result.scalar_one_or_none()
        if not user:
            return fail(4043, "用户不存在", 404)

        order_result = await session.execute(select(Order).where(Order.id == order_id))
        order = order_result.scalar_one_or_none()
        if not order:
            return fail(4040, "订单不存在", 404)

        if user.role == "nurse":
            if order.assigned_nurse_id != user.id:
                return fail(4031, "仅可更新分配给自己的订单", 403)
            needed = "admin:order:update_status_assigned"
        elif user.role == "admin":
            needed = "admin:order:update_status_any"
        else:
            return fail(4031, "无权限更新状态", 403)

        if needed not in ROLE_PERMISSIONS.get(user.role, set()):
            return fail(4031, f"缺少权限: {needed}", 403)

        data = request.get_json() or {}
        next_status = data.get("status", "").strip()
        if next_status not in ["pending", "accepted", "in_service", "completed"]:
            return fail(4004, "状态非法")

        if next_status not in VALID_TRANSITIONS.get(order.status, []):
            return fail(
                4005,
                f"非法状态流转: {order.status} -> {next_status}",
                400,
                {"allowed": VALID_TRANSITIONS.get(order.status, [])},
            )

        old_status = order.status
        order.status = next_status
        session.add(
            OrderTimeline(
                order_id=order.id,
                actor_user_id=user.id,
                from_status=old_status,
                to_status=next_status,
                remark=f"{user.role}更新状态",
            )
        )
        session.add(
            Notification(
                user_id=order.user_id,
                channel="in_app",
                title="订单状态更新",
                content=f"您的订单 {order.order_no} 状态已更新为 {next_status}",
                sent=True,
            )
        )

    return ok({"order_id": order.id, "status": order.status}, "状态更新成功")


@admin_bp.post("/notifications/send")
@jwt_required()
@permission_required("notification:send")
@verify_signature()
async def send_notification():
    data = request.get_json() or {}
    user_id = data.get("user_id")
    channel = (data.get("channel") or "in_app").strip()
    title = (data.get("title") or "系统通知").strip()
    content = (data.get("content") or "").strip()

    if not user_id or not content:
        return fail(4001, "user_id 和 content 必填")

    if channel not in ["in_app", "sms", "wechat"]:
        return fail(4006, "不支持的通知渠道")

    async with get_session() as session:
        msg = Notification(
            user_id=int(user_id),
            channel=channel,
            title=title,
            content=content,
            sent=True,
        )
        session.add(msg)
        await session.flush()
        msg_id = msg.id

    return ok({"id": msg_id}, "通知发送成功")