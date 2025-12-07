<template>
  <div class="container py-5 text-center">
    <div v-if="loading" class="spinner-border text-primary"></div>
    
    <div v-else-if="!session" class="alert alert-warning">
        No active parking session found. <router-link to="/user">Go to Dashboard</router-link>
    </div>

    <div v-else class="card shadow-lg border-success mx-auto" style="max-width: 600px;">
        <div class="card-header bg-success text-white py-3">
            <h3 class="mb-0">Active Parking</h3>
        </div>
        <div class="card-body p-5">
            <div class="mb-4">
                <h5 class="text-muted">Parking Lot</h5>
                <h2>{{ session.lot_name }}</h2>
            </div>
            
            <div class="row mb-4">
                <div class="col-6">
                    <h5 class="text-muted">Spot</h5>
                    <h3>{{ session.spot }}</h3>
                </div>
                <div class="col-6">
                    <h5 class="text-muted">Vehicle</h5>
                    <h3>{{ session.vehicle }}</h3>
                </div>
            </div>

            <hr>

            <div class="my-4">
                <h1 class="display-3 font-monospace text-success">{{ duration }}</h1>
                <p class="text-muted">Elapsed Time</p>
            </div>

            <button class="btn btn-danger btn-lg w-100" @click="unpark">
                Unpark Vehicle
            </button>
        </div>
    </div>
  </div>
</template>

<script>
import api from '@/axios';

export default {
    data() {
        return {
            session: null,
            loading: true,
            timer: null,
            duration: '00:00:00'
        }
    },
    async created() {
        try {
            const res = await api.get('/user/history');
            const active = res.data.find(s => s.status === 'ACTIVE');
            if (active) {
                this.session = active;
                this.startTimer(active.entry);
            }
        } catch (e) { console.error(e); } finally { this.loading = false; }
    },
    beforeUnmount() { if (this.timer) clearInterval(this.timer); },
    methods: {
        startTimer(startStr) {
            if (!startStr) {
                return;
            }
            const sanitized = startStr.replace(/\.\d{3,}Z$/, m => m.slice(0, 4) + 'Z');
            const start = Date.parse(sanitized);

            this.timer = setInterval(() => {
                const diff = Date.now() - start;
                const hrs = Math.floor(diff / 3600000);
                const mins = Math.floor((diff % 3600000) / 60000);
                const secs = Math.floor((diff % 60000) / 1000);
                this.duration = `${hrs.toString().padStart(2,'0')}:${mins.toString().padStart(2,'0')}:${secs.toString().padStart(2,'0')}`;
            }, 1000);
        },
        async unpark() {
            if(!confirm("Unpark now?")) return;
            try {
                await api.post('/user/unpark');
                this.$router.push('/user');
            } catch(e) { alert('Error unparking'); }
        }
    }
}
</script>
