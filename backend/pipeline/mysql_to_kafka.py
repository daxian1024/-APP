"""
MySQL -> Kafka CDC 示例骨架
生产环境建议使用 Debezium + Kafka Connect；此文件提供 Python 轮询版演示。
"""

import json
import time
from sqlalchemy import create_engine, text
from kafka import KafkaProducer


DB_URL = "mysql+pymysql://root:123456@127.0.0.1:3306/smart_nursing?charset=utf8mb4"
KAFKA_BOOTSTRAP = "127.0.0.1:9092"
TOPIC = "smart_nursing_orders"


def main():
    engine = create_engine(DB_URL)
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP,
        value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode("utf-8"),
    )

    last_id = 0
    while True:
        with engine.connect() as conn:
            rows = conn.execute(
                text(
                    "SELECT id, order_no, user_id, service_item_id, status, created_at "
                    "FROM orders WHERE id > :last_id ORDER BY id ASC LIMIT 200"
                ),
                {"last_id": last_id},
            ).mappings().all()

            for r in rows:
                payload = dict(r)
                payload["created_at"] = str(payload.get("created_at"))
                producer.send(TOPIC, payload)
                last_id = max(last_id, payload["id"])

            producer.flush()

        time.sleep(3)


if __name__ == "__main__":
    main()
