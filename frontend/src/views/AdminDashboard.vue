<template>
    <section class="admin">
        <!-- LEFT SIDEBAR -->
        <div class="lun">
            <nav class="lu-nav">
                <!-- Upper Brand Block -->
                <div class="lun-upper">
                    <h3>Placement Hub</h3>
                    <p>ADMIN CONSOLE</p>
                </div>

                <!-- Middle Functional Tabs -->
                <div class="lun-middle">
                    <ul>
                        <li>
                            <router-link to="/admin-dashboard" exact class="link">
                                <i class="bi bi-grid-1x2-fill"></i><span>Dashboard</span>
                            </router-link>
                        </li>
                        <li>
                            <router-link to="/admin-dashboard/students" class="link">
                                <i class="bi bi-mortarboard-fill"></i><span>Students</span>
                            </router-link>
                        </li>
                        <li>
                            <router-link to="/admin-dashboard/company" class="link">
                                <i class="bi bi-buildings-fill"></i><span>Company</span>
                            </router-link>
                        </li>
                        <li>
                            <router-link to="/admin-dashboard/drives" class="link">
                                <i class="bi bi-briefcase-fill"></i><span>Drives</span>
                            </router-link>
                        </li>
                        <li>
                            <router-link to="#" class="link">
                                <i class="bi bi-graph-up-arrow"></i><span>Analytics</span>
                            </router-link>
                        </li>
                    </ul>
                </div>

                <!-- Bottom Config Block (Settings, Support & Drive fixed) -->
                <div class="lun-bottom">
                    <router-link to="#" class="link text-link">
                        <i class="bi bi-question-circle"></i><span>Support</span>
                    </router-link>
                    <router-link to="#" class="link text-link">
                        <i class="bi bi-gear"></i><span>Settings</span>
                    </router-link>
                    <div @click="handleLogout" class="link logout-clickable-btn">
                        <i class="bi bi-box-arrow-left"></i><span>Log Out</span>
                    </div>
                </div>
            </nav>
        </div>

        <!-- TOP NAVBAR -->
        <div class="lut">
            <div class="lut-img">
                <img src="../assets/clglogo.png">
                <p>Admin Dashboard</p>
            </div>
            <div class="lut-right">
                <div class="lutr-left">
                    <i class="bi bi-bell-fill"></i>
                </div>
                <div class="lutr-right">
                    <h3>Admin User</h3>
                    <p>Super Admin</p>
                </div>
                <div class="lutr-am">
                    <img src="../assets/admin.png">
                </div>
            </div>
        </div>

        <!-- MAIN ROUTER COMPONENT SPACE -->
        <div class="admin-content-render-node">
            <RouterView></RouterView>
        </div>
    </section>
</template>

<script>
export default {
    name: "AdminDashboard",
    methods: {
        handleLogout() {
            localStorage.removeItem('accessToken');
            this.$router.push('/login');
        }
    }
}
</script>

<style>
@import '../assets/css/AdminDashboard.css';
</style>