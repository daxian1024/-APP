<template>
  <div>
    <h2 class="page-title">订单时间线</h2>
    <div class="section-card mb-3 grid-2">
      <input v-model.number="orderId" class="input input-bordered" placeholder="订单ID" />
      <button class="btn btn-sm" @click="load">查询时间线</button>
    </div>

    <ul class="timeline-list">
      <li v-for="t in items" :key="t.id" class="section-card">
        <div class="font-bold">{{ t.from_status || 'null' }} → {{ t.to_status }}</div>
        <div class="text-slate-400 text-sm">{{ t.remark }} | {{ t.created_at }}</div>
      </li>
    </ul>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import api from '../lib/api'

const orderId = ref(null)
const items = ref([])

async function load() {
  if (!orderId.value) return
  try {
    const res = await api.get(`/orders/${orderId.value}/timeline`)
    items.value = res.data?.data?.items || []
  } catch (e) {
    alert(e?.response?.data?.message || '查询失败')
  }
}
</script>

<style scoped>
.timeline-list { list-style: none; margin: 0; padding: 0; display: grid; gap: 10px; }
</style>
