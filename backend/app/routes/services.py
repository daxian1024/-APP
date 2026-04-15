import json
from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from app.extensions import db
from app.models.entities import ServiceItem
from app.services.redis_client import get_redis_client
from app.services.authz import permission_required
from app.services.response import ok, fail
from app.services.security import verify_signature


service_bp = Blueprint("services", __name__, url_prefix="/api/services")


@service_bp.get("")
def list_services():
    items = ServiceItem.query.filter_by(is_active=True).order_by(ServiceItem.id.desc()).all()
    return ok(
        {
            "items": [
                {
                    "id": item.id,
                    "name": item.name,
                    "description": item.description,
                    "price": item.price,
                    "duration_minutes": item.duration_minutes,
                    "is_active": item.is_active,
                }
                for item in items
            ]
        }
    )


@service_bp.get("/popular")
def popular_services():
    cache_key = "services:popular"
    try:
        client = get_redis_client()
        cached = client.get(cache_key)
        if cached:
            return ok({"source": "redis", "items": json.loads(cached)})
    except Exception:
        client = None

    top_items = (
        ServiceItem.query.filter_by(is_active=True)
        .order_by(ServiceItem.price.desc(), ServiceItem.id.desc())
        .limit(6)
        .all()
    )
    payload = [
        {
            "id": item.id,
            "name": item.name,
            "description": item.description,
            "price": item.price,
            "duration_minutes": item.duration_minutes,
            "is_active": item.is_active,
        }
        for item in top_items
    ]

    if client:
        client.set(cache_key, json.dumps(payload, ensure_ascii=False), ex=180)

    return ok({"source": "db", "items": payload})


@service_bp.post("")
@jwt_required()
@permission_required("admin:service:crud")
@verify_signature()
def create_service():
    data = request.get_json() or {}
    name = data.get("name", "").strip()
    price = data.get("price")
    if not name or price is None:
        return fail(4001, "name 和 price 必填")

    item = ServiceItem(
        name=name,
        description=data.get("description", "").strip(),
        price=float(price),
        duration_minutes=int(data.get("duration_minutes", 30)),
        is_active=bool(data.get("is_active", True)),
    )
    db.session.add(item)
    db.session.commit()
    return ok({"id": item.id}, "服务项目创建成功")


@service_bp.patch("/<int:service_id>")
@jwt_required()
@permission_required("admin:service:crud")
@verify_signature()
def update_service(service_id: int):
    item = ServiceItem.query.get(service_id)
    if not item:
        return fail(4041, "服务项目不存在", 404)

    data = request.get_json() or {}
    if "name" in data:
        item.name = data["name"].strip()
    if "description" in data:
        item.description = (data["description"] or "").strip()
    if "price" in data:
        item.price = float(data["price"])
    if "duration_minutes" in data:
        item.duration_minutes = int(data["duration_minutes"])
    if "is_active" in data:
        item.is_active = bool(data["is_active"])

    db.session.commit()
    return ok({"id": item.id}, "服务项目更新成功")


@service_bp.delete("/<int:service_id>")
@jwt_required()
@permission_required("admin:service:crud")
@verify_signature()
def delete_service(service_id: int):
    item = ServiceItem.query.get(service_id)
    if not item:
        return fail(4041, "服务项目不存在", 404)

    db.session.delete(item)
    db.session.commit()
    return ok({"id": service_id}, "服务项目删除成功")
