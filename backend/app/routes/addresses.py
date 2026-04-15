from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy import select

from app.models.entities import Address
from app.services.async_db import get_session
from app.services.authz import permission_required
from app.services.response import fail, ok


address_bp = Blueprint("addresses", __name__, url_prefix="/api/addresses")


def _serialize_address(item: Address) -> dict:
    return {
        "id": item.id,
        "contact_name": item.contact_name,
        "contact_phone": item.contact_phone,
        "province": item.province,
        "city": item.city,
        "district": item.district,
        "detail": item.detail,
        "is_default": item.is_default,
    }


@address_bp.get("")
@jwt_required()
@permission_required("address:manage:self")
async def list_addresses():
    user_id = int(get_jwt_identity())

    async with get_session() as session:
        result = await session.execute(
            select(Address)
            .where(Address.user_id == user_id)
            .order_by(Address.id.desc())
        )
        items = result.scalars().all()

    return ok({"items": [_serialize_address(item) for item in items]})


@address_bp.post("")
@jwt_required()
@permission_required("address:manage:self")
async def create_address():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}

    required = ["contact_name", "contact_phone", "province", "city", "district", "detail"]
    if any(not data.get(k) for k in required):
        return fail(4001, "地址信息不完整")

    async with get_session() as session:
        if data.get("is_default"):
            result = await session.execute(
                select(Address).where(Address.user_id == user_id, Address.is_default.is_(True))
            )
            current_default = result.scalars().all()
            for item in current_default:
                item.is_default = False

        item = Address(
            user_id=user_id,
            contact_name=data["contact_name"],
            contact_phone=data["contact_phone"],
            province=data["province"],
            city=data["city"],
            district=data["district"],
            detail=data["detail"],
            is_default=bool(data.get("is_default", False)),
        )
        session.add(item)
        await session.flush()
        address_id = item.id

    return ok({"id": address_id}, "添加成功")


@address_bp.patch("/<int:address_id>")
@jwt_required()
@permission_required("address:manage:self")
async def update_address(address_id: int):
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}

    async with get_session() as session:
        result = await session.execute(
            select(Address).where(Address.id == address_id, Address.user_id == user_id)
        )
        item = result.scalar_one_or_none()
        if not item:
            return fail(4044, "地址不存在", 404)

        for field in ["contact_name", "contact_phone", "province", "city", "district", "detail"]:
            if field in data and str(data[field]).strip():
                setattr(item, field, str(data[field]).strip())

        if "is_default" in data:
            new_default = bool(data["is_default"])
            if new_default:
                result = await session.execute(
                    select(Address).where(Address.user_id == user_id, Address.is_default.is_(True))
                )
                current_default = result.scalars().all()
                for addr in current_default:
                    if addr.id != item.id:
                        addr.is_default = False
            item.is_default = new_default

    return ok({"id": item.id}, "地址更新成功")


@address_bp.delete("/<int:address_id>")
@jwt_required()
@permission_required("address:manage:self")
async def delete_address(address_id: int):
    user_id = int(get_jwt_identity())

    async with get_session() as session:
        result = await session.execute(
            select(Address).where(Address.id == address_id, Address.user_id == user_id)
        )
        item = result.scalar_one_or_none()
        if not item:
            return fail(4044, "地址不存在", 404)

        await session.delete(item)

    return ok({"id": address_id}, "地址删除成功")