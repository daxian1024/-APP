-- Kafka -> Flink -> Hive 示例 SQL（需在 Flink SQL Client 中执行）
CREATE TABLE kafka_orders (
  id BIGINT,
  order_no STRING,
  user_id BIGINT,
  service_item_id BIGINT,
  status STRING,
  created_at STRING
) WITH (
  'connector' = 'kafka',
  'topic' = 'smart_nursing_orders',
  'properties.bootstrap.servers' = '127.0.0.1:9092',
  'properties.group.id' = 'smart-nursing-flink',
  'scan.startup.mode' = 'earliest-offset',
  'format' = 'json'
);

CREATE TABLE hive_dwd_orders (
  id BIGINT,
  order_no STRING,
  user_id BIGINT,
  service_item_id BIGINT,
  status STRING,
  created_at STRING
) WITH (
  'connector' = 'hive',
  'table-name' = 'dwd_orders_detail',
  'database-name' = 'smart_nursing'
);

INSERT INTO hive_dwd_orders
SELECT id, order_no, user_id, service_item_id, status, created_at
FROM kafka_orders;
