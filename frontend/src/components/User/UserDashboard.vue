<template>
  <div>
    <div class="container py-4">
      <h2 class="mb-4 text-primary fw-bold">My Parking Dashboard</h2>

      <ul class="nav nav-pills mb-4 nav-fill shadow-sm rounded-3 bg-light p-1">
        <li class="nav-item">
          <a class="nav-link" :class="{ 'active': section === 'home' }" @click.prevent="setSection('home')" href="#">
            <i class="bi bi-house-door me-2"></i>Home
          </a>
        </li>
        <li class="nav-item">
          <a class="nav-link" :class="{ 'active': section === 'history' }" @click.prevent="setSection('history')" href="#">
            <i class="bi bi-clock-history me-2"></i>History
          </a>
        </li>
        <li class="nav-item">
          <a class="nav-link" :class="{ 'active': section === 'summary' }" @click.prevent="setSection('summary')" href="#">
            <i class="bi bi-bar-chart-line me-2"></i>Summary
          </a>
        </li>
        <li class="nav-item">
          <a class="nav-link" :class="{ 'active': section === 'search' }" @click.prevent="setSection('search')" href="#">
            <i class="bi bi-search me-2"></i>Search
          </a>
        </li>
      </ul>

      <div class="tab-content">
        <div v-if="section === 'home'" class="tab-pane active">
          <Home userRole="user" />
        </div>
        
        <div v-if="section === 'history'" class="tab-pane active">
          <BookingHistory />
        </div>
        
        <div v-if="section === 'summary'" class="tab-pane active">
          <UserSummary />
        </div>
        
        <div v-if="section === 'search'" class="tab-pane active">
          <UserSearch @initiate-park="handleSearchPark" />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Home from '../Common/Home.vue';
import BookingHistory from './BookingHistory.vue';
import UserSummary from './UserSummary.vue';
import UserSearch from './UserSearch.vue';

export default {
  components: {
    Home,
    BookingHistory,
    UserSummary,
    UserSearch
  },
  data() {
    return {
      section: 'home',
    };
  },
  methods: {
    setSection(newSection) {
      this.section = newSection;
    },
    handleSearchPark(lot) {
        this.section = 'home';
        alert(`You selected ${lot.name}. Please find it in the list to park.`);
    }
  }
};
</script>

<style scoped>
.container { max-width: 1000px; }
.nav-pills .nav-link { cursor: pointer; }
</style>
