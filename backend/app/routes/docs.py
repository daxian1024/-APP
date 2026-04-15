from flask import Blueprint, jsonify, Response


docs_bp = Blueprint("docs", __name__, url_prefix="/api/docs")


@docs_bp.get("/openapi.json")
def openapi_spec():
    spec = {
        "openapi": "3.0.3",
        "info": {
            "title": "智慧护理平台 API",
            "version": "1.0.0",
            "description": "包含用户、订单、管理端、评价投诉与缓存示例接口",
        },
        "servers": [{"url": "http://127.0.0.1:5000"}],
        "paths": {
            "/api/auth/register": {"post": {"summary": "用户注册"}},
            "/api/auth/login": {"post": {"summary": "用户登录"}},
            "/api/services": {"get": {"summary": "服务项目列表"}},
            "/api/services/popular": {"get": {"summary": "热门服务（Redis缓存）"}},
            "/api/orders": {"get": {"summary": "我的订单"}, "post": {"summary": "创建订单"}},
            "/api/admin/orders": {"get": {"summary": "管理端订单列表"}},
            "/api/admin/orders/{order_id}/assign": {"patch": {"summary": "管理员分配护士"}},
            "/api/admin/orders/{order_id}/status": {"patch": {"summary": "订单状态流转"}},
        },
    }
    return jsonify(spec)


@docs_bp.get("")
def swagger_ui():
    html = """
<!doctype html>
<html>
  <head>
    <meta charset=\"utf-8\" />
    <title>Smart Nursing API Docs</title>
    <link rel=\"stylesheet\" href=\"https://unpkg.com/swagger-ui-dist@5/swagger-ui.css\" />
  </head>
  <body>
    <div id=\"swagger-ui\"></div>
    <script src=\"https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js\"></script>
    <script>
      window.ui = SwaggerUIBundle({
        url: '/api/docs/openapi.json',
        dom_id: '#swagger-ui'
      });
    </script>
  </body>
</html>
"""
    return Response(html, mimetype="text/html")
