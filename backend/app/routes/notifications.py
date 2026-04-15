from flask import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.entities import Notification
from app.services.authz import permission_required
from app.services.response import ok


notification_bp = Blueprint("notifications", __name__, url_prefix="/api/notifications")


@notification_bp.get("")
@jwt_required()
@permission_required("notification:view:self")
def my_notifications():
    user_id = int(get_jwt_identity())
    rows = Notification.query.filter_by(user_id=user_id).order_by(Notification.id.desc()).limit(50).all()
    return ok(
        {
            "items": [
                {
                    "id": r.id,
                    "channel": r.channel,
                    "title": r.title,
                    "content": r.content,
                    "sent": r.sent,
                    "created_at": r.created_at.isoformat(),
                }
                for r in rows
            ]
        }
    )
