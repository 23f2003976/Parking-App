<template>
  <div class="summary-charts">
    <h3 class="mb-4 text-primary">System Overview & Analytics</h3>

    <div v-if="loading" class="text-center p-5">
      <div class="spinner-border text-primary" role="status"></div>
      <p class="mt-2 text-muted">Fetching dashboard analytics...</p>
    </div>

    <div v-else-if="error" class="alert alert-danger">
      {{ error }}
    </div>

    <div v-else>
      <div class="row g-4 mb-5">
        <div class="col-md-3">
          <div class="card bg-white p-3 shadow-sm border-start border-4 border-primary h-100">
            <h6 class="text-muted text-uppercase mb-2">Total Users</h6>
            <h2 class="fw-bold text-dark">{{ data.total_users }}</h2>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card bg-white p-3 shadow-sm border-start border-4 border-info h-100">
            <h6 class="text-muted text-uppercase mb-2">Total Lots</h6>
            <h2 class="fw-bold text-dark">{{ data.total_lots }}</h2>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card bg-white p-3 shadow-sm border-start border-4 border-success h-100">
            <h6 class="text-muted text-uppercase mb-2">Total Capacity</h6>
            <h2 class="fw-bold text-dark">{{ data.total_capacity }}</h2>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card bg-white p-3 shadow-sm border-start border-4 border-warning h-100">
            <h6 class="text-muted text-uppercase mb-2">Current Occupancy</h6>
            <h2 class="fw-bold text-dark">{{ data.current_occupancy }}</h2>
          </div>
        </div>
      </div>
      
      <div class="row g-4">
        <div class="col-md-8">
          <div class="card p-4 shadow-sm h-100">
            <h5 class="card-title text-primary mb-3">Revenue by Parking Lot</h5>
            <canvas id="revenueChart"></canvas>
          </div>
        </div>

        <div class="col-md-4">
          <div class="card p-4 shadow-sm h-100">
            <h5 class="card-title text-primary mb-3">Bookings Distribution</h5>
            <canvas id="bookingsChart"></canvas>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '@/axios';
import { Chart, registerables } from 'chart.js';
Chart.register(...registerables);

export default {
  name: 'AdminSummary',
  data() {
    return {
      loading: true,
      error: null,
      data: {
        total_users: 0,
        total_lots: 0,
        total_capacity: 0,
        current_occupancy: 0,
        lot_analytics: []
      }
    };
  },
  async mounted() {
    await this.fetchSummaryData();
    if (!this.error && !this.loading) {
      this.$nextTick(() => {
          this.renderCharts();
      });
    }
  },
  methods: {
    async fetchSummaryData() {
      this.loading = true;
      try {
        const res = await api.get('/admin/summary'); 
        this.data = res.data;
      } catch (err) {
        this.error = 'Could not connect to summary endpoint.';
        console.error(err);
      } finally {
        this.loading = false;
      }
    },
    
    renderCharts() {
      const labels = this.data.lot_analytics.map(d => d.name);
      const revenueData = this.data.lot_analytics.map(d => d.revenue);
      const bookingData = this.data.lot_analytics.map(d => d.bookings);

      new Chart(document.getElementById('revenueChart'), {
        type: 'bar',
        data: {
          labels: labels,
          datasets: [{
            label: 'Total Revenue ($)',
            data: revenueData,
            backgroundColor: 'rgba(54, 162, 235, 0.6)',
            borderColor: 'rgba(54, 162, 235, 1)',
            borderWidth: 1
          }]
        },
        options: { responsive: true }
      });

      new Chart(document.getElementById('bookingsChart'), {
        type: 'doughnut',
        data: {
          labels: labels,
          datasets: [{
            data: bookingData,
            backgroundColor: [
              '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF'
            ],
            hoverOffset: 4
          }]
        },
        options: { 
            responsive: true,
            plugins: { legend: { position: 'bottom' } } 
        }
      });
    }
  }
};
</script>
