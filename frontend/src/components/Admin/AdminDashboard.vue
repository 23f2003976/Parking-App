<template>
  <div>
    <div class="container py-4">
      <h2 class="mb-4 text-primary fw-bold">Parking Admin Dashboard</h2>

      <ul class="nav nav-pills mb-4 nav-fill shadow-sm rounded-3 bg-light p-1">
        <li class="nav-item">
          <a class="nav-link" :class="{ 'active': section === 'home' }" @click.prevent="setSection('home')" href="#">
            <i class="bi bi-house-door me-2"></i>Home
          </a>
        </li>
        <li class="nav-item">
          <a class="nav-link" :class="{ 'active': ['lots', 'spots'].includes(section) }" @click.prevent="setSection('lots')" href="#">
            <i class="bi bi-p-square me-2"></i>Parking Lots
          </a>
        </li>
        <li class="nav-item">
          <a class="nav-link" :class="{ 'active': section === 'search' }" @click.prevent="setSection('search')" href="#">
            <i class="bi bi-search me-2"></i>Search
          </a>
        </li>
        <li class="nav-item">
          <a class="nav-link" :class="{ 'active': section === 'summary' }" @click.prevent="setSection('summary')" href="#">
            <i class="bi bi-bar-chart-line me-2"></i>Analytics
          </a>
        </li>
      </ul>

      <div class="tab-content">
        <div v-if="section === 'home'" class="tab-pane active">
          <Home :userRole="userRole" :username="username" />
        </div>
        
        <div v-if="section === 'search'" class="tab-pane active">
          <SearchManager />
        </div>

        <div v-if="section === 'summary'" class="tab-pane active">
          <AdminSummary />
        </div>

        <div v-if="section === 'lots' || section === 'spots'" class="tab-pane active">
          
          <div v-if="section === 'spots'" class="d-flex justify-content-between align-items-center mb-3">
              <h4 class="mb-0">
                  Spots in Lot: <span class="badge bg-primary">{{ selectedLot.name }}</span>
              </h4>
              <button @click.prevent="setSection('lots')" class="btn btn-outline-secondary">
                  &larr; Back to Lots
              </button>
          </div>
          
          <LotManager v-if="section === 'lots'" @open-spots="openSpots" />
          
          <SpotManager v-else-if="section === 'spots'"
            :lotId="selectedLot.id" 
            :lotName="selectedLot.name"
            @back-to-lots="setSection('lots')"/>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Home from '../Common/Home.vue' 
import LotManager from './LotManager.vue'
import SpotManager from './SpotManager.vue'
import SearchManager from './SearchManager.vue' 
import AdminSummary from './AdminSummary.vue'

export default {
  components: {
    Home,
    LotManager,
    SpotManager,
    SearchManager, 
    AdminSummary
  },
  data() {
    return {
      section: 'home',
      selectedLot: { id: null, name: '' },
      
      userRole: 'admin', 
      username: '',
    }
  },
  mounted() {
    this.loadAuthData(); 
  },
  methods: {
    loadAuthData() {
      const authDataJson = localStorage.getItem('qm_auth');
      if (authDataJson) {
        try {
          const authData = JSON.parse(authDataJson);
          if (authData && authData.user) {
            this.userRole = authData.user.role || 'user';
            this.username = authData.user.username || 'User';
          }
        } catch (e) {
          console.error('Error parsing auth data', e);
        }
      }
    },
    
    setSection(newSection) {
      if (newSection === 'home' || newSection === 'summary' || newSection === 'search') { 
        this.selectedLot = { id: null, name: '' };
      }
      this.section = newSection;
    },
    
    openSpots(lot) {
      this.selectedLot = { id: lot.id, name: lot.name };
      this.section = 'spots'; 
    }
  }
}
</script>

<style scoped>
.container {
  max-width: 1100px;
}
</style>
