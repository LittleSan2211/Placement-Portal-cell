<template>
    <section class="admin">
        <CreateDriveModal 
            v-if="isDriveModalOpen" 
            :isAdminMode="false" 
            @close="isDriveModalOpen = false" 
            @submit-drive="handleCreateDriveAPI"
        />
        <div class="lun">
            <nav class="lu-nav">
                <div class="lun-upper">
                    <h3>Placement Hub</h3>
                    <p>CORPORATE PORTAL</p>
                </div>

                <div class="lun-middle">
                    <ul>
                        <li><router-link to="/company-dashboard" exact class="link"><i
                                    class="bi bi-building"></i><span>Dashboard</span></router-link></li>
                        <li><router-link to="/company-dashboard/manage-drives" class="link"><i
                                    class="bi bi-bag"></i><span>Manage Drives</span></router-link></li>
                        <li><router-link to="/company-dashboard/manage-applicants" class="link"><i
                                    class="bi bi-mortarboard s-icon"></i><span>Applicants</span></router-link></li>
                        <li><router-link to="/company-dashboard/analytics" class="link"><i
                                    class="bi bi-bar-chart-line-fill"></i><span>Analytics</span></router-link></li>
                    </ul>
                </div>

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

        <div class="lut">
            <div class="lut-img">
                <img src="../assets/clglogo.png">
                <p>Company Dashboard</p>
            </div>
            <div class="lut-right">

                <button @click="isDriveModalOpen = true"
                    style="background-color: #4f46e5; color: white; border: none; padding: 8px 16px; border-radius: 8px; font-size: 13.5px; font-weight: 600; cursor: pointer; display: flex; align-items: center; gap: 8px; transition: all 0.2s ease; margin-right: 10px;">
                    <i class="bi bi-plus-circle-fill"></i> Create Drive
                </button>

                <div
                    style="font-size: 18px; color: #64748b; cursor: pointer; display: flex; align-items: center; margin-right: 10px;">
                    <i class="bi bi-bell-fill"></i>
                </div>

                <div class="lutr-right" style="text-align: right; margin-right: 15px;">
                    <h3>Alex Rivera</h3>
                    <p> Recruiter</p>
                </div>

                <div class="lutr-am">
                    <img src="../assets/admin.png">
                </div>

            </div>
        </div>

        <div>
            <RouterView></RouterView>
        </div>

        
    </section>
</template>

<script>
import CreateDriveModal from "../components/CreateDriveModal.vue";
import axios from "axios";

export default {
    name: "CompanyDashboard",
    components: { 
        CreateDriveModal 
    },
    data() {
        return {
            isDriveModalOpen: false // Modal state visibility flag
        };
    },
    methods: {
        handleLogout() {
            localStorage.removeItem('accessToken');
            this.$router.push('/login');
        },
        async handleCreateDriveAPI(payload) {
            try {
                // Interceptor automatic header jod dega, bas clean POST call maaro
                const response = await axios.post("/company/dashboard/create-new-drive", payload);

                // Success feedback alerts
                alert(response.data.message || "Placement drive successfully launched live!");

                // Modal ko safe close kar do
                this.isDriveModalOpen = false;

                // Dashboard stats update window trigger
                if (this.getCompanyMetrics) {
                    this.getCompanyMetrics();
                } else {
                    location.reload();
                }

            } catch (error) {
                console.error("Drive creation pipeline failed:", error);
                const errorMsg = error.response?.data?.message || "Failed to create drive. Technical glitch.";
                alert(errorMsg);
            }
        }
    }
}
</script>

<style>
@import '../assets/css/AdminDashboard.css';
</style>