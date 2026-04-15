"""
Flink 实时告警示例（伪代码骨架）
场景：单位时间内投诉量激增触发告警
"""

# 实际部署时请替换为 pyflink DataStream API 实现


def process_stream(complaint_events):
    window_size_minutes = 10
    threshold = 20

    # 这里用伪逻辑表示窗口统计
    count_in_window = len(complaint_events)
    if count_in_window >= threshold:
        print(
            {
                "type": "complaint_spike_alert",
                "window_minutes": window_size_minutes,
                "count": count_in_window,
                "level": "high",
            }
        )


if __name__ == "__main__":
    fake_events = [{"id": i} for i in range(23)]
    process_stream(fake_events)
