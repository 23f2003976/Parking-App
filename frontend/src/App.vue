<template>
  <div>
    <Nav />
    
    <div class="container mt-4">
      <router-view />
    </div>
  </div>
</template>

<script>
import Nav from './components/Common/Nav.vue'; 

export default {
  name: 'App',
  components: {
    Nav
  }
}
</script>