import json

from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from sqlalchemy import select

from app.models.entities import ServiceItem
from app.services.async_db import get_session
from app.services.authz import permission_required
from app.services.redis_client import get_redis_client
from app.services.response import fail, ok
from app.services.security import verify_signature


service_bp = Blueprint("services", __name__, url_prefix="/api/services")


def _serialize_service(item: ServiceItem) -> dict:
    return {
        "id": item.id,
        "name": item.name,
        "description": item.description,
        "price": item.price,
        "duration_minutes": item.duration_minutes,
        "is_active": item.is_active,
    }


@service_bp.get("")
async def list_services():
    async with get_session() as session:
        result = await session.execute(
            select(ServiceItem)
            .where(ServiceItem.is_active.is_(True))
            .order_by(ServiceItem.id.desc())
        )
        items = result.scalars().all()

    return ok({"items": [_serialize_service(item) for item in items]})


@service_bp.get("/popular")
async def popular_services():
    cache_key = "services:popular"
    client = None

    try:
        client = get_redis_client()
        cached = client.get(cache_key)
        if cached:
            if isinstance(cached, bytes):
                cached = cached.decode("utf-8")
            return ok({"source": "redis", "items": json.loads(cached)})
    except Exception:
        client = None

    async with get_session() as session:
        result = await session.execute(
            select(ServiceItem)
            .where(ServiceItem.is_active.is_(True))
            .order_by(ServiceItem.price.desc(), ServiceItem.id.desc())
            .limit(6)
        )
        top_items = result.scalars().all()

    payload = [_serialize_service(item) for item in top_items]

    if client:
        try:
            client.set(cache_key, json.dumps(payload, ensure_ascii=False), ex=180)
        except Exception:
            pass

    return ok({"source": "db", "items": payload})


@service_bp.post("")
@jwt_required()
@permission_required("admin:service:crud")
@verify_signature()
async def create_service():
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

    async with get_session() as session:
        session.add(item)
        await session.flush()
        service_id = item.id

    return ok({"id": service_id}, "服务项目创建成功")


@service_bp.patch("/<int:service_id>")
@jwt_required()
@permission_required("admin:service:crud")
@verify_signature()
async def update_service(service_id: int):
    data = request.get_json() or {}

    async with get_session() as session:
        result = await session.execute(select(ServiceItem).where(ServiceItem.id == service_id))
        item = result.scalar_one_or_none()

        if not item:
            return fail(4041, "服务项目不存在", 404)

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

    return ok({"id": item.id}, "服务项目更新成功")


@service_bp.delete("/<int:service_id>")
@jwt_required()
@permission_required("admin:service:crud")
@verify_signature()
async def delete_service(service_id: int):
    async with get_session() as session:
        result = await session.execute(select(ServiceItem).where(ServiceItem.id == service_id))
        item = result.scalar_one_or_none()

        if not item:
            return fail(4041, "服务项目不存在", 404)

        await session.delete(item)

    return ok({"id": service_id}, "服务项目删除成功")