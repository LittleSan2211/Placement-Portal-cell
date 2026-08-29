<template>
    <div class="login-portal-wrapper">
        <!-- Background decorative blobs for premium feel -->
        <div class="glow-blob blob-1"></div>
        <div class="glow-blob blob-2"></div>

        <div class="login-center-card">
            <!-- Left Side: University Branding Context -->
            <div class="branding-panel">
                <div class="brand-header">
                    <div class="brand-icon-box">
                        <i class="bi bi-mortarboard-fill"></i>
                    </div>
                    <h2>PS Placement</h2>
                </div>
                
                <div class="branding-hero-text">
                    <h1>Empowering Brightest Minds</h1>
                    <p>Connect with top-tier global opportunities and streamline your professional journey through our unified institutional platform.</p>
                </div>

                <div class="branding-stats-row">
                    <div class="stat-pill">
                        <h3>500+</h3>
                        <p>Partners</p>
                    </div>
                    <div class="stat-pill">
                        <h3>98%</h3>
                        <p>Placed</p>
                    </div>
                </div>
            </div>

            <!-- Right Side: Clean Modern Form -->
            <div class="form-panel">
                <div class="form-header-area">
                    <h3>Welcome Back</h3>
                    <p>Sign in to unlock your secure placement dashboard.</p>
                </div>

                <form @submit.prevent="loginUser()" class="modern-login-form">
                    <!-- Dynamic Error Box -->
                    <div v-if="serverMessage" class="modern-error-alert">
                        <i class="bi bi-exclamation-circle-fill"></i>
                        <span>{{ serverMessage }}</span>
                    </div>

                    <!-- Input Email -->
                    <div class="input-field-group">
                        <label for="email">Institutional Email ID</label>
                        <div class="input-with-icon">
                            <i class="bi bi-envelope"></i>
                            <input type="text" v-model="email" id="email" placeholder="username@ds.study.iitm.ac.in" name="email">
                        </div>
                    </div>
                    
                    <!-- Input Password -->
                    <div class="input-field-group">
                        <label for="password">Account Password</label>
                        <div class="input-with-icon">
                            <i class="bi bi-lock"></i>
                            <input type="password" v-model="password" id="password" name="password" placeholder="••••••••">
                        </div>
                    </div>
                    
                    <!-- Action Options Row -->
                    <div class="form-actions-flex-row">
                        <label class="modern-checkbox-label">
                            <input type="checkbox" v-model="checkbox" id="checkbox" name="checkbox">
                            <span class="checkmark-text">Remember me</span>
                        </label>
                        <span class="forgot-pass-trigger">Forgot password?</span>
                    </div>
                    
                    <!-- Action Button -->
                    <button class="submit-portal-btn">
                        <span>Sign In</span>
                        <i class="bi bi-arrow-right-short"></i>
                    </button>
                    
                    <div class="form-footer-divider">
                        <span>or</span>
                    </div>

                    <p class="register-navigation-text">
                        New candidate? <router-link to="/register">Create an account</router-link>
                    </p>
                </form>
            </div>
        </div>
    </div>
</template>

<script>
import axios from 'axios';
export default {
    name: "LoginView",
    data() {
        return {
            email: "",
            password: "",
            checkbox: "",
            serverMessage: "" 
        }
    },
    methods : {
        async loginUser() {
            try {
                this.serverMessage = "";

                const res = await axios.post("auth/login", {
                    "email": this.email,
                    "password": this.password 
                },
                {
                    withCredentials: true
                });

                localStorage.setItem('accessToken', res.data.accessToken);
                const role = res.data.role;

                if (role === 'Admin' ){
                    this.$router.push('/admin-dashboard');
                } else if (role === 'Company') {
                    this.$router.push('/company-dashboard');
                } else {
                    this.$router.push("/student");
                }
            }
            catch (err) {
                if (err.response && err.response.data && err.response.data.message) {
                    this.serverMessage = err.response.data.message; 
                } else if (err.response && err.response.data && err.response.data.error) {
                    this.serverMessage = err.response.data.error; 
                } else {
                    this.serverMessage = "Network or Server Error. Please try again.";
                }
            }
        }
    }
}
</script>

<style>
@import "../assets/css/LoginView.css";
</style>