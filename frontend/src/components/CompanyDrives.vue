<template>
    <div class="md-master-container">

        <div class="md-cards-header-row">
            <div class="md-count-card">
                <div class="md-card-icon-circle md-bg-blue">
                    <i class="bi bi-collection-fill"></i>
                </div>
                <span class="md-card-label">TOTAL DRIVES</span>
                <span class="md-card-value-text">{{ topCards.totalDrives }}</span>
            </div>

            <div class="md-count-card">
                <div class="md-card-icon-circle md-bg-green">
                    <i class="bi bi-play-circle-fill"></i>
                </div>
                <span class="md-card-label">ONGOING DRIVES</span>
                <span class="md-card-value-text md-clr-green">{{ topCards.ongoingDrives }}</span>
            </div>

            <div class="md-count-card">
                <div class="md-card-icon-circle md-bg-red">
                    <i class="bi bi-stop-circle-fill"></i>
                </div>
                <span class="md-card-label">CLOSED DRIVES</span>
                <span class="md-card-value-text md-clr-red">{{ topCards.closedDrives }}</span>
            </div>
        </div>

        <div class="md-section-container">
            <h3 class="md-layout-title">Ongoing Campaigns & Controls</h3>

            <div class="md-scrollable-table-frame">
                <table class="md-table-element">
                    <thead>
                        <tr>
                            <th>JOB TITLE / ROLE</th>
                            <th>LOCATION</th>
                            <th>DEADLINE</th>
                            <th class="md-cell-center">QUICK ACTIONS</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="drive in ongoingDrives" :key="drive.id">
                            <td class="md-bold-cell">{{ drive.title }}</td>
                            <td>{{ drive.location }}</td>
                            <td>{{ drive.deadline }}</td>
                            <td class="md-cell-center">
                                <button @click="updateStatus(drive.id, 'CLOSED')" class="md-btn-toggle-close">
                                    <i class="bi bi-x-circle"></i> Close Drive
                                </button>
                            </td>
                        </tr>
                        <tr v-if="ongoingDrives.length === 0">
                            <td colspan="4" class="md-empty-cell-text">No active ongoing drives available right now.
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

        <div class="md-section-container md-space-top">
            <h3 class="md-layout-title">All Historical Drives Database</h3>

            <div class="md-responsive-table-frame">
                <table class="md-table-element">
                    <thead>
                        <tr>
                            <th>ROLE TITLE</th>
                            <th>PACKAGE / COMPENSATION</th>
                            <th class="md-cell-center">TOTAL APPLICANTS</th>
                            <th>DEADLINE STATUS</th>
                            <th>CURRENT STATE</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="drive in allDrives" :key="drive.id">
                            <td class="md-bold-cell">{{ drive.title }}</td>
                            <td class="md-package-highlight">{{ drive.package }}</td>
                            <td class="md-cell-center md-count-blue">{{ drive.total_apps }}</td>
                            <td>{{ drive.deadline }}</td>
                            <td>
                                <span
                                    :class="['md-state-badge', drive.status === 'ONGOING' ? 'md-state-ongoing' : 'md-state-closed']">
                                    {{ drive.status }}
                                </span>
                            </td>
                        </tr>
                        <tr v-if="allDrives.length === 0">
                            <td colspan="5" class="md-empty-cell-text">No drive history records found in company
                                datastore.</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

    </div>
</template>
<script>
import axios from 'axios';
export default {
    name: "CompanyDrives",
    data() {
        return {
            topCards: {
                totalDrives: 0,
                ongoingDrives: 0,
                closedDrives: 0
            },
            ongoingDrives: [], allDrives: [], Error: "",
        }
    },
    created() {
        this.loadSegmentedDashboard();
    },
    methods: {
        async loadSegmentedDashboard() {
            try {
                const res = await axios.get('/company/dashboard/manage-drives');
                this.topCards = res.data.top_cards;
                this.ongoingDrives = res.data.ongoing_table;
                this.allDrives = res.data.all_drives_table;
                this.Error = "";
            } catch (err) {
                if (err.response && err.response.data) {
                    this.Error = err.response.data.message || "Server error while compiling data.";
                } else {
                    this.Error = "Network Error: Server is offline.";
                }
            }
        },
        async updateStatus(jobId, targetStatus) {
            try {
                await axios.post(`/company/dashboard/toggle-drive-status/${jobId}`, { status: targetStatus });
                this.loadSegmentedDashboard();
            } catch (err) {
                if (err.response && err.response.data) {
                    this.Error = err.response.data.message || "Status shift failed.";
                } else {
                    this.Error = "Network Error";
                }
            }
        }
    }
}
</script>
<style>
@import "../assets/css/CompanyDrives.css";
</style>