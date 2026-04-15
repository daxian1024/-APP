<template>
  <div>
    <h2 class="page-title">地址管理</h2>

    <div class="section-card mb-3">
      <AddressForm ref="formRef" />
      <div class="flex gap-2 mt-3">
        <button class="btn btn-primary btn-sm" @click="createAddress">新增地址</button>
        <button class="btn btn-sm" @click="load">刷新列表</button>
      </div>
    </div>

    <div class="section-card mb-3">
      <div class="grid-2">
        <input v-model.number="editId" class="input input-bordered" placeholder="编辑地址ID" />
        <button class="btn btn-sm" @click="updateAddress">更新地址</button>
        <input v-model.number="deleteId" class="input input-bordered" placeholder="删除地址ID" />
        <button class="btn btn-error btn-sm" @click="deleteAddress">删除地址</button>
      </div>
    </div>

    <div class="grid cards">
      <article v-for="a in items" :key="a.id" class="section-card">
        <h3>#{{ a.id }} {{ a.contact_name }} {{ a.contact_phone }}</h3>
        <p class="muted">{{ a.province }}{{ a.city }}{{ a.district }}{{ a.detail }}</p>
      </article>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import api from '../lib/api'
import AddressForm from '../components/forms/AddressForm.vue'

const items = ref([])
const formRef = ref(null)
const editId = ref(null)
const deleteId = ref(null)

async function load() {
  const res = await api.get('/addresses')
  items.value = res.data?.data?.items || []
}

async function createAddress() {
  try {
    await api.post('/addresses', { ...formRef.value.getPayload(), is_default: true })
    formRef.value.reset()
    await load()
  } catch (e) {
    alert(e?.response?.data?.message || '新增失败')
  }
}

async function updateAddress() {
  if (!editId.value) return alert('请输入编辑ID')
  try {
    await api.patch(`/addresses/${editId.value}`, formRef.value.getPayload())
    await load()
  } catch (e) {
    alert(e?.response?.data?.message || '更新失败')
  }
}

async function deleteAddress() {
  if (!deleteId.value) return alert('请输入删除ID')
  try {
    await api.delete(`/addresses/${deleteId.value}`)
    await load()
  } catch (e) {
    alert(e?.response?.data?.message || '删除失败')
  }
}

onMounted(load)
</script>

<style scoped>
.cards { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 12px; }
.muted { color: #8ca3c5; margin: 0; }
</style>
