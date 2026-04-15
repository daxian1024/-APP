import uuid
from pathlib import Path
from flask import Flask, request, send_from_directory
from flask_cors import CORS
from app.config import Config
from app.extensions import db, migrate, jwt
from app.routes.auth import auth_bp
from app.routes.services import service_bp
from app.routes.addresses import address_bp
from app.routes.orders import order_bp
from app.routes.feedback import feedback_bp
from app.routes.admin import admin_bp
from app.routes.docs import docs_bp
from app.routes.analytics import analytics_bp
from app.routes.notifications import notification_bp
from app.models.entities import AuditLog


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # 开发阶段允许前端 5173 跨域
    CORS(app, resources={r"/api/*": {"origins": ["http://127.0.0.1:5174", "http://localhost:5174"]}})

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(service_bp)
    app.register_blueprint(address_bp)
    app.register_blueprint(order_bp)
    app.register_blueprint(feedback_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(docs_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(notification_bp)

    @app.before_request
    def inject_request_id():
        request.request_id = request.headers.get("X-Request-Id", uuid.uuid4().hex[:16])

    @app.after_request
    def write_audit_log(response):
        if request.path.startswith("/api"):
            try:
                uid = None
                auth = request.headers.get("Authorization", "")
                if auth.startswith("Bearer "):
                    uid = None
                log = AuditLog(
                    user_id=uid,
                    action="api_call",
                    method=request.method,
                    path=request.path,
                    ip=request.headers.get("X-Forwarded-For", request.remote_addr),
                    request_id=getattr(request, "request_id", None),
                    details=f"status={response.status_code}",
                )
                db.session.add(log)
                db.session.commit()
            except Exception:
                db.session.rollback()
        response.headers["X-Request-Id"] = getattr(request, "request_id", "")
        return response

    @app.errorhandler(404)
    def not_found(_e):
        if request.path.startswith("/api"):
            return {"code": 4040, "message": "资源不存在", "data": {}}, 404
        # 前端路由 fallback 到 index.html
        return serve_spa()

    @app.errorhandler(500)
    def server_error(_e):
        return {"code": 5000, "message": "服务器内部错误", "data": {}}, 500

    dist_dir = Path(app.root_path).parent / "static" / "frontend"

    def serve_spa():
        index_file = dist_dir / "index.html"
        if index_file.exists():
            return send_from_directory(dist_dir, "index.html")
        return {
            "code": 5001,
            "message": "前端静态资源未构建，请先在 frontend-vue 执行 npm run build",
            "data": {},
        }, 500

    @app.get("/api/health")
    def health_check():
        return {"code": 0, "message": "ok", "data": {}}

    # 先尝试返回打包后的静态文件
    @app.get("/")
    def root():
        return serve_spa()

    @app.get("/<path:path>")
    def spa_assets(path: str):
        if path.startswith("api/"):
            return {"code": 4040, "message": "资源不存在", "data": {}}, 404

        file_path = dist_dir / path
        if file_path.exists() and file_path.is_file():
            return send_from_directory(dist_dir, path)

        return serve_spa()

    return app
