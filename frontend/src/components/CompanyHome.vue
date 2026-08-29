<template>
    <div class="company-home-wrapper">

        <div class="ch-metrics-grid-row">
            <div class="ch-metric-card">
                <div class="ch-card-icon-wrap ch-icon-blue">
                    <i class="bi bi-briefcase-fill"></i>
                </div>
                <span class="ch-card-meta-label">TOTAL JOB POSTINGS</span>
                <span class="ch-card-main-value">{{ metricsData.totalDrives }}</span>
                <p class="ch-card-hint-text">Total campaigns created</p>
            </div>

            <div class="ch-metric-card">
                <div class="ch-card-icon-wrap ch-icon-green">
                    <i class="bi bi-people-fill"></i>
                </div>
                <span class="ch-card-meta-label">TOTAL APPLICANTS</span>
                <span class="ch-card-main-value">{{ metricsData.totalApplicants }}</span>
                <p class="ch-card-hint-text">Across all positions</p>
            </div>

            <div class="ch-metric-card">
                <div class="ch-card-icon-wrap ch-icon-orange">
                    <i class="bi bi-person-check-fill"></i>
                </div>
                <span class="ch-card-meta-label">SHORTLISTED</span>
                <span class="ch-card-main-value">{{ metricsData.shortlisted }}</span>
                <p class="ch-card-hint-text">Candidates in pipeline</p>
            </div>

            <div class="ch-metric-card ch-purple-border-card">
                <div class="ch-card-icon-wrap ch-icon-purple">
                    <i class="bi bi-patch-check-fill"></i>
                </div>
                <span class="ch-card-meta-label">PLACEMENT RATE</span>
                <span class="ch-card-main-value ch-purple-value-text">{{ metricsData.successRate }}%</span>
                <p class="ch-card-hint-text">Final conversion metric</p>
            </div>
        </div>

        <div class="ch-error-message-bar" v-if="ErrorMessage">
            <p>{{ ErrorMessage }}</p>
        </div>

        <div class="ch-drives-section">
            <h3 class="ch-section-title">Latest Posted Drives</h3>

            <div class="ch-drives-grid">
                <div v-for="drive in latestDrives" :key="drive.id" class="ch-drive-selector-card">
                    <div class="ch-card-header">
                        <span :class="['ch-role-tag', drive.status === 'ONGOING' ? 'ch-tag-ongoing' : 'ch-tag-closed']">
                            {{ drive.status }}
                        </span>
                    </div>
                    <h4 class="ch-drive-title-text">{{ drive.title }}</h4>
                    <p class="ch-drive-deadline-text">
                        <i class="bi bi-calendar-event"></i> Deadline: {{ drive.deadline }}
                    </p>
                    <div class="ch-drive-card-footer">
                        <span class="ch-drive-applicant-count-text">
                            <strong>{{ drive.apps_count }}</strong> applied
                        </span>
                    </div>
                </div>

                <div v-if="latestDrives.length === 0" class="ch-no-drives-card">
                    No recent job campaigns found.
                </div>
            </div>
        </div>

        <div class="ch-analytics-table-section">
            <h3 class="ch-section-title">Role Analytics & Skill Benchmarks</h3>

            <div class="ch-table-responsive-wrapper">
                <table class="ch-analytics-data-table">
                    <thead>
                        <tr>
                            <th>ROLE / OPENING</th>
                            <th>STATUS</th>
                            <th class="ch-text-center">TOTAL APPS</th>
                            <th class="ch-text-center">SHORTLISTED</th>
                            <th class="ch-text-center">SELECTED</th>
                            <th>TARGET CORE SKILLS</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="role in roleAnalytics" :key="role.id" class="ch-table-data-row">
                            <td class="ch-role-name-cell">{{ role.role_name }}</td>
                            <td>
                                <span :class="['ch-status-badge', role.status === 'ONGOING' ? 'ch-status-ongoing' : 'ch-status-closed']">
                                    {{ role.status }}
                                </span>
                            </td>
                            <td class="ch-text-center ch-count-blue">{{ role.total_applicants }}</td>
                            <td class="ch-text-center ch-count-orange">{{ role.shortlisted }}</td>
                            <td class="ch-text-center ch-count-green">{{ role.selected }}</td>
                            <td class="ch-skills-cell">{{ role.required_skills }}</td>
                        </tr>
                        <tr v-if="roleAnalytics.length === 0">
                            <td colspan="6" class="ch-empty-table-cell">
                                No analytics matrix available yet.
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</template>

<script>
import axios from 'axios'

export default {
    name: "CompanyMetrics",
    data() {
        return {
            metricsData: {
                totalDrives: 0,
                totalApplicants: 0,
                shortlisted: 0,
                successRate: 0
            },
            ErrorMessage: "",
            MetricsdataPolling: null,
            latestDrives: [],
            roleAnalytics: []
        }
    },
    beforeDestroy() {
        clearTimeout(this.MetricsdataPolling);
        window.removeEventListener("online", this.handleNetworkRecovery);
    },
    created() {
        this.fetchLiveMetrics();
        window.addEventListener("online", this.handleNetworkRecovery);
        this.fetchLatestDrives();
        this.fetchRoleAnalytics();
    },
    methods: {
        async fetchLiveMetrics() {
            try {
                const res = await axios.get('/company/dashboard/metrics');
                this.metricsData = res.data;
                this.ErrorMessage = "";
                const ONE_HOUR = 60 * 60 * 1000;
                this.MetricsdataPolling = setTimeout(() => { this.fetchLiveMetrics() }, ONE_HOUR);
            } catch (err) {
                if (err.response && err.response.data) {
                    this.ErrorMessage = err.response.data.message || "Server side exception caught.";
                } else {
                    this.ErrorMessage = "Network Error";
                }
                this.MetricsdataPolling = setTimeout(() => { this.fetchLiveMetrics() }, 60 * 1000);
            }
        },
        async fetchLatestDrives() {
            try {
                const res = await axios.get('/company/dashboard/latest-drives');
                this.latestDrives = res.data;
            } catch (err) {
                if (err.response && err.response.data) {
                    this.ErrorMessage = err.response.data.message || "Error loading drives.";
                } else {
                    this.ErrorMessage = "Network Error";
                }
            }
        },
        async fetchRoleAnalytics() {
            try {
                const res = await axios.get('/company/dashboard/role-analytics');
                this.roleAnalytics = res.data;
            } catch (err) {
                if (err.response && err.response.data) {
                    this.ErrorMessage = err.response.data.message || "Error loading analytics.";
                } else {
                    this.ErrorMessage = "Network Error";
                }
            }
        },
        handleNetworkRecovery() {
            if (navigator.onLine) {
                console.log("Internet restored! Automatic sync active...");
                this.ErrorMessage = "";
                this.fetchLiveMetrics();
                this.fetchLatestDrives();
                this.fetchRoleAnalytics();
            }
        }
    }
}
</script>

<style scoped>
@import '../assets/css/CompanyHome.css';
</style>