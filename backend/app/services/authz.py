import functools

from flask import request
from flask_jwt_extended import get_jwt_identity
from sqlalchemy import select

from app.models.entities import User
from app.services.async_db import get_session
from app.services.response import fail
from app.services.security import verify_api_signature


ROLE_PERMISSIONS = {
    "elderly": {
        "address:manage:self",
        "order:create",
        "order:view:self",
        "payment:create:self",
        "feedback:create",
        "notification:view:self",
    },
    "nurse": {
        "order:view:self",
        "admin:order:update_status_assigned",
        "notification:view:self",
    },
    "admin": {
        "admin:service:crud",
        "admin:user:role:update",
        "admin:order:list",
        "admin:order:assign",
        "admin:order:update_status_any",
        "notification:send",
        "notification:view:self",
        "address:manage:self",
        "order:create",
        "order:view:self",
        "payment:create:self",
        "feedback:create",
    },
}


async def get_current_user():
    identity = get_jwt_identity()
    if not identity:
        return None

    async with get_session() as session:
        result = await session.execute(select(User).where(User.id == int(identity)))
        return result.scalar_one_or_none()


def permission_required(permission: str):
    def decorator(fn):
        @functools.wraps(fn)
        async def wrapper(*args, **kwargs):
            user = await get_current_user()
            if not user:
                return fail(4010, "未登录", 401)

            perms = ROLE_PERMISSIONS.get(user.role, set())
            if permission not in perms:
                return fail(4031, "无权限访问", 403)

            return await fn(*args, **kwargs)

        return wrapper

    return decorator


def verify_signature():
    def decorator(fn):
        @functools.wraps(fn)
        async def wrapper(*args, **kwargs):
            ok, message = verify_api_signature(
                request.method,
                request.path,
                request.headers,
                request.get_data(as_text=True),
            )
            if not ok:
                return fail(4012, message, 401)
            return await fn(*args, **kwargs)

        return wrapper

    return decorator