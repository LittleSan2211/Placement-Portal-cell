<template>
  <section class="home">
    <nav-bar />
    <main class="page-content">
      <router-view />
    </main>
  </section>
</template>

<script>
// import LandingPage from '@/components/LandingPage.vue';
import NavBar from '@/components/NavBar.vue';

export default {
  name: "HomeView",
  components: {
    NavBar
  }

};
</script>
<style>
@import "../assets/css/HomeView.css";
/* @import "../assets/css/LoginView.css"; */
</style>
