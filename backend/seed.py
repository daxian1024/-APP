import asyncio

from sqlalchemy import select

from app import create_app
from app.extensions import Base, async_engine
from app.models.entities import ServiceItem
from app.services.async_db import get_session

app = create_app()

services = [
    {"name": "基础生命体征监测", "description": "上门测量血压、血糖、体温并记录", "price": 69.0, "duration_minutes": 30},
    {"name": "压疮护理", "description": "压疮风险评估、换药与健康宣教", "price": 199.0, "duration_minutes": 60},
    {"name": "导尿管护理", "description": "导尿管更换及感染预防指导", "price": 229.0, "duration_minutes": 60},
    {"name": "康复训练指导", "description": "术后/慢病康复动作训练与家属指导", "price": 159.0, "duration_minutes": 45},
]


async def main():
    if async_engine is None:
        raise RuntimeError("Async engine has not been initialized")

    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with get_session() as session:
        result = await session.execute(select(ServiceItem.id))
        has_service = result.first() is not None
        if not has_service:
            session.add_all(ServiceItem(**item) for item in services)
            print("已初始化服务项目数据")
        else:
            print("服务项目已存在，跳过初始化")


if __name__ == "__main__":
    asyncio.run(main())
