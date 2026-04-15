from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.extensions import db
from app.models.entities import Address
from app.services.authz import permission_required
from app.services.response import ok, fail


address_bp = Blueprint("addresses", __name__, url_prefix="/api/addresses")


@address_bp.get("")
@jwt_required()
@permission_required("address:manage:self")
def list_addresses():
    user_id = int(get_jwt_identity())
    data = Address.query.filter_by(user_id=user_id).order_by(Address.id.desc()).all()
    return ok(
        {
            "items": [
                {
                    "id": item.id,
                    "contact_name": item.contact_name,
                    "contact_phone": item.contact_phone,
                    "province": item.province,
                    "city": item.city,
                    "district": item.district,
                    "detail": item.detail,
                    "is_default": item.is_default,
                }
                for item in data
            ]
        }
    )


@address_bp.post("")
@jwt_required()
@permission_required("address:manage:self")
def create_address():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}

    required = ["contact_name", "contact_phone", "province", "city", "district", "detail"]
    if any(not data.get(k) for k in required):
        return fail(4001, "地址信息不完整")

    if data.get("is_default"):
        Address.query.filter_by(user_id=user_id, is_default=True).update({"is_default": False})

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
    db.session.add(item)
    db.session.commit()
    return ok({"id": item.id}, "添加成功")


@address_bp.patch("/<int:address_id>")
@jwt_required()
@permission_required("address:manage:self")
def update_address(address_id: int):
    user_id = int(get_jwt_identity())
    item = Address.query.filter_by(id=address_id, user_id=user_id).first()
    if not item:
        return fail(4044, "地址不存在", 404)

    data = request.get_json() or {}
    for field in ["contact_name", "contact_phone", "province", "city", "district", "detail"]:
        if field in data and str(data[field]).strip():
            setattr(item, field, str(data[field]).strip())

    if "is_default" in data:
        new_default = bool(data["is_default"])
        if new_default:
            Address.query.filter_by(user_id=user_id, is_default=True).update({"is_default": False})
        item.is_default = new_default

    db.session.commit()
    return ok({"id": item.id}, "地址更新成功")


@address_bp.delete("/<int:address_id>")
@jwt_required()
@permission_required("address:manage:self")
def delete_address(address_id: int):
    user_id = int(get_jwt_identity())
    item = Address.query.filter_by(id=address_id, user_id=user_id).first()
    if not item:
        return fail(4044, "地址不存在", 404)

    db.session.delete(item)
    db.session.commit()
    return ok({"id": address_id}, "地址删除成功")
