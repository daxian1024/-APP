-- ClickHouse DWS 层示例：订单主题宽表
CREATE TABLE IF NOT EXISTS dws_order_metrics
(
  dt Date,
  service_item_id UInt64,
  total_orders UInt64,
  completed_orders UInt64,
  paid_orders UInt64
)
ENGINE = MergeTree
ORDER BY (dt, service_item_id);
