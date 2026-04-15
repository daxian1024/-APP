import uuid
from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.extensions import db
from app.models.entities import Order, ServiceItem, Address, OrderTimeline, PaymentRecord
from app.services.response import ok, fail
from app.services.authz import permission_required
from app.services.security import rate_limit


order_bp = Blueprint("orders", __name__, url_prefix="/api/orders")


@order_bp.get("")
@jwt_required()
@permission_required("order:view:self")
def list_orders():
    user_id = int(get_jwt_identity())
    data = Order.query.filter_by(user_id=user_id).order_by(Order.id.desc()).all()
    return ok(
        {
            "items": [
                {
                    "id": item.id,
                    "order_no": item.order_no,
                    "service_name": item.service_item.name if item.service_item else "",
                    "appointment_time": item.appointment_time,
                    "status": item.status,
                    "payment_status": item.payment_status,
                    "note": item.note,
                }
                for item in data
            ]
        }
    )


@order_bp.get("/<int:order_id>/timeline")
@jwt_required()
@permission_required("order:view:self")
def get_timeline(order_id: int):
    user_id = int(get_jwt_identity())
    order = Order.query.filter_by(id=order_id, user_id=user_id).first()
    if not order:
        return fail(4040, "订单不存在", 404)

    items = (
        OrderTimeline.query.filter_by(order_id=order_id)
        .order_by(OrderTimeline.created_at.asc())
        .all()
    )
    return ok(
        {
            "items": [
                {
                    "id": i.id,
                    "from_status": i.from_status,
                    "to_status": i.to_status,
                    "remark": i.remark,
                    "created_at": i.created_at.isoformat(),
                }
                for i in items
            ]
        }
    )


@order_bp.post("")
@jwt_required()
@permission_required("order:create")
@rate_limit("order_create")
def create_order():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}

    service_item_id = data.get("service_item_id")
    address_id = data.get("address_id")
    appointment_time = data.get("appointment_time")

    if not service_item_id or not address_id or not appointment_time:
        return fail(4001, "参数缺失")

    service_item = ServiceItem.query.get(service_item_id)
    address = Address.query.filter_by(id=address_id, user_id=user_id).first()
    if not service_item or not address:
        return fail(4002, "服务项目或地址不存在")

    order = Order(
        order_no=f"OD{uuid.uuid4().hex[:12].upper()}",
        user_id=user_id,
        service_item_id=service_item.id,
        address_id=address.id,
        appointment_time=appointment_time,
        note=data.get("note", ""),
    )
    db.session.add(order)
    db.session.flush()

    db.session.add(
        OrderTimeline(
            order_id=order.id,
            actor_user_id=user_id,
            from_status=None,
            to_status="pending",
            remark="用户创建订单",
        )
    )
    db.session.commit()

    return ok({"order_no": order.order_no, "order_id": order.id}, "预约成功")


@order_bp.post("/<int:order_id>/pay")
@jwt_required()
@permission_required("payment:create:self")
@rate_limit("order_pay")
def pay_order(order_id: int):
    user_id = int(get_jwt_identity())
    order = Order.query.filter_by(id=order_id, user_id=user_id).first()
    if not order:
        return fail(4040, "订单不存在", 404)
    if order.payment_status == "paid":
        return fail(4003, "订单已支付")

    amount = order.service_item.price if order.service_item else 0
    txn = f"TXN{uuid.uuid4().hex[:16].upper()}"
    payment = PaymentRecord(
        order_id=order.id,
        user_id=user_id,
        amount=amount,
        method=(request.get_json() or {}).get("method", "mock_alipay"),
        status="paid",
        transaction_no=txn,
    )
    order.payment_status = "paid"
    db.session.add(payment)
    db.session.commit()

    return ok({"transaction_no": txn, "amount": amount}, "支付成功")
