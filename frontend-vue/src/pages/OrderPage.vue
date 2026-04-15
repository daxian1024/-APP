<template>
  <div>
    <h2 class="page-title">下单与支付</h2>
    <div class="section-card mb-3">
      <div class="grid-2">
        <input v-model.number="service_item_id" class="input input-bordered" placeholder="服务项目ID" />
        <input v-model.number="address_id" class="input input-bordered" placeholder="地址ID" />
        <input v-model="appointment_time" class="input input-bordered" placeholder="预约时间 2026-04-15 10:00" />
        <input v-model="note" class="input input-bordered" placeholder="备注" />
      </div>
      <button class="btn btn-primary btn-sm mt-3" @click="createOrder">提交预约</button>
    </div>

    <div class="section-card">
      <div class="grid-2">
        <input v-model.number="payOrderId" class="input input-bordered" placeholder="订单ID" />
        <button class="btn btn-sm" @click="payOrder">模拟支付</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import api from '../lib/api'

const service_item_id = ref(null)
const address_id = ref(null)
const appointment_time = ref('')
const note = ref('')
const payOrderId = ref(null)

async function createOrder() {
  try {
    const res = await api.post('/orders', {
      service_item_id: service_item_id.value,
      address_id: address_id.value,
      appointment_time: appointment_time.value,
      note: note.value,
    })
    payOrderId.value = res.data?.data?.order_id || null
    alert('下单成功')
  } catch (e) {
    alert(e?.response?.data?.message || '下单失败')
  }
}

async function payOrder() {
  if (!payOrderId.value) return alert('请输入订单ID')
  try {
    await api.post(`/orders/${payOrderId.value}/pay`, { method: 'mock_alipay' })
    alert('支付成功')
  } catch (e) {
    alert(e?.response?.data?.message || '支付失败')
  }
}
</script>
