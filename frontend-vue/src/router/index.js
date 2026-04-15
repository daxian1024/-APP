import { createRouter, createWebHistory } from 'vue-router'
import ServicesPage from '../pages/ServicesPage.vue'
import AddressPage from '../pages/AddressPage.vue'
import OrderPage from '../pages/OrderPage.vue'
import TimelinePage from '../pages/TimelinePage.vue'
import FeedbackPage from '../pages/FeedbackPage.vue'
import ProfilePage from '../pages/ProfilePage.vue'
import SpacePage from '../pages/SpacePage.vue'

const routes = [
  { path: '/', redirect: '/services' },
  { path: '/services', component: ServicesPage, meta: { title: '服务项目' } },
  { path: '/address', component: AddressPage, meta: { title: '地址管理' } },
  { path: '/orders', component: OrderPage, meta: { title: '下单与支付' } },
  { path: '/timeline', component: TimelinePage, meta: { title: '订单时间线' } },
  { path: '/feedback', component: FeedbackPage, meta: { title: '评价与投诉' } },
  { path: '/profile', component: ProfilePage, meta: { title: '个人资料' } },
  { path: '/space', component: SpacePage, meta: { title: '个人空间' } },
  { path: '/analytics', component: SpacePage, meta: { title: '数据看板' } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.afterEach((to) => {
  document.title = to.meta?.title ? `${to.meta.title} - 智慧护理平台` : '智慧护理平台'
})

export default router