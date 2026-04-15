from app import create_app
from app.extensions import db
from app.models.entities import ServiceItem

app = create_app()

services = [
    {"name": "基础生命体征监测", "description": "上门测量血压、血糖、体温并记录", "price": 69.0, "duration_minutes": 30},
    {"name": "压疮护理", "description": "压疮风险评估、换药与健康宣教", "price": 199.0, "duration_minutes": 60},
    {"name": "导尿管护理", "description": "导尿管更换及感染预防指导", "price": 229.0, "duration_minutes": 60},
    {"name": "康复训练指导", "description": "术后/慢病康复动作训练与家属指导", "price": 159.0, "duration_minutes": 45},
]


with app.app_context():
    db.create_all()
    if ServiceItem.query.count() == 0:
        for item in services:
            db.session.add(ServiceItem(**item))
        db.session.commit()
        print("已初始化服务项目数据")
    else:
        print("服务项目已存在，跳过初始化")
