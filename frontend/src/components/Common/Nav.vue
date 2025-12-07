<template>
  <div v-if="!isAuthPage">
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary mb-4 shadow-sm">
      <div class="container">
        <router-link class="navbar-brand fw-bold" to="/">Vehicle Parking App</router-link>

        <div class="d-flex align-items-center text-white" v-if="isLoggedIn">
          <span class="me-3"><i class="bi bi-person-circle me-1"></i> {{ username }}</span>
          <button class="btn btn-sm btn-light text-primary fw-bold" @click="logout">Logout</button>
        </div>
        
        <div v-else>
          <router-link class="btn btn-sm btn-outline-light me-2" to="/login">Login</router-link>
          <router-link class="btn btn-sm btn-light text-primary" to="/register">Register</router-link>
        </div>
      </div>
    </nav>
  </div>
</template>

<script>
export default {
  name: 'Nav',
  data() {
    return {
      isLoggedIn: false,
      userRole: null,
      username: null,
    };
  },
  computed: {
    isAuthPage() {
      const path = this.$route.path;
      return path === '/login' || path === '/register';
    }
  },
  watch: {
    '$route': 'updateAuthState'
  },
  created() {
    this.updateAuthState();
    window.addEventListener('storage', this.updateAuthState);
  },
  beforeUnmount() {
    window.removeEventListener('storage', this.updateAuthState);
  },
  methods: {
    updateAuthState() {
      const raw = localStorage.getItem('qm_auth');
      if (raw) {
        try {
          const authData = JSON.parse(raw);
          this.isLoggedIn = !!authData.user;
          this.userRole = authData.user?.role;
          this.username = authData.user?.username; 
          return;
        } catch (e) { console.error(e); }
      }
      this.isLoggedIn = false;
      this.userRole = null;
      this.username = null;
    },
    logout() {
      localStorage.removeItem('qm_auth');
      this.updateAuthState();
      this.$router.push('/login');
    },
  }
}
</script>
