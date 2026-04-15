<template>
  <form class="space-y-3" @submit.prevent="submit">
    <div>
      <label class="label"><span class="label-text">用户名</span></label>
      <input v-model="username" class="input input-bordered w-full" placeholder="请输入用户名" />
    </div>
    <div>
      <label class="label"><span class="label-text">手机号</span></label>
      <input v-model="phone" class="input input-bordered w-full" placeholder="请输入手机号" />
    </div>
    <div>
      <label class="label"><span class="label-text">密码</span></label>
      <input v-model="password" type="password" class="input input-bordered w-full" placeholder="请输入密码" />
    </div>
    <div>
      <label class="label"><span class="label-text">确认密码</span></label>
      <input v-model="confirmPassword" type="password" class="input input-bordered w-full" placeholder="请再次输入密码" />
    </div>

    <button class="btn btn-primary w-full" :disabled="loading">{{ loading ? '注册中...' : '注册' }}</button>

    <div class="text-right text-sm">
      <a class="link link-hover" @click="$emit('switch', 'login')">登录</a>
    </div>
  </form>
</template>

<script setup>
import { ref } from 'vue'
import { useAuthStore } from '../../stores/auth'

const emit = defineEmits(['success', 'switch'])
const auth = useAuthStore()
const username = ref('')
const phone = ref('')
const password = ref('')
const confirmPassword = ref('')
const loading = ref(false)

async function submit() {
  if (!username.value || !phone.value || !password.value) return
  if (password.value !== confirmPassword.value) return alert('两次密码不一致')
  loading.value = true
  try {
    await auth.register(username.value, phone.value, password.value)
    emit('success')
  } catch (e) {
    alert(e?.response?.data?.message || '注册失败')
  } finally {
    loading.value = false
  }
}
</script>
