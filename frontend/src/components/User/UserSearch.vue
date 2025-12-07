<template>
    <div class="search-component card shadow-sm p-4">
      <h4 class="card-title mb-4 text-primary">Search Parking</h4>
  
      <div class="input-group mb-4">
        <input 
          type="text" 
          class="form-control form-control-lg" 
          placeholder="Search parking lots or location..." 
          v-model="query"
          @keyup.enter="performSearch"
        >
        <button class="btn btn-primary btn-lg" type="button" @click="performSearch" :disabled="loading || !query.trim()">
          <span v-if="loading" class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
          {{ loading ? 'Searching...' : 'Search' }}
        </button>
      </div>
  
      <div v-if="!loading && searchExecuted" class="mt-4">
        <div v-if="totalResults === 0" class="alert alert-warning">
          No results found matching <strong>"{{ lastQuery }}"</strong>.
        </div>
  
        <div v-else>
          <h5 class="mb-3">Results for <strong>"{{ lastQuery }}"</strong> ({{ totalResults }})</h5>
  
          <div v-if="results.lots.length" class="mb-4">
            <h6><i class="bi bi-geo-alt-fill me-1 text-success"></i> Parking Lots ({{ results.lots.length }})</h6>
            <ul class="list-group list-group-flush border rounded-3">
              <li v-for="lot in results.lots" :key="'lot-' + lot.id" class="list-group-item d-flex justify-content-between align-items-center">
                <div>
                  <span class="fw-bold">{{ lot.name }}</span>
                  <div class="small text-muted">{{ lot.location }}</div>
                </div>
                <button @click="$emit('initiate-park', lot)" class="btn btn-sm btn-outline-success">
                  Park Here
                </button>
              </li>
            </ul>
          </div>
  
          <div v-if="results.history.length" class="mb-4">
            <h6><i class="bi bi-clock-history me-1 text-info"></i> Past Bookings ({{ results.history.length }})</h6>
            <ul class="list-group list-group-flush border rounded-3">
              <li v-for="sess in results.history" :key="'sess-' + sess.id" class="list-group-item d-flex justify-content-between align-items-center">
                <div>
                  <span class="fw-bold">{{ sess.lot_name }}</span>
                  <div class="small text-muted">{{ sess.entry_time }}</div>
                </div>
                <div>
                  <span class="badge bg-primary me-3">${{ sess.amount }}</span>
                  <span class="badge bg-secondary">{{ sess.vehicle }}</span>
                </div>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import api from '@/axios';
  
  export default {
    name: "UserSearch",
    emits: ['initiate-park'],
    data() {
      return {
        query: '',
        lastQuery: '',
        loading: false,
        searchExecuted: false,
        results: {
          lots: [],
          history: [],
        },
      };
    },
    computed: {
      totalResults() {
        return this.results.lots.length + this.results.history.length;
      }
    },
    methods: {
      async performSearch() {
        if (!this.query.trim()) return;
  
        this.loading = true;
        this.searchExecuted = true;
        this.lastQuery = this.query.trim();
  
        try {
          const response = await api.get('/user/search', {
            params: { q: this.query.trim() }
          });
  
          const data = response.data;
          this.results.lots = data.lots || [];
          this.results.history = data.history || []; 
  
        } catch (error) {
          console.error('Search failed:', error);
          this.results.lots = [];
          this.results.history = [];
        } finally {
          this.loading = false;
        }
      }
    }
  };
  </script>
