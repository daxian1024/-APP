from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.entities import Order, User, OrderTimeline, Notification
from app.services.authz import permission_required
from app.services.response import ok, fail
from app.services.security import verify_signature


admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")

VALID_TRANSITIONS = {
    "pending": ["accepted"],
    "accepted": ["in_service"],
    "in_service": ["completed"],
    "completed": [],
}


@admin_bp.get("/orders")
@jwt_required()
@permission_required("admin:order:list")
def list_all_orders():
    current_user = User.query.get(int(get_jwt_identity()))
    query = Order.query.order_by(Order.id.desc())
    if current_user and current_user.role == "nurse":
        query = query.filter_by(assigned_nurse_id=current_user.id)

    data = query.all()
    return ok(
        {
            "items": [
                {
                    "id": item.id,
                    "order_no": item.order_no,
                    "status": item.status,
                    "payment_status": item.payment_status,
                    "appointment_time": item.appointment_time,
                    "user_id": item.user_id,
                    "assigned_nurse_id": item.assigned_nurse_id,
                    "service_name": item.service_item.name if item.service_item else "",
                }
                for item in data
            ]
        }
    )


@admin_bp.patch("/orders/<int:order_id>/assign")
@jwt_required()
@permission_required("admin:order:assign")
@verify_signature()
def assign_nurse(order_id: int):
    data = request.get_json() or {}
    nurse_id = data.get("nurse_id")
    if not nurse_id:
        return fail(4001, "nurse_id 必填")

    nurse = User.query.filter_by(id=nurse_id, role="nurse").first()
    if not nurse:
        return fail(4042, "护士不存在", 404)

    order = Order.query.get(order_id)
    if not order:
        return fail(4040, "订单不存在", 404)

    order.assigned_nurse_id = nurse.id
    db.session.add(
        Notification(
            user_id=nurse.id,
            channel="in_app",
            title="新订单分配",
            content=f"您有新订单待处理：{order.order_no}",
            sent=True,
        )
    )
    db.session.commit()
    return ok({"order_id": order.id, "nurse_id": nurse.id}, "分配护士成功")


@admin_bp.patch("/orders/<int:order_id>/status")
@jwt_required()
@verify_signature()
def update_order_status(order_id: int):
    user = User.query.get(int(get_jwt_identity()))
    order = Order.query.get(order_id)
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

    from app.services.authz import ROLE_PERMISSIONS

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

    old = order.status
    order.status = next_status
    db.session.add(
        OrderTimeline(
            order_id=order.id,
            actor_user_id=user.id,
            from_status=old,
            to_status=next_status,
            remark=f"{user.role}更新状态",
        )
    )

    db.session.add(
        Notification(
            user_id=order.user_id,
            channel="in_app",
            title="订单状态更新",
            content=f"您的订单 {order.order_no} 状态已更新为 {next_status}",
            sent=True,
        )
    )
    db.session.commit()
    return ok({"order_id": order.id, "status": order.status}, "状态更新成功")


@admin_bp.post("/notifications/send")
@jwt_required()
@permission_required("notification:send")
@verify_signature()
def send_notification():
    data = request.get_json() or {}
    user_id = data.get("user_id")
    channel = (data.get("channel") or "in_app").strip()
    title = (data.get("title") or "系统通知").strip()
    content = (data.get("content") or "").strip()

    if not user_id or not content:
        return fail(4001, "user_id 和 content 必填")

    if channel not in ["in_app", "sms", "wechat"]:
        return fail(4006, "不支持的通知渠道")

    msg = Notification(
        user_id=int(user_id),
        channel=channel,
        title=title,
        content=content,
        sent=True,
    )
    db.session.add(msg)
    db.session.commit()
    return ok({"id": msg.id}, "通知发送成功")
