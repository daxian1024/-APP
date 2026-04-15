import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'
import 'daisyui/daisyui.css'
import 'daisyui/themes.css'
import './style.css'
import App from './App.vue'
import { useAuthStore } from './stores/auth'

import ServicesPage from './pages/ServicesPage.vue'
import AddressPage from './pages/AddressPage.vue'
import OrderPage from './pages/OrderPage.vue'
import TimelinePage from './pages/TimelinePage.vue'
import FeedbackPage from './pages/FeedbackPage.vue'
import ProfilePage from './pages/ProfilePage.vue'
import SpacePage from './pages/SpacePage.vue'

const routes = [
  { path: '/', redirect: '/services' },
  { path: '/services', component: ServicesPage },
  { path: '/address', component: AddressPage },
  { path: '/orders', component: OrderPage },
  { path: '/timeline', component: TimelinePage },
  { path: '/feedback', component: FeedbackPage },
  { path: '/profile', component: ProfilePage },
  { path: '/space', component: SpacePage },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

const app = createApp(App)
const pinia = createPinia()
app.use(pinia)
app.use(router)

const auth = useAuthStore()
if (typeof auth.hydrate === 'function') {
  auth.hydrate()
}

app.mount('#app')
