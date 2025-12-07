<template>
  <div class="card shadow-sm p-4">
    <h4 class="card-title mb-4 text-primary">Parking History</h4>
    
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-info" role="status"></div>
      <p class="mt-2">Loading history...</p>
    </div>

    <div v-else-if="sessions.length === 0" class="alert alert-warning mb-0">
      You haven't parked with us yet.
    </div>
    
    <div v-else class="table-responsive">
        <table class="table table-hover">
            <thead class="table-light">
                <tr>
                    <th>Lot</th>
                    <th>Spot</th>
                    <th>Vehicle</th>
                    <th>In Time</th>
                    <th>Out Time</th>
                    <th>Fee</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="s in sessions" :key="s.id">
                    <td class="fw-bold">{{ s.lot_name }}</td>
                    <td><span class="badge bg-secondary">{{ s.spot }}</span></td>
                    <td>{{ s.vehicle }}</td>
                    <td class="small">{{ formatTime(s.entry) }}</td>
                    <td class="small">{{ s.exit === 'Active' ? 'Active' : formatTime(s.exit) }}</td>
                    <td>
                        <span v-if="s.status === 'COMPLETED'" class="badge bg-success">${{ s.amount }}</span>
                        <span v-else class="badge bg-warning text-dark">Active</span>
                    </td>
                </tr>
            </tbody>
        </table>
    </div>
  </div>
</template>

<script>
import api from '@/axios';

export default {
  data() {
    return { 
      sessions: [],
      loading: false
    } 
  },
  created() { 
    this.loadHistory(); 
  },
  methods: {
    async loadHistory() {
      this.loading = true;
      try {
        const res = await api.get('/user/history');
        this.sessions = res.data || [];
      } catch (error) {
        console.error('Failed to load history:', error);
      } finally {
        this.loading = false;
      }
    },
    formatTime(dateStr) {
        if (!dateStr) return '-';
        const date = new Date(dateStr);
        return date.toLocaleString('en-US', { 
            month: 'short', 
            day: 'numeric', 
            hour: '2-digit', 
            minute: '2-digit' 
        });
    }
  }
}
</script>
