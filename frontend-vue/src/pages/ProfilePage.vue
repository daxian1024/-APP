<template>
  <div>
    <h2 class="page-title">编辑资料</h2>

    <div class="section-card max-w-3xl">
      <div class="avatar-block">
        <label class="avatar-picker" for="avatarInput">
          <img :src="previewAvatar" class="avatar" alt="avatar" />
          <span class="camera">📷</span>
        </label>
        <input id="avatarInput" type="file" accept="image/*" class="hidden" @change="onPickAvatar" />
      </div>

      <div class="mt-4">
        <label class="label">用户名</label>
        <input v-model="username" class="input input-bordered w-full" placeholder="用户名" />
      </div>

      <div class="mt-3">
        <label class="label">简介</label>
        <textarea v-model="bio" class="textarea textarea-bordered w-full" rows="5" placeholder="请输入简介" />
      </div>

      <button class="btn btn-primary mt-4 w-44" @click="save">更新</button>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const username = ref(auth.user?.username || '')
const bio = ref(auth.bio || '')
const localAvatar = ref(auth.avatar || '')

const previewAvatar = computed(() => localAvatar.value || 'https://api.dicebear.com/9.x/notionists/svg?seed=profile')

function onPickAvatar(e) {
  const file = e.target.files?.[0]
  if (!file) return
  const reader = new FileReader()
  reader.onload = () => {
    localAvatar.value = String(reader.result || '')
  }
  reader.readAsDataURL(file)
}

async function save() {
  if (!auth.isLoggedIn) return alert('请先登录')
  try {
    await auth.updateProfile({ username: username.value.trim(), bio: bio.value.trim(), avatar: localAvatar.value })
    alert('资料更新成功，可使用新用户名登录')
  } catch (e) {
    alert(e?.response?.data?.message || '更新失败')
  }
}
</script>

<style scoped>
.avatar-block { display: flex; justify-content: center; }
.avatar-picker { position: relative; cursor: pointer; display: inline-flex; }
.avatar {
  width: 150px; height: 150px; border-radius: 999px;
  border: 3px solid rgba(92, 212, 255, .5); object-fit: cover;
}
.camera {
  position: absolute; right: 8px; bottom: 8px; width: 34px; height: 34px;
  border-radius: 999px; background: rgba(16, 26, 40, .85);
  display: grid; place-items: center;
}
</style>
