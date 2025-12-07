<template>
  <div class="container py-4">
    <div class="alert alert-light border shadow-sm mb-4 d-flex justify-content-between align-items-center">
      <h3 class="mb-0 text-primary">Welcome, {{ username || 'Guest' }}!</h3>
      <span class="badge bg-secondary">{{ userRole === 'admin' ? 'Administrator' : 'Driver' }}</span>
    </div>

    <div v-if="userRole === 'admin'">
      <div class="alert alert-info mb-4">
        Use the tabs above to manage Parking Lots and Monitor Spots.
      </div>
      <div>
        <div class="row g-4">
          <div class="col-md-6">
            <div class="card shadow-sm border-primary h-100">
              <div class="card-header bg-primary text-white"><h5>🅿️ Managed Parking Lots</h5></div>
              <div class="card-body">
                <div v-if="loading.lots" class="text-muted">Loading...</div>
                <ul v-else-if="lots.length" class="list-group list-group-flush">
                  <li v-for="l in lots" :key="l.id" class="list-group-item d-flex justify-content-between">
                    <span class="fw-bold">{{ l.name }}</span>
                    <span class="badge bg-success">{{ l.capacity }} Spots</span>
                  </li>
                </ul>
                <div v-else class="text-muted">No lots created.</div>
              </div>
            </div>
          </div>
          <div class="col-md-6">
            <div class="card shadow-sm border-primary h-100">
              <div class="card-header bg-primary text-white"><h5>Top 10 Drivers</h5></div>
              <div class="card-body">
                <div v-if="loading.users" class="text-muted">Loading...</div>
                <ul v-else-if="users.length" class="list-group list-group-flush">
                  <li v-for="u in users" :key="u.id" class="list-group-item d-flex justify-content-between">
                    <span class="fw-bold">{{ u.name }}</span>
                  </li>
                </ul>
                <div v-else class="text-muted">No one has enrolled a slot yet.</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="mt-4">
        
      <div v-if="activeSession" class="card shadow-lg mb-5 border-success">
          <div class="card-header bg-success text-white">
              <h4 class="mb-0"><i class="bi bi-car-front-fill me-2"></i> Active Parking Session</h4>
          </div>
          <div class="card-body text-center p-5">
              <h2 class="display-4 fw-bold text-success">{{ activeSession.lot_name }}</h2>
              <p class="lead">Spot: <strong>{{ activeSession.spot }}</strong> | Vehicle: <strong>{{ activeSession.vehicle }}</strong></p>
              
              <div class="my-4 p-3 bg-light rounded d-inline-block">
                  <h5 class="text-muted">Duration</h5>
                  <h3 class="text-dark font-monospace">{{ sessionDuration }}</h3>
              </div>

              <div class="mt-3">
                  <button class="btn btn-danger btn-lg px-5" @click="unparkVehicle" :disabled="loading.parkingAction">
                      {{ loading.parkingAction ? 'Processing...' : 'Unpark & Pay' }}
                  </button>
              </div>
          </div>
      </div>

      <div class="card shadow-lg">
        <div class="card-header bg-primary text-white">
          <h4 class="mb-0">🅿️ Available Parking Lots</h4>
        </div>
        <div class="card-body p-0">
          <div v-if="loading.lots" class="text-center py-5">
            <div class="spinner-border text-primary" role="status"></div>
            <p class="mt-2">Finding spots...</p>
          </div>
          <div v-else-if="lots.length === 0" class="alert alert-light text-center mb-0">
            No parking lots available at the moment.
          </div>
          <div v-else class="table-responsive">
            <table class="table table-hover mb-0 align-middle">
              <thead class="table-light">
                <tr>
                    <th>Lot Name</th>
                    <th>Location</th>
                    <th>Rate/Hr</th>
                    <th>Availability</th>
                    <th>Action</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="lot in lots" :key="lot.id">
                    <td class="fw-bold">{{ lot.name }}</td>
                    <td>{{ lot.location }}</td>
                    <td>${{ lot.rate }}</td>
                    <td>
                        <span class="badge" :class="lot.available_spots > 0 ? 'bg-success' : 'bg-danger'">
                            {{ lot.available_spots }} Spots Free
                        </span>
                    </td>
                    <td>
                        <button class="btn btn-sm btn-primary" 
                            :disabled="lot.available_spots === 0 || activeSession"
                            @click="openParkModal(lot)">
                            {{ activeSession ? 'Unavailable' : 'Park Here' }}
                        </button>
                    </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <div class="d-flex justify-content-end mt-4">
          <button class="btn btn-outline-secondary" @click="downloadCsv">
              <i class="bi bi-download me-1"></i> Download History CSV
          </button>
      </div>

      <div v-if="showParkModal" class="modal-backdrop">
        <div class="modal-dialog modal-dialog-centered">
          <div class="modal-content">
            <div class="modal-header bg-primary text-white">
              <h5 class="modal-title">Park at {{ selectedLot.name }}</h5>
              <button type="button" class="btn-close btn-close-white" @click="showParkModal = false"></button>
            </div>
            <form @submit.prevent="parkVehicle">
                <div class="modal-body">
                    <div class="mb-3">
                        <label class="form-label">Vehicle Number</label>
                        <input v-model="vehicleNumber" class="form-control" placeholder="e.g. ABC-1234" required />
                    </div>
                    <p class="text-muted small"><i class="bi bi-info-circle"></i> Spot will be allocated automatically upon confirmation.</p>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" @click="showParkModal = false">Cancel</button>
                    <button type="submit" class="btn btn-success" :disabled="loading.parkingAction">Confirm Parking</button>
                </div>
            </form>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script>
import api from '@/axios';

export default {
  props: {
    userRole: { type: String, default: 'user' },
    username: { type: String, default: 'User' }
  },
  data() {
    return {
      lots: [],
      users: [],
      activeSession: null,
      sessionTimer: null,
      sessionDuration: '00:00:00',
      
      loading: {
        lots: false,
        parkingAction: false,
        users: false
      },
      
      showParkModal: false,
      selectedLot: null,
      vehicleNumber: '',
    };
  },
  mounted() {
    if (this.userRole === 'admin') {
      this.fetchAdminLots();
      this.fetch10Users();
    } else {
      this.fetchUserLots();
      this.checkActiveSession();
    }
  },
  beforeUnmount() {
      if (this.sessionTimer) clearInterval(this.sessionTimer);
  },
  methods: {
    async fetchAdminLots() { 
        this.loading.lots = true;
        try {
            const res = await api.get('/admin/lots'); 
            this.lots = res.data || [];
        } catch (e) { console.error(e); } finally { this.loading.lots = false; }
    },
     async fetch10Users() { 
        this.loading.users = true;
        try {
            const res = await api.get('/admin/users/10'); 
            this.users = res.data || [];
        } catch (e) { console.error(e); } finally { this.loading.users = false; }
    },
    async fetchUserLots() { 
        this.loading.lots = true;
        try {
            const res = await api.get('/user/lots'); 
            this.lots = res.data || [];
        } catch (e) { console.error(e); } finally { this.loading.lots = false; }
    },
    
    async checkActiveSession() {
        try {
            const res = await api.get('/user/history');
            const history = res.data || [];
            const active = history.find(s => s.status === 'ACTIVE');
            
            if (active) {
                this.activeSession = active;
                this.startTimer(active.entry);
            } else {
                this.activeSession = null;
            }
        } catch (e) { console.error("Session check failed", e); }
    },

    startTimer(startTimeStr) {
        if (this.sessionTimer) clearInterval(this.sessionTimer);
        const sanitized = startTimeStr.replace(/\.\d{3,}Z$/, m => m.slice(0, 4) + 'Z');
        const start = Date.parse(sanitized);
        
        this.sessionTimer = setInterval(() => {
            const now = new Date().getTime();
            const diff = now - start;
            
            const hrs = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            const mins = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
            const secs = Math.floor((diff % (1000 * 60)) / 1000);
            
            this.sessionDuration = `${String(hrs).padStart(2,'0')}:${String(mins).padStart(2,'0')}:${String(secs).padStart(2,'0')}`;
        }, 1000);
    },

    openParkModal(lot) {
        this.selectedLot = lot;
        this.vehicleNumber = '';
        this.showParkModal = true;
    },

    async parkVehicle() {
        if (!this.vehicleNumber) return;
        this.loading.parkingAction = true;
        try {
            await api.post('/user/park', {
                lot_id: this.selectedLot.id,
                vehicle_number: this.vehicleNumber
            });
            
            this.showParkModal = false;
            await this.fetchUserLots();
            await this.checkActiveSession();
            alert("Parking Successful!");
        } catch (err) {
            alert(err.response?.data?.error || 'Parking failed');
        } finally {
            this.loading.parkingAction = false;
        }
    },

    async unparkVehicle() {
        if (!confirm("Are you sure you want to unpark? Charges will apply.")) return;
        this.loading.parkingAction = true;
        try {
            const res = await api.post('/user/unpark');
            const { amount_paid, duration_hours } = res.data;
            
            alert(`Vehicle Unparked!\nDuration: ${duration_hours} hrs\nAmount Paid: $${amount_paid}`);
            
            this.activeSession = null;
            if (this.sessionTimer) clearInterval(this.sessionTimer);
            this.fetchUserLots();
        } catch (err) {
            alert(err.response?.data?.error || 'Unparking failed');
        } finally {
            this.loading.parkingAction = false;
        }
    },

    async downloadCsv() {
        try {
            const res = await api.post('/user/export/trigger');
            alert(res.data.message || 'Export started. Check your email.');
        } catch (e) {
            alert('Export failed.');
        }
    }
  }
};
</script>

<style scoped>
.modal-backdrop {
  position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  background-color: rgba(0,0,0,0.5); z-index: 1050;
  display: flex; align-items: center; justify-content: center;
}
.modal-dialog { width: 100%; max-width: 500px; }
.modal-content { background: white; border-radius: 0.5rem; }
.modal-header,.modal-body, .modal-footer {padding : 2%;}
.modal-footer {justify-content: space-between;}
</style>
