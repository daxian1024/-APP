# 实时数据管道说明

本目录用于承载项目的实时数据采集、处理与分析链路，整体目标是将业务系统中的 MySQL 数据实时同步到消息队列，再通过 Flink 进行流式加工，最终落地到 Hive 或 ClickHouse 供离线分析和报表查询使用。

## 数据链路

当前规划的数据链路如下：

```text
MySQL -> Kafka -> Flink -> Hive / ClickHouse
```

## 目录结构

- `mysql_to_kafka.py`
  - 演示版增量抽取脚本
  - 当前采用轮询方式模拟 MySQL 到 Kafka 的数据同步
- `flink/kafka_to_hive.sql`
  - Flink SQL 作业示例
  - 用于消费 Kafka 中的数据并写入 Hive
- `clickhouse/dws_ddl.sql`
  - ClickHouse 数仓 DWS 层建表脚本
  - 用于存放聚合后的分析指标表

## 使用说明

### 1. 数据采集

如果你需要演示 MySQL 到 Kafka 的同步流程，可以参考 `mysql_to_kafka.py` 的实现方式。

### 2. 流式处理

使用 `flink/kafka_to_hive.sql` 作为 Flink SQL 作业示例，完成 Kafka 数据消费与 Hive 写入。

### 3. 数仓建模

使用 `clickhouse/dws_ddl.sql` 创建 ClickHouse DWS 层指标表，为后续分析和可视化提供数据支撑。

## 生产环境建议

当前实现更偏向于教学演示或项目骨架，生产环境建议进一步完善以下能力：

1. 使用 Debezium + Kafka Connect 替代轮询抽取，实现真正的 MySQL CDC。
2. 在 Flink 作业中补充 watermark、状态后端、checkpoint、容错重启策略，并尽量保证 exactly-once 语义。
3. 按照 ODS / DWD / DWS 分层建设 Hive 或 ClickHouse 数仓。
4. 配套任务编排与调度系统，例如 Airflow、DolphinScheduler 或类似方案。
5. 增加监控、告警与日志采集能力，便于排查链路异常。

## 后续扩展方向

- 增加 Kafka Topic 管理与消息格式规范
- 补充 Flink 作业部署文档
- 增加 Hive/ClickHouse 数据验证脚本
- 对接统一的数据治理与权限控制
