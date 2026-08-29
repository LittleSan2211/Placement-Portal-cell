<template>
    <div class="register-portal-wrapper">
        <!-- Decorative Ambient Background Blobs -->
        <div class="portal-glow-blur blob-1"></div>
        <div class="portal-glow-blur blob-2"></div>

        <div class="register-master-card">
            <!-- Institutional Card Header -->
            <div class="register-card-header">
                <div class="reg-brand-node">
                    <div class="reg-icon-box">
                        <i class="bi bi-mortarboard-fill"></i>
                    </div>
                    <h2>PS Placement Cell</h2>
                </div>
                <h1>Create Institutional Account</h1>
                <p>Join the secure placement automation and corporate recruitment network.</p>
            </div>

            <!-- Role Selection Tabs Block -->
            <div class="reg-role-tabs-container">
                <button type="button" class="reg-tab-trigger" :class="{ active: role === 'Student' }" @click="changeRole('Student')">
                    <i class="bi bi-mortarboard"></i> Candidate Student
                </button>
                <button type="button" class="reg-tab-trigger" :class="{ active: role === 'Company' }" @click="changeRole('Company')">
                    <i class="bi bi-building"></i> Corporate Recruiter
                </button>
            </div>

            <!-- Registration Form Area -->
            <form @submit.prevent="registerUser()" class="reg-modern-form-body">
                
                <!-- Server Response Alerts -->
                <div v-if="serverMessage" :class="['reg-alert-node', { 'reg-success-node': isSuccess }]">
                    <i :class="isSuccess ? 'bi bi-check-circle-fill' : 'bi bi-exclamation-circle-fill'"></i>
                    <span>{{ serverMessage }}</span>
                </div>

                <!-- Two-Column Grid Content -->
                <div class="reg-fields-grid">
                    <!-- Username -->
                    <div class="reg-input-group">
                        <label for="username">Account Username</label>
                        <div class="reg-field-container">
                            <i class="bi bi-person"></i>
                            <input type="text" v-model="username" id="username" placeholder="e.g., kashyap_hori" required>
                        </div>
                    </div>

                    <!-- Email -->
                    <div class="reg-input-group">
                        <label for="email">Registered Email ID</label>
                        <div class="reg-field-container">
                            <i class="bi bi-envelope"></i>
                            <input type="email" v-model="email" id="email" placeholder="name@domain.com" required>
                        </div>
                    </div>

                    <!-- Password -->
                    <div class="reg-input-group">
                        <label for="password">Access Password</label>
                        <div class="reg-field-container">
                            <i class="bi bi-lock"></i>
                            <input type="password" v-model="password" id="password" placeholder="••••••••••••" required>
                        </div>
                    </div>

                    <!-- Confirm Password -->
                    <div class="reg-input-group">
                        <label for="confirm_password">Confirm Password</label>
                        <div class="reg-field-container">
                            <i class="bi bi-shield-lock"></i>
                            <input type="password" v-model="confirm_password" id="confirm_password" placeholder="••••••••••••" required>
                        </div>
                    </div>

                    <!-- Dynamic Name Label -->
                    <div class="reg-input-group">
                        <label for="full_name">{{ role === 'Student' ? 'Candidate Full Name' : 'Company / HR Name' }}</label>
                        <div class="reg-field-container">
                            <i class="bi bi-person-badge"></i>
                            <input type="text" v-model="full_name" id="full_name" :placeholder="role === 'Student' ? 'e.g., Hori Kashyap' : 'e.g., Tech Company HR'" required>
                        </div>
                    </div>

                    <!-- Contact -->
                    <div class="reg-input-group">
                        <label for="contact">Contact Number</label>
                        <div class="reg-field-container">
                            <i class="bi bi-telephone"></i>
                            <input type="text" v-model="contact" id="contact" placeholder="e.g., 9876543210" required>
                        </div>
                    </div>

                    <!-- Student Specific Block -->
                    <template v-if="role === 'Student'">
                        <div class="reg-input-group">
                            <label for="branch">Branch Stream</label>
                            <div class="reg-field-container reg-select-wrapper">
                                <i class="bi bi-diagram-2"></i>
                                <select v-model="branch" id="branch">
                                    <option value="Computer Science (CSE)">Computer Science (CSE)</option>
                                    <option value="Data Science (DS)">Data Science (DS)</option>
                                    <option value="Electrical Engineering (EE)">Electrical Engineering (EE)</option>
                                </select>
                            </div>
                        </div>

                        <div class="reg-input-group">
                            <label for="cgpa">Current CGPA</label>
                            <div class="reg-field-container">
                                <i class="bi bi-award"></i>
                                <input type="text" v-model="cgpa" id="cgpa" placeholder="e.g., 8.5">
                            </div>
                        </div>
                    </template>

                    <!-- Company Specific Block -->
                    <template v-if="role === 'Company'">
                        <div class="reg-input-group reg-full-width">
                            <label for="about">About Company / Organization</label>
                            <div class="reg-field-container reg-textarea-container">
                                <i class="bi bi-info-circle"></i>
                                <textarea v-model="about" id="about" placeholder="Describe core operations, industries, scale, or hiring context..." rows="3" required></textarea>
                            </div>
                        </div>
                    </template>
                </div>

                <!-- Submit and Redirects -->
                <button type="submit" class="reg-submit-btn">
                    <span>Complete Registration</span>
                    <i class="bi bi-arrow-right-short"></i>
                </button>

                <div class="reg-footer-divider"><span>or</span></div>

                <p class="reg-login-nav-text">
                    Already cataloged? <router-link to="/login">Access Login Node</router-link>
                </p>
            </form>
        </div>
    </div>
</template>

<script>
import axios from 'axios';

export default {
    name: "RegisterView",
    data() {
        return {
            role: "Student",
            username: "",
            email: "",
            password: "",
            confirm_password: "",
            full_name: "",
            contact: "",
            branch: "Computer Science (CSE)",
            cgpa: "",
            about: "",
            serverMessage: "",
            isSuccess: false
        }
    },
    methods: {
        changeRole(selectedRole) {
            this.role = selectedRole;
            this.serverMessage = "";
        },
        async registerUser() {
            if (this.password !== this.confirm_password) {
                this.isSuccess = false;
                this.serverMessage = "Passwords do not match. Please verify fields.";
                return;
            }

            try {
                this.serverMessage = "";
                const payload = {
                    role: this.role,
                    username: this.username,
                    email: this.email,
                    password: this.password,
                    full_name: this.full_name,
                    contact: this.contact
                };

                if (this.role === 'Student') {
                    payload.branch = this.branch;
                    payload.cgpa = this.cgpa;
                } else if (this.role === 'Company') {
                    payload.about = this.about;
                }

                const res = await axios.post("auth/register", payload, {
                    withCredentials: true
                });

                this.isSuccess = true;
                this.serverMessage = res.data.message || "Registration completed successfully!";
                
                this.username = this.email = this.password = this.confirm_password = this.full_name = this.contact = this.cgpa = this.about = "";
                
                setTimeout(() => {
                    this.$router.push('/login');
                }, 2000);

            } catch (err) {
                this.isSuccess = false;
                if (err.response && err.response.data && err.response.data.message) {
                    this.serverMessage = err.response.data.message;
                } else if (err.response && err.response.data && err.response.data.error) {
                    this.serverMessage = err.response.data.error;
                } else {
                    this.serverMessage = "Network latency error. Please try again.";
                }
            }
        }
    }
}
</script>
<style>
@import "../assets/css/RegisterationView.css";
</style>