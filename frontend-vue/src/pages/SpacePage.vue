<template>
  <div class="dashboard-page">
    <header class="dashboard-header">
      <div>
        <h1>数据可视化看板</h1>
        <p>护理平台运营数据总览、趋势分析与分布统计</p>
      </div>

      <button class="refresh-btn" @click="loadAll" :disabled="loading">
        {{ loading ? '加载中...' : '刷新数据' }}
      </button>
    </header>

    <section class="kpi-grid">
      <div class="kpi-card">
        <div class="kpi-label">订单总数</div>
        <div class="kpi-value">{{ overview.total_orders }}</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">已完成订单</div>
        <div class="kpi-value">{{ overview.completed_orders }}</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">待处理订单</div>
        <div class="kpi-value">{{ overview.pending_orders }}</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">完成率</div>
        <div class="kpi-value">{{ formatPercent(overview.completion_rate) }}</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">平均评分</div>
        <div class="kpi-value">{{ overview.avg_rating }}</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">投诉数量</div>
        <div class="kpi-value">{{ overview.complaint_count }}</div>
      </div>
    </section>

    <section class="chart-grid">
      <div class="chart-card chart-large">
        <div class="chart-header">
          <h2>订单趋势</h2>
          <span>最近 {{ trendDays }} 天</span>
        </div>
        <div ref="trendChartRef" class="chart-box"></div>
      </div>

      <div class="chart-card">
        <div class="chart-header">
          <h2>服务项目分布</h2>
          <span>订单占比</span>
        </div>
        <div ref="serviceChartRef" class="chart-box"></div>
      </div>

      <div class="chart-card">
        <div class="chart-header">
          <h2>订单状态分布</h2>
          <span>状态占比</span>
        </div>
        <div ref="statusChartRef" class="chart-box"></div>
      </div>

      <div class="chart-card chart-large">
        <div class="chart-header">
          <h2>护士接单排行榜</h2>
          <span>按接单数排序</span>
        </div>

        <div class="rank-list">
          <div v-if="nurseRanking.items.length === 0" class="empty-state">
            暂无护士接单数据
          </div>

          <div v-for="(item, index) in nurseRanking.items" :key="item.nurse_id" class="rank-item">
            <div class="rank-left">
              <span class="rank-index">{{ index + 1 }}</span>
              <div>
                <div class="rank-name">{{ item.nurse_name }}</div>
                <div class="rank-sub">护士 ID：{{ item.nurse_id }}</div>
              </div>
            </div>
            <div class="rank-value">{{ item.count }} 单</div>
          </div>
        </div>
      </div>

      <div class="chart-card chart-large">
        <div class="chart-header">
          <h2>投诉趋势</h2>
          <span>最近 {{ trendDays }} 天</span>
        </div>
        <div ref="complaintTrendChartRef" class="chart-box"></div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { onBeforeUnmount, onMounted, nextTick, ref } from 'vue'
import * as echarts from 'echarts'
import { analyticsApi } from '../lib/api'

const loading = ref(false)
const trendDays = ref(7)

const overview = ref({
  total_orders: 0,
  completed_orders: 0,
  pending_orders: 0,
  completion_rate: 0,
  avg_rating: 0,
  complaint_count: 0,
})

const ordersTrend = ref({ days: 7, items: [] })
const serviceDistribution = ref({ items: [] })
const statusDistribution = ref({ items: [] })
const nurseRanking = ref({ items: [] })
const complaintTrend = ref({ days: 7, items: [] })

const trendChartRef = ref(null)
const serviceChartRef = ref(null)
const statusChartRef = ref(null)
const complaintTrendChartRef = ref(null)

let trendChart = null
let serviceChart = null
let statusChart = null
let complaintTrendChart = null

const formatPercent = (value) => `${Math.round((Number(value) || 0) * 10000) / 100}%`

const translateStatus = (status) => {
  const map = {
    pending: '待处理',
    accepted: '已接单',
    in_service: '服务中',
    completed: '已完成',
  }
  return map[status] || status
}

const initCharts = () => {
  if (trendChartRef.value) trendChart = echarts.init(trendChartRef.value)
  if (serviceChartRef.value) serviceChart = echarts.init(serviceChartRef.value)
  if (statusChartRef.value) statusChart = echarts.init(statusChartRef.value)
  if (complaintTrendChartRef.value) complaintTrendChart = echarts.init(complaintTrendChartRef.value)
}

const resizeCharts = () => {
  trendChart?.resize()
  serviceChart?.resize()
  statusChart?.resize()
  complaintTrendChart?.resize()
}

const renderTrendChart = () => {
  if (!trendChart) return

  const xData = ordersTrend.value.items.map((item) => item.date)
  const yData = ordersTrend.value.items.map((item) => item.count)

  trendChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { left: 40, right: 20, top: 30, bottom: 30 },
    xAxis: {
      type: 'category',
      data: xData,
      axisLabel: { rotate: 25 },
    },
    yAxis: {
      type: 'value',
      minInterval: 1,
    },
    series: [
      {
        name: '订单数',
        type: 'line',
        smooth: true,
        data: yData,
        symbolSize: 8,
        lineStyle: { width: 3 },
        areaStyle: { opacity: 0.12 },
      },
    ],
  })
}

const renderServiceChart = () => {
  if (!serviceChart) return

  serviceChart.setOption({
    tooltip: {
      trigger: 'item',
      formatter: '{b}<br/>订单数：{c}<br/>占比：{d}%',
    },
    legend: {
      bottom: 0,
      type: 'scroll',
    },
    series: [
      {
        name: '服务分布',
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['50%', '45%'],
        data: serviceDistribution.value.items.map((item) => ({
          name: item.service_name,
          value: item.count,
        })),
        label: {
          formatter: '{b}\n{d}%',
        },
      },
    ],
  })
}

const renderStatusChart = () => {
  if (!statusChart) return

  statusChart.setOption({
    tooltip: {
      trigger: 'item',
      formatter: '{b}<br/>数量：{c}<br/>占比：{d}%',
    },
    legend: {
      bottom: 0,
    },
    series: [
      {
        name: '订单状态',
        type: 'pie',
        radius: ['45%', '75%'],
        center: ['50%', '45%'],
        avoidLabelOverlap: true,
        data: statusDistribution.value.items.map((item) => ({
          name: translateStatus(item.status),
          value: item.count,
        })),
        label: {
          formatter: '{b}\n{d}%',
        },
      },
    ],
  })
}

const renderComplaintTrendChart = () => {
  if (!complaintTrendChart) return

  const xData = complaintTrend.value.items.map((item) => item.date)
  const yData = complaintTrend.value.items.map((item) => item.count)

  complaintTrendChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { left: 40, right: 20, top: 30, bottom: 30 },
    xAxis: {
      type: 'category',
      data: xData,
      axisLabel: { rotate: 25 },
    },
    yAxis: {
      type: 'value',
      minInterval: 1,
    },
    series: [
      {
        name: '投诉数',
        type: 'bar',
        data: yData,
        barWidth: '40%',
        itemStyle: {
          borderRadius: [6, 6, 0, 0],
        },
      },
    ],
  })
}

const loadAll = async () => {
  loading.value = true
  try {
    const [
      overviewRes,
      trendRes,
      serviceRes,
      statusRes,
      rankingRes,
      complaintRes,
    ] = await Promise.all([
      analyticsApi.getOverview(),
      analyticsApi.getOrdersTrend(trendDays.value),
      analyticsApi.getServiceDistribution(),
      analyticsApi.getOrderStatusDistribution(),
      analyticsApi.getNurseRanking(),
      analyticsApi.getComplaintTrend(trendDays.value),
    ])

    overview.value = overviewRes.data || overviewRes
    ordersTrend.value = trendRes.data || trendRes
    serviceDistribution.value = serviceRes.data || serviceRes
    statusDistribution.value = statusRes.data || statusRes
    nurseRanking.value = rankingRes.data || rankingRes
    complaintTrend.value = complaintRes.data || complaintRes

    await nextTick()
    renderTrendChart()
    renderServiceChart()
    renderStatusChart()
    renderComplaintTrendChart()
  } finally {
    loading.value = false
  }
}

const handleResize = () => resizeCharts()

onMounted(async () => {
  initCharts()
  await loadAll()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  trendChart?.dispose()
  serviceChart?.dispose()
  statusChart?.dispose()
  complaintTrendChart?.dispose()
})
</script>

<style scoped>
.dashboard-page {
  padding: 24px;
  background: linear-gradient(180deg, #f7f9fc 0%, #eef3fb 100%);
  min-height: 100vh;
  color: #1f2937;
}

.dashboard-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 24px;
}

.dashboard-header h1 {
  margin: 0;
  font-size: 30px;
  font-weight: 800;
  color: #111827;
}

.dashboard-header p {
  margin: 8px 0 0;
  color: #6b7280;
}

.refresh-btn {
  border: none;
  background: linear-gradient(135deg, #2563eb, #1d4ed8);
  color: #fff;
  padding: 12px 18px;
  border-radius: 12px;
  cursor: pointer;
  font-weight: 600;
  box-shadow: 0 8px 20px rgba(37, 99, 235, 0.18);
  transition: transform 0.2s ease, opacity 0.2s ease;
}

.refresh-btn:hover {
  transform: translateY(-1px);
}

.refresh-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.kpi-grid {
  display: grid;
  grid-template-columns: repeat(6, minmax(0, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.kpi-card,
.chart-card {
  background: rgba(255, 255, 255, 0.88);
  backdrop-filter: blur(14px);
  border: 1px solid rgba(255, 255, 255, 0.6);
  border-radius: 18px;
  box-shadow: 0 12px 30px rgba(15, 23, 42, 0.08);
}

.kpi-card {
  padding: 18px;
}

.kpi-label {
  font-size: 13px;
  color: #6b7280;
}

.kpi-value {
  margin-top: 10px;
  font-size: 28px;
  font-weight: 800;
  color: #111827;
}

.chart-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.chart-card {
  padding: 18px;
  min-height: 360px;
}

.chart-large {
  grid-column: span 2;
}

.chart-header {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 12px;
}

.chart-header h2 {
  margin: 0;
  font-size: 18px;
  color: #111827;
}

.chart-header span {
  color: #6b7280;
  font-size: 13px;
}

.chart-box {
  width: 100%;
  height: 300px;
}

.rank-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 8px;
}

.rank-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px;
  border-radius: 14px;
  background: #f8fafc;
  border: 1px solid #e5e7eb;
}

.rank-left {
  display: flex;
  align-items: center;
  gap: 14px;
}

.rank-index {
  width: 32px;
  height: 32px;
  border-radius: 999px;
  background: #2563eb;
  color: #fff;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
}

.rank-name {
  font-weight: 700;
  color: #111827;
}

.rank-sub {
  font-size: 12px;
  color: #6b7280;
  margin-top: 4px;
}

.rank-value {
  font-weight: 700;
  color: #2563eb;
}

.empty-state {
  padding: 28px;
  text-align: center;
  color: #6b7280;
  border: 1px dashed #d1d5db;
  border-radius: 14px;
  background: #fafafa;
}

@media (max-width: 1200px) {
  .kpi-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }

  .chart-grid {
    grid-template-columns: 1fr;
  }

  .chart-large {
    grid-column: span 1;
  }
}

@media (max-width: 768px) {
  .dashboard-page {
    padding: 16px;
  }

  .dashboard-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .kpi-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .chart-box {
    height: 260px;
  }
}

@media (max-width: 480px) {
  .kpi-grid {
    grid-template-columns: 1fr;
  }
}
</style>