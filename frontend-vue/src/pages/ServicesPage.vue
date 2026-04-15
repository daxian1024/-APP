<template>
  <div>
    <h2 class="page-title">服务项目</h2>

    <div class="section-card mb-3">
      <div class="flex gap-2">
        <button class="btn btn-sm" @click="loadServices(true)">刷新全部</button>
        <button class="btn btn-sm btn-primary" @click="loadPopular">热门服务</button>
      </div>
    </div>

    <div class="grid cards">
      <article v-for="item in visible" :key="item.id" class="section-card service-card">
        <h3>#{{ item.id }} {{ item.name }}</h3>
        <p class="muted">{{ item.description || '暂无描述' }}</p>
        <div class="price">￥{{ item.price }} / {{ item.duration_minutes }}分钟</div>
      </article>
    </div>

    <div ref="loadMoreRef" class="py-4 text-center text-sm text-slate-400">{{ loadingMore ? '加载中...' : '向下滚动加载更多' }}</div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import api from '../lib/api'

const all = ref([])
const page = ref(1)
const pageSize = 8
const loadingMore = ref(false)
const loadMoreRef = ref(null)

const visible = computed(() => all.value.slice(0, page.value * pageSize))

async function loadServices(reset = false) {
  const res = await api.get('/services')
  all.value = res.data?.data?.items || []
  if (reset) page.value = 1
}

async function loadPopular() {
  const res = await api.get('/services/popular')
  all.value = res.data?.data?.items || []
  page.value = 1
}

function setupInfinite() {
  const io = new IntersectionObserver((entries) => {
    const e = entries[0]
    if (!e.isIntersecting) return
    if (visible.value.length >= all.value.length) return
    loadingMore.value = true
    setTimeout(() => {
      page.value += 1
      loadingMore.value = false
    }, 250)
  }, { threshold: 0.2 })

  if (loadMoreRef.value) io.observe(loadMoreRef.value)
}

onMounted(async () => {
  await loadServices(true)
  setupInfinite()
})
</script>

<style scoped>
.cards { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 12px; }
.service-card h3 { margin: 0 0 8px; font-size: 18px; }
.muted { color: #8ca3c5; margin: 0 0 8px; }
.price { color: #5de2d1; font-weight: 700; }
</style>
