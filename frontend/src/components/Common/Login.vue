<template>
  <div class="row justify-content-center">
    <div class="col-md-6">
      <div class="card p-4 shadow-sm border-0">
        <h3 class="mb-3 text-center text-primary">Login</h3>
        <form @submit.prevent="submit">
          <div class="mb-3">
            <label class="form-label">Username</label>
            <input v-model="form.username" class="form-control" required />
          </div>
          <div class="mb-3">
            <label class="form-label">Password</label>
            <input v-model="form.password" type="password" class="form-control" required />
          </div>
          
          <div v-if="errorMessage" class="alert alert-danger p-2 mt-2">{{ errorMessage }}</div>

          <button class="btn btn-primary w-100 mt-3">Login</button>
          
          <div class="text-center mt-3">
            <router-link to="/register">Create an account</router-link>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import api from '@/axios';

export default {
  data() {
    return {
      form: { username: '', password: '' },
      errorMessage: null,
    }
  },
  methods: {
    async submit() {
      this.errorMessage = null;
      try {
        const res = await api.post('/auth/login', this.form);
        const { token, role, user } = res.data;
        const userData = user || { username: this.form.username, role };
        
        localStorage.setItem('qm_auth', JSON.stringify({ token, user: userData }));
        window.dispatchEvent(new Event('storage')); 
        
        if (userData.role === 'admin') this.$router.push('/admin');
        else this.$router.push('/user');
      } catch (e) {
        this.errorMessage = e.response?.data?.error || 'Invalid credentials.';
      }
    }
  }
}
</script>
