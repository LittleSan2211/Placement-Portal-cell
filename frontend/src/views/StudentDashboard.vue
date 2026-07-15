<template>
    <div class="db-master-wrapper">

        <div class="db-sidebar-pane">
            <div class="db-brand-section">
                <i class="bi bi-mortarboard-fill"></i>
                <span class="db-brand-text">Student Portal</span>
            </div>

            <div class="db-menu-list-wrapper">
                <router-link to="/student" class="db-menu-item" exact-active-class="db-item-active">
                    <i class="bi bi-grid-1x2-fill"></i> Dashboard
                </router-link>
                <router-link to="/student/profile" class="db-menu-item" exact-active-class="db-item-active">
                    <i class="bi bi-person-bounding-box"></i> My Profile
                </router-link>
                <router-link to="/student/job-explore" class="db-menu-item"
                    exact-active-class="db-item-active">
                    <i class="bi bi-compass-fill"></i> Job Explore
                </router-link>
                <router-link to="/student/applications" class="db-menu-item" exact-active-class="db-item-active">
                    <i class="bi bi-file-earmark-text-fill"></i> Applied History
                </router-link> 
                <!-- <router-link to="/student/downloads" class="db-menu-item" exact-active-class="db-item-active">
                    <i class="bi bi-cloud-arrow-down-fill"></i> Letters Download
                </router-link> -->
            </div>
            <div class="db-sidebar-footer-utils">
                <button class="db-util-btn-showcase" title="Settings (Disabled)">
                    <i class="bi bi-gear-fill"></i> <span>Settings</span>
                </button>

                <button class="db-util-btn-showcase" title="Help & Support (Disabled)">
                    <i class="bi bi-question-circle-fill"></i> <span>Support</span>
                </button>

                <div class="db-divider-line"></div>

                <button @click="handleUserLogout" class="db-util-btn-logout" title="Exit Session">
                    <i class="bi bi-box-arrow-left"></i> <span>Logout</span>
                </button>
            </div>
        </div>

        <div class="db-content-core-pane">

            <div class="db-top-header-bar">
                <div class="db-header-welcome-zone">
                    <h2 class="db-user-greet">Welcome back, <span class="db-highlight-name">{{ studentName ||
                        'Loading...' }}</span> 👋</h2>
                    <p class="db-context-subtext">IIT Placement Automation Tracker Matrix</p>
                </div>

                <div class="db-header-profile-badge">
                    <div class="db-avatar-circle">
                        {{ studentName ? studentName.charAt(0).toUpperCase() : 'S' }}
                    </div>
                </div>
            </div>

            <div class="db-view-render-container">
                <router-view></router-view>
            </div>

        </div>

    </div>
</template>

<script>
import axios from 'axios';

export default {
    name: "StudentDashboard",
    data() {
        return {
            studentName: ""
        }
    },
    created() {
        this.fetchStudentIdentityLayer();
    },
    methods: {
        async fetchStudentIdentityLayer() {
            try {
                const res = await axios.get('/student/dashboard/identity');
                this.studentName = res.data.full_name;
            } catch (err) {
                console.error("Identity synchronization down:", err);
                this.studentName = "Student Student";
            }
        },
        handleUserLogout() {
            // LocalStorage ya Cookies jahan bhi tumne JWT token save kiya hai use clear karo
            localStorage.removeItem('access_token');
            localStorage.removeItem('user_role'); // Agar role set kiya hai to

            // Custom header reset (Optional safe step)
            if (axios.defaults.headers.common['Authorization']) {
                delete axios.defaults.headers.common['Authorization'];
            }

            // Redirect back to login root view page
            this.$router.push('/login');
        }
    }
}
</script>
<style>
@import "../assets/css/StudentDashboard.css";
</style>