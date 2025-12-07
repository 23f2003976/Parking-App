<template>
    <div class="search-manager card shadow-sm p-4">
      <h4 class="card-title mb-4">Search System</h4>
  
      <div class="input-group mb-4">
        <input 
          type="text" 
          class="form-control" 
          placeholder="Enter username or parking lot name..." 
          v-model="query"
          @keyup.enter="performSearch"
        >
        <button class="btn btn-primary" type="button" @click="performSearch" :disabled="loading">
          <span v-if="loading" class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
          {{ loading ? 'Searching...' : 'Search' }}
        </button>
      </div>
  
      <div v-if="!loading && searchExecuted && totalResults === 0" class="alert alert-warning">
        No results found for <strong>"{{ lastQuery }}"</strong>.
      </div>
  
      <div v-if="totalResults > 0">
        <h5 class="mb-3">Results for <strong>"{{ lastQuery }}"</strong></h5>
  
        <div v-if="results.users.length" class="mb-4">
          <h6><i class="bi bi-person-fill me-1"></i> Users ({{ results.users.length }})</h6>
          <ul class="list-group list-group-flush">
            <li v-for="user in results.users" :key="user.id" class="list-group-item d-flex justify-content-between align-items-center">
              <span>{{ user.username }} ({{ user.role }})</span>
              <small class="text-muted">ID: {{ user.id }}</small>
            </li>
          </ul>
        </div>
  
        <div v-if="results.lots.length" class="mb-4">
          <h6><i class="bi bi-p-square-fill me-1"></i> Parking Lots ({{ results.lots.length }})</h6>
          <ul class="list-group list-group-flush">
            <li v-for="lot in results.lots" :key="lot.id" class="list-group-item">
              <p class="mb-1 fw-bold">{{ lot.name }}</p>
              <small class="text-muted">{{ lot.location }}</small>
            </li>
          </ul>
        </div>
        
        <div v-if="results.spots.length" class="mb-4">
          <h6><i class="bi bi-p-square-fill me-1"></i> Parking Spots ({{ results.spots.length }})</h6>
          <ul class="list-group list-group-flush">
            <li v-for="spot in results.spots" :key="spot.id" class="list-group-item">
              <p class="mb-1 fw-bold">{{ spot.name }}</p>
              <small class="text-muted">Parking Lot ID: {{ spot.lot_id }}</small>
            </li>
          </ul>
        </div>

        </div>
    </div>
  </template>
  
  <script>
  import api from '@/axios';
  
  export default {
    data() {
      return {
        query: '',
        lastQuery: '',
        loading: false,
        searchExecuted: false,
        results: {
          users: [],
          lots: [],
          spots: []
        },
      };
    },
    computed: {
      totalResults() {
        return this.results.users.length + this.results.lots.length + this.results.spots.length;
      }
    },
    methods: {
      async performSearch() {
        if (!this.query.trim()) return;
  
        this.loading = true;
        this.searchExecuted = true;
        this.lastQuery = this.query.trim();
  
        try {
          const response = await api.get('/admin/search', {
            params: { q: this.query.trim() }
          });
  
          const data = response.data.results;
          this.results.users = data.users || [];
          this.results.lots = data.lots || [];
          this.results.spots = data.spots || [];

        } catch (error) {
          console.error('Search failed:', error);
          this.results.users = [];
          this.results.lots = [];
          this.results.spots = [];
          alert('Failed to perform search.');
        } finally {
          this.loading = false;
        }
      }
    }
  };
  </script>
