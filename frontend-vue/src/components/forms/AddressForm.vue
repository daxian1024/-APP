<template>
  <div class="grid-2">
    <input v-model="form.contact_name" class="input input-bordered" placeholder="联系人" />
    <input v-model="form.contact_phone" class="input input-bordered" placeholder="联系电话" />
    <input v-model="form.province" class="input input-bordered" placeholder="省" />
    <input v-model="form.city" class="input input-bordered" placeholder="市" />
    <input v-model="form.district" class="input input-bordered" placeholder="区" />
    <input v-model="form.detail" class="input input-bordered" placeholder="详细地址" />
  </div>
</template>

<script setup>
import { reactive } from 'vue'

const form = reactive({
  contact_name: '',
  contact_phone: '',
  province: '',
  city: '',
  district: '',
  detail: '',
})

function getPayload() {
  return { ...form }
}

function setPayload(payload = {}) {
  Object.assign(form, payload)
}

function reset() {
  setPayload({
    contact_name: '', contact_phone: '', province: '', city: '', district: '', detail: '',
  })
}

defineExpose({ getPayload, setPayload, reset })
</script>
