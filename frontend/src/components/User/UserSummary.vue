<template>
  <div class="summary-charts">
    <h3 class="mb-4 text-primary">My Parking Activity</h3>

    <div v-if="loading" class="text-center p-5">
      <div class="spinner-border text-primary" role="status"></div>
      <p class="mt-2 text-muted">Fetching analytics...</p>
    </div>

    <div v-else-if="error" class="alert alert-danger">
      Failed to load data: {{ error }}
    </div>

    <div v-else>
      <div class="row g-4 mb-5">
        
        <div class="col-md-12">
          <div class="card shadow-sm border-primary">
            <div class="card-header bg-primary text-white"><h5>Monthly Spending ($)</h5></div>
            <div class="card-body">
              <canvas id="spendingChart"></canvas>
            </div>
          </div>
        </div>
        
        <div class="col-md-6">
          <div class="card shadow-sm border-success">
            <div class="card-header bg-success text-white"><h5>Favorite Parking Lots (Visits)</h5></div>
            <div class="card-body">
              <canvas id="lotUsageChart"></canvas>
            </div>
          </div>
        </div>

        <div class="col-md-6">
          <div class="card shadow-sm border-info">
            <div class="card-header bg-info text-white"><h5>Total Cost per Lot ($)</h5></div>
            <div class="card-body">
              <canvas id="lotSpendChart"></canvas>
            </div>
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
  name: 'UserSummary',
  data() {
    return {
      data: {
        monthly_spend: [], 
        usage_by_lot: [],
        spend_by_lot: []
      },
      loading: false,
      error: null
    };
  },
  async mounted() {
    await this.fetchSummaryData();
    if (!this.error && !this.loading) {
      this.renderCharts();
    }
  },
  methods: {
    async fetchSummaryData() {
      this.loading = true;
      try {
        const res = await api.get('/user/summary'); 
        this.data = res.data;
      } catch (err) {
        this.error = 'Could not load summary data.';
        console.error(err);
      } finally {
        this.loading = false;
      }
    },
    
    renderCharts() {
      this.renderSpendingChart();
      this.renderLotUsageChart();
      this.renderLotSpendChart();
    },

    renderSpendingChart() {
      if (!this.data.monthly_spend || !this.data.monthly_spend.length) return;

      const labels = this.data.monthly_spend.map(d => d.month);
      const dataPoints = this.data.monthly_spend.map(d => d.amount);

      new Chart(document.getElementById('spendingChart'), {
        type: 'bar',
        data: {
          labels: labels,
          datasets: [{
            label: 'Amount Spent ($)',
            data: dataPoints,
            backgroundColor: 'rgba(54, 162, 235, 0.6)',
            borderColor: 'rgba(54, 162, 235, 1)',
            borderWidth: 1
          }]
        },
        options: { responsive: true, maintainAspectRatio: false }
      });
    },

    renderLotUsageChart() {
      if (!this.data.usage_by_lot || !this.data.usage_by_lot.length) return;

      const labels = this.data.usage_by_lot.map(d => d.lot);
      const dataPoints = this.data.usage_by_lot.map(d => d.count);
      const colors = ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF'];

      new Chart(document.getElementById('lotUsageChart'), {
        type: 'doughnut',
        data: {
          labels: labels,
          datasets: [{
            data: dataPoints,
            backgroundColor: colors.slice(0, labels.length),
            hoverOffset: 4
          }]
        },
        options: { 
          responsive: true, 
          maintainAspectRatio: false,
          plugins: { legend: { position: 'right' } }
        }
      });
    },

    renderLotSpendChart() {
      if (!this.data.spend_by_lot || !this.data.spend_by_lot.length) return;

      const labels = this.data.spend_by_lot.map(d => d.lot);
      const dataPoints = this.data.spend_by_lot.map(d => d.amount);
      const colors = ['#4BC0C0', '#9966FF', '#FF9F40', '#FF6384', '#36A2EB'];

      new Chart(document.getElementById('lotSpendChart'), {
        type: 'bar',
        data: {
          labels: labels,
          datasets: [{
            label: 'Total Paid ($)',
            data: dataPoints,
            backgroundColor: colors.slice(0, labels.length),
            borderWidth: 1
          }]
        },
        options: { 
          responsive: true, 
          maintainAspectRatio: false,
          scales: { y: { beginAtZero: true } }
        }
      });
    }
  }
};
</script>

<style scoped>
#spendingChart, #lotUsageChart, #lotSpendChart { max-height: 300px; }
</style>