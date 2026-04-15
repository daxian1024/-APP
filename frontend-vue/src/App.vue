<template>
  <div data-theme="night" class="app-shell">
    <div class="app-drawer" :class="{ open: drawerOpen }">
      <aside class="sidebar">
        <div class="menu-title">功能菜单</div>
        <RouterLink to="/services" class="menu-item">服务项目</RouterLink>
        <RouterLink to="/address" class="menu-item">地址管理</RouterLink>
        <RouterLink to="/orders" class="menu-item">下单与支付</RouterLink>
        <RouterLink to="/timeline" class="menu-item">订单时间线</RouterLink>
        <RouterLink to="/feedback" class="menu-item">评价与投诉</RouterLink>
        <RouterLink to="/profile" class="menu-item">个人资料</RouterLink>
        <RouterLink to="/space" class="menu-item">个人空间</RouterLink>
      </aside>
    </div>

    <div class="main">
      <header class="topbar">
        <div class="left">
          <button class="btn btn-ghost btn-sm" @click="drawerOpen = !drawerOpen">☰</button>
          <h1>智慧护理平台</h1>
          <input class="input input-bordered search" placeholder="搜索服务、订单号" />
        </div>

        <div class="right">
          <button v-if="!auth.isLoggedIn" class="btn btn-primary btn-sm" @click="openAuth('login')">登录</button>
          <div v-else class="dropdown dropdown-end">
            <label tabindex="0" class="avatar-wrap" role="button">
              <img :src="auth.avatar || defaultAvatar" class="avatar-img" alt="avatar" />
            </label>
            <ul tabindex="0" class="menu dropdown-content z-[1] p-2 shadow bg-base-100 rounded-box w-52">
              <li class="menu-title">{{ auth.displayName }}</li>
              <li><RouterLink to="/profile">个人资料</RouterLink></li>
              <li><RouterLink to="/space">个人空间</RouterLink></li>
              <li><a @click="logout">退出登录</a></li>
            </ul>
          </div>
        </div>
      </header>

      <main class="content">
        <RouterView />
      </main>
    </div>

    <AuthModal ref="authModalRef" @logged-in="afterLogin" />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { RouterLink, RouterView, useRouter } from 'vue-router'
import { useAuthStore } from './stores/auth'
import AuthModal from './components/auth/AuthModal.vue'

const drawerOpen = ref(true)
const authModalRef = ref(null)
const auth = useAuthStore()
const router = useRouter()
const defaultAvatar = 'https://api.dicebear.com/9.x/notionists/svg?seed=smartcare'

function openAuth(mode = 'login') {
  authModalRef.value?.open(mode)
}

function afterLogin() {
  router.push('/services')
}

function logout() {
  auth.logout()
  router.push('/services')
}
</script>

<style scoped>
.app-shell { display: flex; min-height: 100vh; color: #eaf1fc; background: #0b1420; }
.app-drawer { width: 250px; border-right: 1px solid rgba(111, 133, 164, .2); background: #0f1a2a; transition: .2s; }
.app-drawer:not(.open) { width: 0; overflow: hidden; }
.sidebar { padding: 14px; display: flex; flex-direction: column; gap: 8px; }
.menu-title { color: #8ea1bd; font-size: 13px; margin: 4px 8px; }
.menu-item { color: #dce7f8; text-decoration: none; padding: 10px 12px; border-radius: 10px; }
.menu-item:hover, .router-link-active { background: #1d3048; }

.main { flex: 1; min-width: 0; }
.topbar {
  height: 60px; border-bottom: 1px solid rgba(111, 133, 164, .2);
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 12px; background: #101b2c; position: sticky; top: 0; z-index: 20;
}
.left { display: flex; align-items: center; gap: 10px; min-width: 0; }
.left h1 { margin: 0; font-size: 34px; font-weight: 700; }
.search { width: 360px; max-width: 34vw; }
.right { display: flex; align-items: center; gap: 8px; }
.avatar-wrap { display: inline-flex; cursor: pointer; }
.avatar-img { width: 38px; height: 38px; border-radius: 999px; border: 2px solid rgba(101, 201, 255, .45); }
.content { padding: 16px; }

@media (max-width: 900px) {
  .app-drawer { position: fixed; left: 0; top: 60px; bottom: 0; z-index: 30; }
  .search { display: none; }
}
</style>
