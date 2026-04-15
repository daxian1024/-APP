<template>
  <div>
    <h2 class="page-title">评价与投诉</h2>

    <div class="section-card mb-3">
      <div class="grid-2">
        <input v-model.number="reviewOrderId" class="input input-bordered" placeholder="评价订单ID" />
        <select v-model.number="rating" class="select select-bordered">
          <option :value="5">5星</option>
          <option :value="4">4星</option>
          <option :value="3">3星</option>
          <option :value="2">2星</option>
          <option :value="1">1星</option>
        </select>
      </div>
      <textarea v-model="comment" class="textarea textarea-bordered w-full mt-2" placeholder="评价内容" />
      <div class="flex gap-2 mt-2">
        <button class="btn btn-primary btn-sm" @click="createReview">提交评价</button>
        <button class="btn btn-sm" @click="loadReviews">我的评价</button>
      </div>
    </div>

    <div class="section-card mb-3">
      <div class="grid-2">
        <input v-model.number="complaintOrderId" class="input input-bordered" placeholder="投诉订单ID(可选)" />
        <button class="btn btn-error btn-sm" @click="createComplaint">提交投诉</button>
      </div>
      <textarea v-model="complaintContent" class="textarea textarea-bordered w-full mt-2" placeholder="投诉内容" />
      <button class="btn btn-sm mt-2" @click="loadComplaints">我的投诉</button>
    </div>

    <div class="grid cards">
      <article v-for="f in records" :key="`${f.type}-${f.id}`" class="section-card">
        <h3>{{ f.type }} #{{ f.id }}</h3>
        <p class="text-slate-400 text-sm">订单: {{ f.order_id || '-' }} {{ f.rating ? `| 评分:${f.rating}` : '' }} {{ f.status ? `| 状态:${f.status}` : '' }}</p>
        <p>{{ f.comment || f.content }}</p>
      </article>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import api from '../lib/api'

const reviewOrderId = ref(null)
const rating = ref(5)
const comment = ref('')

const complaintOrderId = ref(null)
const complaintContent = ref('')

const records = ref([])

async function createReview() {
  try {
    await api.post('/feedback/reviews', {
      order_id: reviewOrderId.value,
      rating: rating.value,
      comment: comment.value,
    })
    await loadReviews()
  } catch (e) {
    alert(e?.response?.data?.message || '评价失败')
  }
}

async function createComplaint() {
  try {
    await api.post('/feedback/complaints', {
      order_id: complaintOrderId.value || null,
      content: complaintContent.value,
    })
    await loadComplaints()
  } catch (e) {
    alert(e?.response?.data?.message || '投诉失败')
  }
}

async function loadReviews() {
  const res = await api.get('/feedback/reviews')
  records.value = (res.data?.data?.items || []).map((x) => ({ ...x, type: '评价' }))
}

async function loadComplaints() {
  const res = await api.get('/feedback/complaints')
  records.value = (res.data?.data?.items || []).map((x) => ({ ...x, type: '投诉' }))
}
</script>

<style scoped>
.cards { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 12px; }
</style>
