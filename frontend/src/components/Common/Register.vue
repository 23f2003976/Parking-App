<template>
  <div class="row justify-content-center">
    <div class="col-md-6">
      <div class="card p-4 shadow-sm border-0">
        <h3 class="mb-3 text-center text-primary">Register for Parking App</h3>
        <form @submit.prevent="submit">
          <div class="mb-3">
            <label class="form-label">Username</label>
            <input v-model="form.username" class="form-control" required />
          </div>
          <div class="mb-3">
            <label class="form-label">Email</label>
            <input v-model="form.email" type="email" class="form-control" required />
          </div>
          <div class="mb-3">
            <label class="form-label">Password</label>
            <input v-model="form.password" type="password" class="form-control" required />
          </div>
          
          <div v-if="errorMessage" class="alert alert-danger p-2 mt-2">{{ errorMessage }}</div>

          <button class="btn btn-success w-100 mt-3">Create Account</button>
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
      form: { username: '', email: '', password: '' },
      errorMessage: null,
    } 
  },
  methods: {
    async submit() {
      this.errorMessage = null;
      try {
        await api.post('/auth/register', this.form);
        alert("Registration successful! Please login.");
        this.$router.push('/login');
      } catch (e) {
        this.errorMessage = e.response?.data?.message || 'Registration failed.';
      }
    }
  }
}
</script>
