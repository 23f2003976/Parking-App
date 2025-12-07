<template>
    <div>
      <div class="d-flex justify-content-between align-items-center mb-3">
        <h4 class="mb-0"> Parking Lots Management </h4>
        <button class="btn btn-primary ms-auto" @click="showCreateModal = true">+ Add Parking Lot</button>
      </div>
  
      <div v-if="showCreateModal" class="card p-4 mb-3 border-primary shadow-sm">
          <h5 class="card-title text-primary mb-3">Create New Parking Lot</h5>
          <form class="row g-3" @submit.prevent="createLot">
            <div class="col-md-6">
              <label class="form-label">Lot Name</label>
              <input v-model="newLot.name" class="form-control" placeholder="e.g. Downtown Garage" required />
            </div>
            <div class="col-md-6">
              <label class="form-label">Location</label>
              <input v-model="newLot.location" class="form-control" placeholder="e.g. 1st Avenue" required />
            </div>
            <div class="col-md-4">
              <label class="form-label">Capacity (Spots)</label>
              <input type="number" v-model="newLot.capacity" class="form-control" min="1" required />
              <div class="form-text">Spots are auto-generated.</div>
            </div>
            <div class="col-md-4">
              <label class="form-label">Rate per Hour ($)</label>
              <input type="number" v-model="newLot.rate_per_hour" class="form-control" step="0.5" min="0" required />
            </div>
            
            <div class="col-12 d-flex gap-2 justify-content-end mt-3">
              <button type="button" class="btn btn-secondary" @click="showCreateModal = false">Cancel</button>
              <button type="submit" class="btn btn-primary">Create Lot</button>
            </div>
          </form>
      </div>
  
      <div v-if="loading" class="text-muted text-center py-4">Loading parking lots...</div>
      <div v-else>
        <div v-if="lots.length === 0" class="alert alert-info">No parking lots found. Create one to get started.</div>
  
        <div v-for="lot in lots" :key="lot.id" class="card mb-3 shadow-sm border-0">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-start">
                <div class="w-75">
                    <div v-if="!lot.editing">
                        <h5 class="card-title fw-bold text-dark">{{ lot.name }}</h5>
                        <p class="mb-1 text-muted"><i class="bi bi-geo-alt-fill"></i> {{ lot.location }}</p>
                        <div class="d-flex gap-3 mt-2">
                           <span class="badge bg-light text-dark border">Capacity: {{ lot.capacity }}</span>
                           <span class="badge bg-light text-dark border">Rate: ${{ lot.rate }}/hr</span>
                           <span class="badge" :class="lot.available > 0 ? 'bg-success' : 'bg-danger'">
                             Available: {{ lot.available }}
                           </span>
                        </div>
                    </div>
                    <div v-else class="row g-2">
                        <div class="col-md-6">
                            <label class="small text-muted">Name</label>
                            <input v-model="lot.name" class="form-control form-control-sm" />
                        </div>
                        <div class="col-md-6">
                            <label class="small text-muted">Location</label>
                            <input v-model="lot.location" class="form-control form-control-sm" />
                        </div>
                        <div class="col-md-4">
                             <label class="small text-muted">Rate ($)</label>
                             <input v-model="lot.rate" type="number" step="0.5" class="form-control form-control-sm" />
                        </div>
                        <div class="col-12 text-muted small">
                            Note: Capacity cannot be changed after creation.
                        </div>
                    </div>
                </div>
                
                <div class="d-flex flex-column gap-2">
                    <button v-if="!lot.editing" class="btn btn-sm btn-info text-white" @click.stop="$emit('open-spots', lot)">
                        View Spots
                    </button>
                    
                    <div class="d-flex gap-2">
                        <template v-if="!lot.editing">
                            <button class="btn btn-sm btn-outline-primary" @click.stop="enableEdit(lot)">Edit</button>
                            <button class="btn btn-sm btn-outline-danger" @click.stop="deleteLot(lot.id)">Delete</button>
                        </template>
                        <template v-else>
                            <button class="btn btn-sm btn-success" @click.stop="saveLot(lot)">Save</button>
                            <button class="btn btn-sm btn-secondary" @click.stop="cancelEdit(lot)">Cancel</button>
                        </template>
                    </div>
                </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import api from '@/axios';
  
  export default {
      name: "LotManager",
      emits: ['open-spots'],
      data() {
          return {
              lots: [],
              loading: false,
              showCreateModal: false,
              newLot: {
                  name: '',
                  location: '',
                  capacity: 10,
                  rate_per_hour: 5.0
              }
          };
      },
      created() {
          this.fetch();
      },
      methods: {
          async fetch() {
              this.loading = true;
              try {
                  const res = await api.get('/admin/lots'); 
                  this.lots = res.data.map(l => ({ 
                      ...l, 
                      editing: false 
                  })) || [];
              } catch (err) {
                  console.error("Failed to load lots:", err);
              } finally {
                  this.loading = false;
              }
          },
          async createLot() {
              if (!this.newLot.name || !this.newLot.capacity) return;
              try {
                  await api.post('/admin/lots', this.newLot);
                  this.newLot = { name: '', location: '', capacity: 10, rate_per_hour: 5.0 };
                  this.showCreateModal = false;
                  this.fetch();
              } catch (err) {
                  console.error(err);
                  alert(err.response?.data?.error || 'Failed to create lot');
              }
          },
          enableEdit(lot) { 
              lot._orig = { ...lot };
              lot.editing = true; 
          },
          cancelEdit(lot) {
              Object.assign(lot, lot._orig);
              lot.editing = false;
          },
          async saveLot(lot) {
              try {
                  await api.put(`/admin/lots/${lot.id}`, { 
                      name: lot.name, 
                      location: lot.location,
                      rate_per_hour: lot.rate
                  });
                  lot.editing = false;
              } catch (err) {
                  console.error(err);
                  alert(err.response?.data?.error || 'Failed to update lot');
              }
          },
          async deleteLot(id) {
              if (!confirm('Are you sure? Lots can only be deleted if empty.')) return;
              try {
                  await api.delete(`/admin/lots/${id}`);
                  this.fetch();
              } catch (err) {
                  console.error(err);
                  alert(err.response?.data?.error || 'Failed to delete lot');
              }
          }
      }
  }
  </script>
