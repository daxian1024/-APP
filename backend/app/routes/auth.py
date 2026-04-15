from sqlalchemy import or_, select
from flask import Blueprint, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required,
)
from app.models.entities import User
from app.services.async_db import get_session
from app.services.authz import permission_required, ROLE_PERMISSIONS
from app.services.response import ok, fail
from app.services.security import rate_limit, verify_signature


auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.post("/register")
@rate_limit("auth_register")
async def register():
    data = request.get_json() or {}
    username = data.get("username", "").strip()
    phone = data.get("phone", "").strip()
    password = data.get("password", "")
    role = data.get("role", "elderly").strip()

    if role not in ["elderly", "nurse", "admin"]:
        return fail(4007, "角色不合法")

    if not username or not phone or len(password) < 6:
        return fail(4001, "参数不合法")

    async with get_session() as session:
        stmt = select(User).where(or_(User.username == username, User.phone == phone))
        result = await session.execute(stmt)
        exists = result.scalar_one_or_none()
        if exists:
            return fail(4008, "用户名或手机号已存在")

        user = User(username=username, phone=phone, role=role)
        user.set_password(password)
        session.add(user)
        await session.flush()
        user_id = user.id

    return ok({"id": user_id}, "注册成功")


@auth_bp.post("/login")
@rate_limit("auth_login")
async def login():
    data = request.get_json() or {}
    account = data.get("account", "").strip()
    password = data.get("password", "")

    async with get_session() as session:
        stmt = select(User).where(or_(User.username == account, User.phone == account))
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()

    if not user or not user.check_password(password):
        return fail(4011, "账号或密码错误", 401)

    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))
    return ok(
        {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": {
                "id": user.id,
                "username": user.username,
                "phone": user.phone,
                "role": user.role,
            },
            "permissions": sorted(list(ROLE_PERMISSIONS.get(user.role, set()))),
        }
    )


@auth_bp.post("/refresh")
@jwt_required(refresh=True)
def refresh_access_token():
    user_id = str(get_jwt_identity())
    new_access = create_access_token(identity=user_id)
    return ok({"access_token": new_access}, "刷新成功")


@auth_bp.get("/me")
@jwt_required()
async def me():
    user_id = int(get_jwt_identity())
    async with get_session() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

    if not user:
        return fail(4043, "用户不存在", 404)
    return ok({"id": user.id, "username": user.username, "phone": user.phone, "role": user.role})


@auth_bp.patch("/me")
@jwt_required()
async def update_me():
    user_id = int(get_jwt_identity())

    data = request.get_json() or {}
    username = (data.get("username") or "").strip()

    async with get_session() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            return fail(4043, "用户不存在", 404)

        if username:
            exists_result = await session.execute(select(User).where(User.username == username, User.id != user.id))
            exists = exists_result.scalar_one_or_none()
            if exists:
                return fail(4008, "用户名已存在")
            user.username = username

    return ok({"id": user.id, "username": user.username, "phone": user.phone, "role": user.role}, "资料更新成功")


@auth_bp.patch("/users/<int:user_id>/role")
@jwt_required()
@permission_required("admin:user:role:update")
@verify_signature()
async def update_user_role(user_id: int):
    data = request.get_json() or {}
    role = data.get("role", "").strip()
    if role not in ["elderly", "nurse", "admin"]:
        return fail(4007, "角色不合法")

    async with get_session() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            return fail(4043, "用户不存在", 404)

        user.role = role

    return ok({"id": user.id, "role": user.role}, "角色更新成功")
