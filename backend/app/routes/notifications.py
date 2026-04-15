from flask import Blueprint
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy import select

from app.models.entities import Notification
from app.services.async_db import get_session
from app.services.authz import permission_required
from app.services.response import ok


notification_bp = Blueprint("notifications", __name__, url_prefix="/api/notifications")


@notification_bp.get("")
@jwt_required()
@permission_required("notification:view:self")
async def list_notifications():
    user_id = int(get_jwt_identity())

    async with get_session() as session:
        result = await session.execute(
            select(Notification)
            .where(Notification.user_id == user_id)
            .order_by(Notification.id.desc())
            .limit(50)
        )
        rows = result.scalars().all()

    return ok(
        {
            "items": [
                {
                    "id": item.id,
                    "title": item.title,
                    "content": item.content,
                    "channel": item.channel,
                    "sent": item.sent,
                    "created_at": item.created_at.isoformat(),
                }
                for item in rows
            ]
        }
    )