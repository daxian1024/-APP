import hashlib
import hmac
import json
import time
from functools import wraps
from flask import current_app, request
from app.services.response import fail
from app.services.redis_client import get_redis_client


def _client_ip():
    return request.headers.get("X-Forwarded-For", request.remote_addr or "unknown")


def rate_limit(key_prefix: str):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                redis_client = get_redis_client()
                window = current_app.config["RATE_LIMIT_WINDOW_SEC"]
                max_req = current_app.config["RATE_LIMIT_MAX_REQUESTS"]
                key = f"rl:{key_prefix}:{_client_ip()}:{int(time.time() // window)}"
                count = redis_client.incr(key)
                if count == 1:
                    redis_client.expire(key, window)
                if count > max_req:
                    return fail(4290, "请求过于频繁，请稍后再试", 429)
            except Exception:
                pass
            return fn(*args, **kwargs)

        return wrapper

    return decorator


def verify_signature(required_for_methods=None):
    required_for_methods = required_for_methods or {"POST", "PATCH", "PUT", "DELETE"}

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if request.method.upper() not in required_for_methods:
                return fn(*args, **kwargs)

            ts = request.headers.get("X-Timestamp", "")
            sign = request.headers.get("X-Signature", "")
            if not ts or not sign:
                return fail(4012, "缺少签名头", 401)

            try:
                ts_int = int(ts)
            except ValueError:
                return fail(4013, "时间戳格式错误", 401)

            if abs(int(time.time()) - ts_int) > 300:
                return fail(4014, "签名已过期", 401)

            body = request.get_json(silent=True) or {}
            canonical = f"{request.method}\n{request.path}\n{ts}\n{json.dumps(body, sort_keys=True, ensure_ascii=False)}"
            secret = current_app.config["API_SIGN_SECRET"].encode("utf-8")
            expected = hmac.new(secret, canonical.encode("utf-8"), hashlib.sha256).hexdigest()
            if not hmac.compare_digest(expected, sign):
                return fail(4015, "签名校验失败", 401)

            return fn(*args, **kwargs)

        return wrapper

    return decorator
