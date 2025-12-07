<template>
  <div>
    <div v-if="loading" class="text-center py-4">
        <div class="spinner-border text-primary" role="status"></div>
        <div class="mt-2 text-muted">Loading parking spots...</div>
    </div>

    <div v-else>
      <div class="row g-3">
        <div v-for="spot in spots" :key="spot.id" class="col-md-4 col-lg-3">
            <div class="card h-100 text-center shadow-sm" 
                 :class="spot.status === 'Occupied' ? 'border-danger bg-light-danger' : 'border-success bg-light-success'">
                <div class="card-body">
                    <h5 class="card-title fw-bold">{{ spot.spot_number }}</h5>
                    
                    <div v-if="spot.status === 'Occupied'" class="mt-3">
                        <span class="badge bg-danger mb-2">Occupied</span>
                        <div class="text-start small border-top pt-2">
                            <div><strong>Vehicle:</strong> {{ spot.vehicle }}</div>
                            <div><strong>User:</strong> {{ spot.parked_by }}</div>
                            <div class="text-muted" style="font-size: 0.8rem">Since: {{ spot.since }}</div>
                        </div>
                    </div>
                    
                    <div v-else class="mt-3">
                         <span class="badge bg-success">Available</span>
                         <div class="mt-2 text-muted small">Ready for booking</div>
                    </div>
                </div>
            </div>
        </div>
      </div>

      <div v-if="spots.length === 0" class="alert alert-warning mt-3">
          No spots found for this lot.
      </div>
    </div>
  </div>
</template>

<script>
import api from '@/axios';

export default {
  props: {
    lotId: {
      type: Number,
      required: true
    },
    lotName: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      spots: [],
      loading: false,
    };
  },
  watch: {
    lotId: {
      immediate: true,
      handler() {
        if (this.lotId) {
          this.fetchSpots();
        }
      }
    }
  },
  methods: {
    async fetchSpots() {
      this.loading = true;
      try {
        const res = await api.get(`/admin/lots/${this.lotId}/spots`);
        this.spots = res.data;
      } catch (err) {
        console.error("Failed to load spots:", err);
        alert('Failed to load parking spots.');
      } finally {
        this.loading = false;
      }
    }
  }
};
</script>

<style scoped>
.bg-light-danger {
    background-color: #fff5f5;
}
.bg-light-success {
    background-color: #f0fff4;
}
</style>
