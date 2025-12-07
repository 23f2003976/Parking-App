import { createRouter, createWebHistory } from 'vue-router';
import Login from './components/Common/Login.vue';
import Register from './components/Common/Register.vue';
import AdminDashboard from './components/Admin/AdminDashboard.vue';
import UserDashboard from './components/User/UserDashboard.vue';
import ActiveSession from './components/User/ActiveSession.vue'; 
import BookingHistory from './components/User/BookingHistory.vue';

const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', component: Login },
  { path: '/register', component: Register },
  { path: '/admin', component: AdminDashboard, meta: { requiresAuth: true, role: 'admin' } },
  { 
    path: '/user', 
    component: UserDashboard, 
    meta: { requiresAuth: true, role: 'user' }, 
    children: [
      { path: 'history', component: BookingHistory, name: 'BookingHistory' } 
    ] 
  },
  { path: '/user/session/:id', component: ActiveSession, meta: { requiresAuth: true, role: 'user' } },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to, from, next) => {
  const raw = localStorage.getItem('qm_auth');
  if (to.meta.requiresAuth) {
    if (!raw) return next('/login');
    const { user } = JSON.parse(raw);
    if (!user) return next('/login');
    if (to.meta.role && user.role !== to.meta.role) return next('/login');
  }
  next();
});

export default router;