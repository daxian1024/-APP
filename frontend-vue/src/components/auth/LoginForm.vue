<template>
  <form class="space-y-3" @submit.prevent="submit">
    <div>
      <label class="label"><span class="label-text">用户名/手机号</span></label>
      <input v-model="account" class="input input-bordered w-full" placeholder="请输入用户名或手机号" />
    </div>
    <div>
      <label class="label"><span class="label-text">密码</span></label>
      <input v-model="password" type="password" class="input input-bordered w-full" placeholder="请输入密码" />
    </div>

    <button class="btn btn-primary w-full" :disabled="loading">{{ loading ? '登录中...' : '登录' }}</button>

    <div class="text-right text-sm">
      <a class="link link-hover" @click="$emit('switch', 'register')">注册</a>
    </div>
  </form>
</template>

<script setup>
import { ref } from 'vue'
import { useAuthStore } from '../../stores/auth'

const emit = defineEmits(['success', 'switch'])
const auth = useAuthStore()
const account = ref('')
const password = ref('')
const loading = ref(false)

async function submit() {
  if (!account.value || !password.value) return
  loading.value = true
  try {
    await auth.login(account.value, password.value)
    emit('success')
  } catch (e) {
    alert(e?.response?.data?.message || '登录失败')
  } finally {
    loading.value = false
  }
}
</script>
