<template>
  <div>
    <h2 class="page-title">个人空间</h2>

    <div class="grid-2">
      <section class="section-card">
        <h3 class="text-lg font-bold mb-2">历史订单</h3>
        <ul class="space-list">
          <li v-for="o in orders" :key="o.id" class="space-item">
            <div class="font-semibold">{{ o.order_no }}</div>
            <div class="text-slate-400 text-sm">{{ o.service_name }} | {{ o.status }} | {{ o.appointment_time }}</div>
          </li>
          <li v-if="orders.length===0" class="text-slate-400">暂无历史订单</li>
        </ul>
      </section>

      <section class="section-card">
        <h3 class="text-lg font-bold mb-2">常用服务项目</h3>
        <ul class="space-list">
          <li v-for="s in favoriteServices" :key="s.id" class="space-item">
            <div class="font-semibold">#{{ s.id }} {{ s.name }}</div>
            <div class="text-slate-400 text-sm">￥{{ s.price }} / {{ s.duration_minutes }}分钟</div>
          </li>
          <li v-if="favoriteServices.length===0" class="text-slate-400">暂无常用服务</li>
        </ul>
      </section>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import api from '../lib/api'

const orders = ref([])
const favoriteServices = ref([])

async function loadOrders() {
  const res = await api.get('/orders')
  orders.value = res.data?.data?.items || []
}

async function loadFavoriteServices() {
  const res = await api.get('/services/popular')
  favoriteServices.value = res.data?.data?.items || []
}

onMounted(async () => {
  try {
    await Promise.all([loadOrders(), loadFavoriteServices()])
  } catch (_e) {}
})
</script>

<style scoped>
.space-list { list-style: none; margin: 0; padding: 0; display: grid; gap: 8px; }
.space-item { padding: 10px; border: 1px solid rgba(95, 120, 153, .35); border-radius: 10px; background: rgba(18, 28, 45, .7); }
</style>
