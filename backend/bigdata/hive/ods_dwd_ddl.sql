-- ODS 层（原始订单数据）
CREATE EXTERNAL TABLE IF NOT EXISTS ods_orders (
  id BIGINT,
  order_no STRING,
  user_id BIGINT,
  service_item_id BIGINT,
  status STRING,
  appointment_time STRING,
  created_at STRING
)
ROW FORMAT DELIMITED FIELDS TERMINATED BY ','
STORED AS TEXTFILE;

-- DWD 层（清洗后明细）
CREATE TABLE IF NOT EXISTS dwd_orders_detail (
  id BIGINT,
  order_no STRING,
  user_id BIGINT,
  service_item_id BIGINT,
  status STRING,
  appointment_time TIMESTAMP,
  created_at TIMESTAMP
)
STORED AS PARQUET;

INSERT OVERWRITE TABLE dwd_orders_detail
SELECT
  id,
  order_no,
  user_id,
  service_item_id,
  status,
  CAST(appointment_time AS TIMESTAMP),
  CAST(created_at AS TIMESTAMP)
FROM ods_orders;
