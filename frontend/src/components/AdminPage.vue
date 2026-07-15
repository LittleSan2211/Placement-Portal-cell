<template>
    <section class="ad">
        <CreateDriveModal v-if="isAdminDriveModalOpen" :isAdminMode="true" :companiesList="availableCompanies"
            @close="isAdminDriveModalOpen = false" @submit-drive="handleAdminCreateDriveAPI" />

        <div class="ad-upper">
            <div class="adu-left">
                <h3>Overview</h3>
                <p>Welcome back. Here's what's happening across the campus today.</p>
            </div>
            <div class="adu-right">
                <button><i class="bi bi-download ad-icon"></i><span>Export Report</span></button>

                <div @click="openAdminModal" style="cursor: pointer;">
                    <p><i class="bi bi-plus"></i><span>New Placement Drive</span></p>
                    <p v-if="statError" class="drv-error-banner" style="color: red; font-size: 12px; margin-top: 4px;">
                        {{ statError }}</p>
                </div>
            </div>
        </div>
        <div class="ad-middle">
            <div class="adm-card">
                <div class="card-top-row">
                    <div class="card-icon-box student-icon"><i class="bi bi-people-fill"></i></div>
                    <span class="trend-tag green-tag">{{ studentGrowth }} <i class="bi bi-arrow-up-right"></i></span>
                </div>
                <span>TOTAL STUDENTS</span>
                <span>{{ totalStudents }}</span>
                <p>Active registrations this term</p>
            </div>
            <div class="adm-card">
                <div class="card-top-row">
                    <div class="card-icon-box company-icon"><i class="bi bi-building"></i></div>
                    <span class="trend-tag green-tag">{{ companyGrowth }} <i class="bi bi-arrow-up-right"></i></span>
                </div>
                <span>TOTAL COMPANIES</span>
                <span>{{ totalCompanies }}</span>
                <p>Active registrations this term</p>
            </div>
            <div class="adm-card">
                <div class="card-top-row">
                    <div class="card-icon-box drive-icon"><i class="bi bi-lightning-charge-fill"></i></div>
                    <span class="trend-tag orange-tag">Active</span>
                </div>
                <span>ONGOING DRIVES</span>
                <span>{{ activeDrives }}</span>
                <p>Live application windows</p>
            </div>
            <div class="adm-card">
                <div class="card-top-row">
                    <div class="card-icon-box rate-icon"><i class="bi bi-patch-check-fill"></i></div>
                    <span class="trend-tag blue-tag">{{ placementRate }}% Rate</span>
                </div>
                <span class="card-title">PLACEMENT RATE</span>
                <span class="card-value">{{ placementRate }}%</span>
                <p class="card-sub">Current placement percentage</p>
            </div>
            <div class="adm-card">
                <div class="card-top-row">
                    <div class="card-icon-box blacklist-icon"><i class="bi bi-slash-circle-fill"></i></div>
                </div>
                <span>BLACKLIST COMPANIES</span>
                <span>{{ blacklistCompanies }}</span>
                <p>Ban companies by institute</p>
            </div>
            <div class="adm-card">
                <div class="card-top-row">
                    <div class="card-icon-box pending-icon"><i class="bi bi-clock-history"></i></div>
                </div>
                <span>PENDING COMPANIES</span>
                <span>{{ pendingCompanies }}</span>
                <p>Pending Companies for approval</p>
            </div>
        </div>
        <div class="adm-table">
            <table>
                <thead>
                    <tr>
                        <th>Company Name</th>
                        <th>Industry</th>
                        <th>Location</th>
                        <th>Time</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="company in recentComapnyRequest" :key="company.id">
                        <td>{{ company.name }}</td>
                        <td>{{ company.industry }}</td>
                        <td>{{ company.location }}</td>
                        <td>{{ company.time }}</td>
                    </tr>
                </tbody>
            </table>
        </div>
        <div class="adl-upper">
            <h3>Recent Activity</h3>
        </div>
        <div class="trp">
            <h3>Top Recruting Partners</h3>
            <div class="partner-list">
                <div v-for="(partner, index) in topPartners" :key="index" class="partner-card">
                    <div class="partner-left">
                        <span class="rank-badge">#{{ index + 1 }}</span>
                        <div class="company-avatar">{{ partner.name.charAt(0) }}</div>
                        <div class="company-details">
                            <h4>{{ partner.name }}</h4>
                            <p>{{ partner.industry }}</p>
                        </div>
                    </div>
                    <div class="partner-right">
                        <span class="package-badge">{{ partner.max_salary }} LPA</span>
                        <p>Highest Offer</p>
                    </div>
                </div>
                <div v-if="topPartners.length === 0" class="no-data">
                    Abhi tak koi placement record nahi hai.
                </div>
            </div>
        </div>
    </section>
</template>

<script>
import axios from 'axios';
import CreateDriveModal from "../components/CreateDriveModal.vue";

export default {
    name: "AdminPage",
    components: {
        CreateDriveModal
    },
    data() {
        return {
            totalStudents: 0, totalCompanies: 0, activeDrives: 0, totalApplications: 0, pendingCompanies: 0,
            blacklistCompanies: 0, placementRate: 0, recentComapnyRequest: [], statError: '', studentGrowth: 0,
            companyGrowth: 0, topPartners: [],
            // 🔥 FIXED SPOT 4: Reactive control variable lists
            isAdminDriveModalOpen: false,
            availableCompanies: []
        }
    },
    created() {
        this.getDashboardData();
        this.getTopPartners();
    },
    methods: {
        async getDashboardData() {
            try {
                const res = await axios.get('/admin/stats')
                this.totalStudents = res.data.totalStudents;
                this.totalCompanies = res.data.totalCompanies;
                this.totalApplications = res.data.totalApplications;
                this.pendingCompanies = res.data.pendingApprovals;
                this.activeDrives = res.data.activeDrives;
                this.blacklistCompanies = res.data.blacklistedCompanies;
                this.recentComapnyRequest = res.data.recentCompanyRequests;
                this.placementRate = res.data.placementRate;
                this.studentGrowth = res.data.studentGrowth;
                this.companyGrowth = res.data.companyGrowth;
            }
            catch (error) {
                this.statError = "Data fetch karne mein dikkat aayi";
            }
        },
        async getTopPartners() {
            try {
                const res = await axios('/admin/top-partners')
                this.topPartners = res.data;
            }
            catch (error) {
                console.log(error);
            }
        },
        // 🔥 FIXED SPOT 5: Open Admin Modal and load dynamic registered corporate channels
        async openAdminModal() {
            try {
                this.statError = "";

                // 🚀 FIXED: Admin dashboard ke context ke hisab se sahi route ko hit kiya
                const res = await axios.get('/admin/drives');

                // Agar /admin/drives endpoint direct pure jobs/companies return kar raha hai
                // toh uski unique companies list ko extraction framework par map karenge:
                if (res.data && res.data.jobs) {
                    const uniqueCompanies = {};
                    res.data.jobs.forEach(job => {
                        if (job.company_name) {
                            // Yahan hum company_name aur company_id (agar unique database columns hain) extract kar rahe hain
                            // Agar backend se structural column job.company_id na mile, toh database setup ke dynamic IDs bypass options use ho sakte hain
                            const c_id = job.company_id || job.id;
                            uniqueCompanies[job.company_name] = c_id;
                        }
                    });

                    this.availableCompanies = Object.keys(uniqueCompanies).map(name => ({
                        id: uniqueCompanies[name],
                        name: name
                    }));
                } else {
                    // Dropdown array data loading fallback matrix
                    this.availableCompanies = [];
                }

                this.isAdminDriveModalOpen = true;
            } catch (err) {
                console.error("Failed loading corporate list arrays:", err);
                this.statError = "Corporate drop list load failed.";
            }
        },
        // 🔥 FIXED SPOT 6: Handle execution for admin override insertion
        async handleAdminCreateDriveAPI(payload) {
            try {
                this.statError = "";
                const res = await axios.post("/dashboard/create-drive-override", payload);

                alert(res.data.message || "Drive successfully deployed by Admin!");
                this.isAdminDriveModalOpen = false;

                // Real-time grid counts reload trigger
                await this.getDashboardData();
            } catch (error) {
                console.error("Admin processing collapse:", error);
                alert(error.response?.data?.message || "Admin creation action failure.");
            }
        }
    }
}
</script>

<style>
@import '../assets/css/AdminPage.css';
@import '../assets/css/ModalPopup.css';
</style>