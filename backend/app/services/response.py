def ok(data=None, message="success"):
    return {"code": 0, "message": message, "data": data or {}}


def fail(code=4000, message="error", http_status=400, extra=None):
    payload = {"code": code, "message": message, "data": extra or {}}
    return payload, http_status
