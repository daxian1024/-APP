from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db
from app.models.base import TimestampMixin


class User(TimestampMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default="elderly", nullable=False)  # elderly / nurse / admin

    addresses = db.relationship("Address", backref="user", lazy=True, cascade="all,delete")
    orders = db.relationship(
        "Order",
        foreign_keys="Order.user_id",
        backref="user",
        lazy=True,
        cascade="all,delete",
    )

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str):
        return check_password_hash(self.password_hash, password)


class ServiceItem(TimestampMixin, db.Model):
    __tablename__ = "service_items"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False, default=30)
    is_active = db.Column(db.Boolean, default=True, nullable=False)


class Address(TimestampMixin, db.Model):
    __tablename__ = "addresses"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    contact_name = db.Column(db.String(80), nullable=False)
    contact_phone = db.Column(db.String(20), nullable=False)
    province = db.Column(db.String(50), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    district = db.Column(db.String(50), nullable=False)
    detail = db.Column(db.String(255), nullable=False)
    is_default = db.Column(db.Boolean, default=False, nullable=False)


class Order(TimestampMixin, db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    order_no = db.Column(db.String(50), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    service_item_id = db.Column(db.Integer, db.ForeignKey("service_items.id"), nullable=False)
    address_id = db.Column(db.Integer, db.ForeignKey("addresses.id"), nullable=False)
    appointment_time = db.Column(db.String(40), nullable=False)
    status = db.Column(db.String(20), default="pending", nullable=False)  # pending/accepted/in_service/completed
    note = db.Column(db.String(255), nullable=True)
    assigned_nurse_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    payment_status = db.Column(db.String(20), default="unpaid", nullable=False)  # unpaid/paid/refunded

    service_item = db.relationship("ServiceItem", backref="orders")
    address = db.relationship("Address", backref="orders")
    assigned_nurse = db.relationship("User", foreign_keys=[assigned_nurse_id], backref="assigned_orders")


class OrderTimeline(TimestampMixin, db.Model):
    __tablename__ = "order_timeline"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    actor_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    from_status = db.Column(db.String(20), nullable=True)
    to_status = db.Column(db.String(20), nullable=False)
    remark = db.Column(db.String(255), nullable=True)

    order = db.relationship("Order", backref="timeline")


class Review(TimestampMixin, db.Model):
    __tablename__ = "reviews"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=True)


class Complaint(TimestampMixin, db.Model):
    __tablename__ = "complaints"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    content = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default="submitted", nullable=False)


class Notification(TimestampMixin, db.Model):
    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    channel = db.Column(db.String(20), nullable=False, default="in_app")  # in_app/sms/wechat
    title = db.Column(db.String(120), nullable=False)
    content = db.Column(db.String(500), nullable=False)
    sent = db.Column(db.Boolean, default=False, nullable=False)


class PaymentRecord(TimestampMixin, db.Model):
    __tablename__ = "payment_records"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    method = db.Column(db.String(30), nullable=False, default="mock_alipay")
    status = db.Column(db.String(20), nullable=False, default="paid")
    transaction_no = db.Column(db.String(80), unique=True, nullable=False)


class AuditLog(TimestampMixin, db.Model):
    __tablename__ = "audit_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=True)
    action = db.Column(db.String(120), nullable=False)
    method = db.Column(db.String(10), nullable=False)
    path = db.Column(db.String(255), nullable=False)
    ip = db.Column(db.String(64), nullable=True)
    request_id = db.Column(db.String(64), nullable=True)
    details = db.Column(db.Text, nullable=True)
