from functools import wraps
from flask_jwt_extended import get_jwt_identity
from app.models.entities import User


ROLE_PERMISSIONS = {
    "elderly": {
        "order:create",
        "order:view:self",
        "address:manage:self",
        "feedback:create",
        "payment:create:self",
        "notification:view:self",
    },
    "nurse": {
        "admin:order:list",
        "admin:order:update_status_assigned",
        "notification:view:self",
    },
    "admin": {
        "admin:order:list",
        "admin:order:assign",
        "admin:order:update_status_any",
        "admin:service:crud",
        "admin:user:role:update",
        "notification:send",
    },
}


def get_current_user():
    identity = get_jwt_identity()
    if not identity:
        return None
    return User.query.get(int(identity))


def roles_required(*allowed_roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            user = get_current_user()
            if not user:
                return {"message": "未登录"}, 401
            if user.role not in allowed_roles:
                return {"message": "无权限访问"}, 403
            return fn(*args, **kwargs)

        return wrapper

    return decorator


def permission_required(permission: str):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            user = get_current_user()
            if not user:
                return {"code": 4010, "message": "未登录", "data": {}}, 401
            perms = ROLE_PERMISSIONS.get(user.role, set())
            if permission not in perms:
                return {"code": 4031, "message": f"缺少权限: {permission}", "data": {}}, 403
            return fn(*args, **kwargs)

        return wrapper

    return decorator
