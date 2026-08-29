<template>
    <section class="drv-container">
        <div class="drv-header-row">
            <div class="drv-header-left">
                <h3>Placement Drives & Campaigns</h3>
                <p>Verify fresh job opening profiles, manage active applications streams, and analyze recruiting velocity.</p>
            </div>
            <div class="drv-header-right">
                <button class="drv-export-btn"><i class="bi bi-file-earmark-bar-graph"></i><span>Generate Campaign Audit</span></button>
            </div>
        </div>

        <p v-if="statError" class="drv-error-banner">
            <i class="bi bi-exclamation-triangle-fill"></i> {{ statError }}
        </p>

        <div class="drv-metrics-grid">
            <div class="drv-metric-card">
                <div class="drv-icon-box drv-blue-box"><i class="bi bi-lightning-charge-fill"></i></div>
                <span class="drv-card-label">TOTAL JOB POSTINGS</span>
                <span class="drv-card-value">{{ metrics.totalJobs }}</span>
                <p class="drv-card-sub">Aggregated openings cataloged</p>
            </div>
            <div class="drv-metric-card">
                <div class="drv-icon-box drv-green-box"><i class="bi bi-play-circle-fill"></i></div>
                <span class="drv-card-label">ONGOING CAMPAIGNS</span>
                <span class="drv-card-value-success">{{ metrics.ongoing }}</span>
                <p class="drv-card-sub">Active application gates open</p>
            </div>
            <div class="drv-metric-card">
                <div class="drv-icon-box drv-orange-box"><i class="bi bi-shield-lock-fill"></i></div>
                <span class="drv-card-label">PENDING APPROVALS</span>
                <span class="drv-card-value-warning">{{ metrics.pending }}</span>
                <p class="drv-card-sub">Incoming listings to calibrate</p>
            </div>
            <div class="drv-metric-card">
                <div class="drv-icon-box drv-purple-box"><i class="bi bi-envelope-paper-fill"></i></div>
                <span class="drv-card-label">TOTAL APPLICATIONS</span>
                <span class="drv-card-value">{{ metrics.totalApps }}</span>
                <p class="drv-card-sub">Student response submissions</p>
            </div>
        </div>

        <div class="drv-split-row">
            <div class="drv-split-left-pane">
                <h3>New Drives Validation Board</h3>
                <div class="drv-table-wrapper">
                    <table class="drv-inner-table">
                        <thead>
                            <tr>
                                <th>Corporate & Designation</th>
                                <th>Remuneration</th>
                                <th>Eligible Stream</th>
                                <th>Validation Triggers</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="job in pendingDrives" :key="job.id">
                                <td class="drv-bold-td">{{ job.company_name }} <p class="drv-sub-text-label">{{ job.title }}</p></td>
                                <td class="drv-highlight-blue">{{ (job.salary / 100000).toFixed(1) }} LPA</td>
                                <td><span class="drv-branch-badge">{{ job.branch }}</span></td>
                                <td class="drv-action-inline">
                                    <button class="drv-mini-circle drv-check" @click="executeAction(job.id, 'APPROVE')" title="Approve & Go Live"><i class="bi bi-check-lg"></i></button>
                                    <button class="drv-mini-circle drv-cross" @click="executeAction(job.id, 'REJECT')" title="Reject / Dismiss opening"><i class="bi bi-x-lg"></i></button>
                                </td>
                            </tr>
                            <tr v-if="pendingDrives.length === 0">
                                <td colspan="4" class="drv-empty-message">No incoming drive profiles awaiting validation locks.</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <div class="drv-split-right-pane">
                <h3>Top 7 Most Active Partners</h3>
                <div class="drv-frequency-stack">
                    <div v-for="(corp, i) in topDemanding" :key="i" class="drv-freq-tile">
                        <div class="drv-tile-left">
                            <span class="drv-badge-idx">#{{ i + 1 }}</span>
                            <span class="drv-corp-name">{{ corp.name }}</span>
                        </div>
                        <span class="drv-openings-pill">{{ corp.job_count }} Drives Listed</span>
                    </div>
                    <div v-if="topDemanding.length === 0" class="drv-empty-message">No recruitment statistics tracks indexed.</div>
                </div>
            </div>
        </div>

        <div class="drv-master-tabs-wrapper">
            <div class="drv-tabs-header-row">
                <div class="drv-tab-buttons-trigger">
                    <button :class="['drv-tab-link', activeTab === 'ongoing' ? 'drv-tab-active' : '']" @click="activeTab = 'ongoing'">Active & Ongoing Tracks ({{ ongoingDrivesList.length }})</button>
                    <button :class="['drv-tab-link', activeTab === 'archived' ? 'drv-tab-active' : '']" @click="activeTab = 'archived'">Archived / Closed Records ({{ archivedDrivesList.length }})</button>
                </div>
                <div class="drv-search-box-wrap">
                    <i class="bi bi-search"></i>
                    <input type="text" v-model="searchQuery" placeholder="Filter directories by firm or role designations...">
                </div>
            </div>

            <table class="drv-directory-grid">
                <thead>
                    <tr>
                        <th>Campaign ID</th>
                        <th>Recruiting Entity</th>
                        <th>Job Designation</th>
                        <th>Compensation Details</th>
                        <th>Application Window Close</th>
                        <th>Submissions Count</th>
                        <th>Operational Management</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="drive in filteredDrives" :key="drive.id">
                        <td class="drv-mono-text">#DRV-{{ drive.id }}</td>
                        <td class="drv-bold-td">{{ drive.company_name }}</td>
                        <td>{{ drive.title }}</td>
                        <td class="drv-highlight-blue">{{ (drive.salary / 100000).toFixed(1) }} LPA</td>
                        <td><i class="bi bi-calendar-event text-muted"></i> {{ drive.deadline }}</td>
                        <td>
                            <span class="drv-count-indicator"><i class="bi bi-people-fill"></i> {{ drive.apps_count }} applied</span>
                        </td>
                        <td class="drv-directory-actions-cell">
                            <button class="drv-panel-btn drv-view-apps" @click="manageApplicants(drive.id)" title="Manage Student Applications"><i class="bi bi-sliders2"></i> View Apps</button>
                            <button v-if="drive.status === 'ONGOING' && drive.approval_status === 'APPROVED'" class="drv-panel-btn drv-close-gate" @click="executeAction(drive.id, 'CLOSE_APPLICATION')" title="Forced Stop Window"><i class="bi bi-stop-circle"></i> Close Gate</button>
                        </td>
                    </tr>
                    <tr v-if="filteredDrives.length === 0">
                        <td colspan="7" class="drv-empty-message">No directory records found indexing current search queries.</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </section>
</template>

<script>
import axios from 'axios'

export default {
    name: "AdminDrive",
    data() {
        return {
            metrics: { totalJobs: 0, ongoing: 0, pending: 0, totalApps: 0 },
            jobs: [],
            topDemanding: [],
            searchQuery: "",
            activeTab: "ongoing",
            statError: ""
        }
    },
    computed: {
        pendingDrives() {
            return this.jobs.filter(j => j.approval_status === 'PENDING');
        },
        ongoingDrivesList() {
            return this.jobs.filter(j => j.status === 'ONGOING' && j.approval_status === 'APPROVED');
        },
        archivedDrivesList() {
            return this.jobs.filter(j => j.status === 'CLOSED' || j.approval_status === 'CLOSED');
        },
        filteredDrives() {
            const currentList = this.activeTab === 'ongoing' ? this.ongoingDrivesList : this.archivedDrivesList;
            return currentList.filter(j => {
                return j.company_name.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
                       j.title.toLowerCase().includes(this.searchQuery.toLowerCase());
            });
        }
    },
    created() {
        this.fetchCampaignRoster();
    },
    methods: {
        async fetchCampaignRoster() {
            try {
                this.statError = "";
                const res = await axios.get('/admin/drives');
                this.metrics = res.data.metrics;
                this.jobs = res.data.jobs;
                this.topDemanding = res.data.topDemanding;
            } catch (err) {
                this.statError = "Error establishing secure connection with placement drive vectors.";
            }
        },
        async executeAction(id, actionType) {
            try {
                this.statError = "";
                await axios.post('/drives/action', { job_id: id, action: actionType });
                await this.fetchCampaignRoster();
            } catch (err) {
                this.statError = `Critical validation drop for execution action state: ${actionType}`;
            }
        },
        manageApplicants(id) {
            alert("Application controller module processing for #DRV-" + id);
        }
    }
}
</script>

<style scoped>
@import "../assets/css/AdminDrive.css";
</style>