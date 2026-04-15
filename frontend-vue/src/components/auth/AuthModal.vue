<template>
  <dialog ref="dlg" class="modal">
    <div class="modal-box max-w-md">
      <h3 class="font-bold text-lg mb-3">{{ mode === 'login' ? '登录' : '注册' }}</h3>
      <LoginForm v-if="mode==='login'" @success="onSuccess" @switch="switchMode" />
      <RegisterForm v-else @success="onSuccess" @switch="switchMode" />
    </div>
    <form method="dialog" class="modal-backdrop"><button>close</button></form>
  </dialog>
</template>

<script setup>
import { ref } from 'vue'
import LoginForm from './LoginForm.vue'
import RegisterForm from './RegisterForm.vue'

const emit = defineEmits(['logged-in'])
const dlg = ref(null)
const mode = ref('login')

function open(m = 'login') {
  mode.value = m
  dlg.value?.showModal()
}

function switchMode(m) {
  mode.value = m
}

function onSuccess() {
  dlg.value?.close()
  emit('logged-in')
}

defineExpose({ open })
</script>
