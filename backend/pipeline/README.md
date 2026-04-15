# 实时数据管道（骨架）

目标链路：MySQL -> Kafka -> Flink -> Hive/ClickHouse

## 目录说明
- `mysql_to_kafka.py`：演示版增量抽取（轮询）
- `flink/kafka_to_hive.sql`：Flink SQL 消费 Kafka 写入 Hive
- `clickhouse/dws_ddl.sql`：ClickHouse DWS 指标表

## 生产建议
1. MySQL CDC 建议换成 Debezium + Kafka Connect。
2. Flink 增加 watermark、状态后端、checkpoint、exactly-once。
3. Hive/ClickHouse 分层（ODS/DWD/DWS）并建立任务编排（Airflow）。
