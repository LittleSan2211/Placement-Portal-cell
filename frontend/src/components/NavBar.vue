<template>
    <div>
        <nav class="nav homenav">
            <div class="logoIITm"> 
                <img src="../assets/clglogo.png" />
            </div>
            <div class="navSection">
                <ul>
                    <li class="navList" :class="{
                        'bottom-line': activeLink === 'home',
                    }" @click="activeLink = 'home'">
                        <router-link to="/" class="link-section">Home</router-link>
                    </li>
                    <li class="navList" :class="{ 'bottom-line': activeLink === 'about' }"
                        @click="activeLink = 'about'">
                        <router-link to="#about" class="link-section">About</router-link>
                    </li>
                    <li :class="{ 'bottom-line': activeLink === 'userSection' }" @click="activeLink = 'userSection'">
                        <router-link to="#userSection" class="link-section">User section</router-link>
                    </li>
                    <li class="navList" :class="{ 'bottom-line': activeLink === 'support' }"
                        @click="activeLink = 'support'">
                        <router-link to="#" class="link-section">Support</router-link>
                    </li>
                    <li class="navList" :class="{ 'bottom-line': activeLink === 'contact' }"
                        @click="activeLink = 'contact'">
                        <router-link to="#" class="link-section">Contact</router-link>
                    </li>
                </ul>
            </div>
            <div class="leftCorner">
                <div class="navIcon">
                    <i class="bi bi-person-circle user-icon"></i>
                    <i class="bi bi-caret-down-fill dropdown-icon"></i>
                </div>
                <div class="enterySection">
                    <router-link to="login">
                        <button class="btn login">Join Us / Login</button>
                    </router-link>
                </div>
            </div>
        </nav>
    </div>
</template>
<script>
export default {
    name : "NavBar",
    data() {
    return {
      activeLink: 'home',
    };
  },
}
</script>