<template>
    <div class="ap-master-container">

        <!-- 🔥 FIXED ROW: Refresh Button aligned right next to layout title text -->
        <div class="ap-header-actions-row"
            style="display: flex; justify-content: space-between; align-items: center; width: 100%;">
            <div style="display: flex; align-items: center; gap: 16px;">
                <h3 class="ap-layout-title">Top Drives by Application Volume</h3>

                <button @click="handleManualRefresh" class="ap-btn-refresh-workspace" title="Sync Layout Data">
                    <i class="bi bi-arrow-clockwise"></i> Refresh Data
                </button>
            </div>

            <!-- CLEANED ACTION ACTIONS PANEL (NO BLOAT NOTIFICATION CARDS) -->
            <div class="ap-actions-feedback-wrapper">
                <span v-if="errorMessage" class="ap-live-error-notice" title="Click to dismiss"
                    @click="errorMessage = ''">
                    <i class="bi bi-exclamation-triangle-fill"></i> {{ errorMessage }}
                </span>

                <!-- 🔥 RE-STRUCTURED CELERY EXPORT TRIGGER BUTTON -->
                <button :disabled="exportStatus.type === 'loading'" @click="runAsyncCsvExport"
                    :class="['btn', exportStatus.type === 'loading' ? 'btn-warning' : exportStatus.type === 'success' ? 'btn-success' : 'btn-primary']"
                    style="border-radius: 6px; font-weight: 600; padding: 8px 18px; display: inline-flex; align-items: center; gap: 8px; border: none; cursor: pointer; transition: all 0.2s;">

                    <!-- Dynamic States Conditions (Loading / Success / Idle Default look) -->
                    <span v-if="exportStatus.type === 'loading'" class="spinner-border spinner-border-sm" role="status"
                        style="width: 1rem; height: 1rem;"></span>
                    <i v-else-if="exportStatus.type === 'success'" class="bi bi-check-circle-fill"></i>
                    <i v-else class="bi bi-file-earmark-spreadsheet-fill"></i>

                    <span>
                        {{ exportStatus.type === 'loading' ? 'Loading...' : exportStatus.type === 'success' ? 'Exported Successfully!' : 'Trigger Celery CSV' }}
                        
                    </span>
                </button>
            </div>
        </div>

        <!-- TOP CARDS ROW -->
        <div class="ap-top-cards-row">
            <div v-for="drive in topDrives" :key="'top-' + drive.id" @click="selectDrive(drive.id)"
                :class="['ap-metric-card', selectedDriveId === drive.id ? 'ap-card-active' : '']">
                <span class="ap-card-label">{{ drive.title }}</span>
                <span class="ap-card-value-text">{{ drive.apps_count }} <span
                        class="ap-small-lbl">Applicants</span></span>
                <p class="ap-card-hint-text"><i class="bi bi-geo-alt"></i> {{ drive.location }}</p>
            </div>

            <div v-if="topDrives.length === 0" class="ap-empty-top-card">
                No drives created yet.
            </div>
        </div>

        <!-- SPLIT WORKSPACE ROW -->
        <div class="ap-split-workspace-row">
            <div class="ap-left-drives-pane">
                <h4 class="ap-pane-sub-title">Campaign Filter Selector</h4>
                <div class="ap-vertical-list-scroll">
                    <div v-for="job in allDrives" :key="'list-' + job.id" @click="selectDrive(job.id)"
                        :class="['ap-list-selector-item', selectedDriveId === job.id ? 'ap-item-selected' : '']">
                        <div class="ap-item-header">
                            <span class="ap-item-title">{{ job.title }}</span>
                        </div>
                    </div>
                </div>
            </div>

            <div class="ap-right-applicants-pane">
                <h4 class="ap-pane-sub-title">Applications Roster Table Grid</h4>
                <div class="ap-horizontal-table-scroll">
                    <table class="ap-data-table-root">
                        <thead>
                            <tr>
                                <th>CANDIDATE NAME</th>
                                <th>BRANCH</th>
                                <th>CURRENT STATE</th>
                                <th class="ap-cell-center">ACTION</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="app in applicants" :key="app.application_id"
                                :class="[selectedApp && selectedApp.application_id === app.application_id ? 'ap-row-highlight' : '']">
                                <td class="ap-bold-cell">{{ app.student_name }}</td>
                                <td>{{ app.branch }}</td>
                                <td>
                                    <span :class="['ap-status-pill', 'ap-pill-' + app.status.toLowerCase()]">
                                        {{ app.status }}
                                    </span>
                                </td>
                                <td class="ap-cell-center">
                                    <button @click="showStudentDetails(app.application_id)" class="ap-btn-action-view">
                                        View Details <i class="bi bi-chevron-right"></i>
                                    </button>
                                </td>
                            </tr>
                            <tr v-if="applicants.length === 0">
                                <td colspan="4" class="ap-empty-table-text">
                                    {{ selectedDriveId ? "No candidate profiles registered for this campaign." : "Please select a drive from top cards or left panel to load candidates." }}
                                    
                                </td>
                            </tr>
                        </tbody>
                    </table> 
                </div>
            </div>
        </div>

        <!-- BOTTOM DETAILS DRAWER -->
        <div class="ap-bottom-details-drawer" v-if="selectedApp">
            <h3 class="ap-layout-title">Evaluator Core Context: {{ selectedApp.student_name }}</h3>

            <div class="ap-drawer-grid">
                <div class="ap-drawer-stats-card">
                    <p class="ap-meta-spec"><strong>Academic Branch:</strong> {{ selectedApp.branch }}</p>
                    <p class="ap-meta-spec"><strong>Current CGPA Metric:</strong> {{ selectedApp.cgpa }}</p>
                    <div class="ap-skills-box">
                        <span class="ap-skills-lbl">Core Technical Skills:</span>
                        <p class="ap-skills-desc-text">{{ selectedApp.skills }}</p>
                    </div>

                    <div style="margin-top: 16px; border-top: 1px dashed #cbd5e1; padding-top: 12px; text-align: left;">
                        <span class="ap-skills-lbl" style="display: block; margin-bottom: 6px;">Verification
                            Document:</span>
                        <a v-if="selectedApp.resume_url" :href="selectedApp.resume_url" target="_blank"
                            class="ap-hr-resume-btn">
                            <i class="bi bi-file-earmark-pdf-fill text-danger"></i> View Candidate Resume
                        </a>
                        <span v-else style="font-size: 13px; color: #64748b; font-style: italic;">
                            <i class="bi bi-file-earmark-x"></i> No Resume Index Available
                        </span>
                    </div>
                </div>

                <div class="ap-drawer-form-card">
                    <div class="ap-form-group">
                        <label class="ap-input-label">Transition Workflow State</label>
                        <select v-model="formState.status" @change="handleStatusChange" class="ap-form-select">
                            <option value="PENDING">Pending Review</option>
                            <option value="Shortlist">Shortlist for Next Phase</option>
                            <option value="Selected">Select / Hire Candidate</option>
                            <option value="Rejected">Reject Profile Application</option>
                        </select>
                    </div>

                    <div class="ap-form-group" v-if="formState.status === 'Shortlist'">
                        <label class="ap-input-label">Schedule Interview Date & Time</label>
                        <input type="datetime-local" v-model="formState.interview_time" class="ap-form-input-text" />
                    </div>

                    <div class="ap-form-group">
                        <label class="ap-input-label">Evaluation Feedback & Reason</label>
                        <textarea v-model="formState.feedback" class="ap-form-textarea"
                            placeholder="Provide evaluation notes..."></textarea>
                    </div>

                    <button @click="submitWorkflowStatus" class="ap-btn-submit-workflow">
                        <i class="bi bi-check-circle-fill"></i> Save Decision Data
                    </button>
                </div>
            </div>
        </div>

    </div>
</template>

<script>
import axios from 'axios';

export default {
    name: "CompanyApplicant",
    data() {
        return {
            topDrives: [],
            allDrives: [],
            applicants: [],
            selectedDriveId: null,
            selectedApp: null,
            formState: { status: "", feedback: "", interview_time: "" },
            TopDrivesPolling: null,
            errorMessage: "",
            exportStatus: {
                visible: false,
                type: 'idle' // loading | success | idle
            }
        }
    },
    created() {
        this.loadTopDrivesLayer();
        this.loadDrivesListLayer();
        const SIX_HOURS = 6 * 60 * 60 * 1000;
        this.TopDrivesPolling = setInterval(() => { this.loadTopDrivesLayer() }, SIX_HOURS);
    },
    beforeDestroy() {
        clearInterval(this.TopDrivesPolling);
    },
    methods: {
        triggerUiError(message, errContext) {
            console.error(`${message}:`, errContext);
            if (errContext && errContext.response && errContext.response.data && errContext.response.data.message) {
                this.errorMessage = errContext.response.data.message;
            } else {
                this.errorMessage = message;
            }
            setTimeout(() => { this.errorMessage = ""; }, 5000);
        },
        async loadTopDrivesLayer() {
            try {
                const res = await axios.get('/company/dashboard/applicants/top-drives');
                this.topDrives = res.data;
            } catch (err) {
                this.triggerUiError("Top cards sync failed", err);
            }
        },
        async loadDrivesListLayer() {
            try {
                const res = await axios.get('/company/dashboard/applicants/drives-list');
                this.allDrives = res.data;
            } catch (err) {
                this.triggerUiError("Left panel campaign list failed to fetch", err);
            }
        },
        async selectDrive(jobId) {
            this.selectedDriveId = this.selectedDriveId === jobId ? null : jobId;
            this.selectedApp = null;
            this.applicants = [];
            if (this.selectedDriveId) { await this.fetchTableMatrix(); }
        },
        async fetchTableMatrix() {
            try {
                const res = await axios.get(`/company/dashboard/applicants/table?job_id=${this.selectedDriveId}`);
                this.applicants = res.data;
            } catch (err) {
                this.triggerUiError("Failed to compile applicants roster grid", err);
            }
        },
        async handleManualRefresh() {
            await this.loadTopDrivesLayer();
            await this.loadDrivesListLayer();
            if (this.selectedDriveId) { await this.fetchTableMatrix(); }
        },
        async showStudentDetails(appId) {
            try {
                this.errorMessage = "";
                const res = await axios.get(`/company/dashboard/applicants/student-profile/${appId}`);
                if (res && res.data) {
                    this.selectedApp = res.data;
                    this.formState.status = res.data.status || "PENDING";
                    this.formState.feedback = res.data.feedback || "Provide evaluation notes...";
                    this.formState.interview_time = res.data.interview_time || "";
                }
            } catch (err) {
                this.triggerUiError("Unable to open applicant evaluation file", err);
            }
        },
        handleStatusChange() {
            if (this.formState.status !== 'Shortlist') { this.formState.interview_time = ""; }
        },
        async submitWorkflowStatus() {
            try {
                await axios.post('/company/dashboard/applicants/update-workflow', {
                    application_id: this.selectedApp.application_id,
                    status: this.formState.status,
                    feedback: this.formState.feedback,
                    interview_time: this.formState.interview_time
                });
                this.selectedApp = null;
                await this.fetchTableMatrix();
            } catch (err) {
                this.triggerUiError("Decision data submission disrupted", err);
            }
        },
        async runAsyncCsvExport() {
            this.exportStatus.type = 'loading';
            try {
                const response = await axios.post('/company/dashboard/applicants/trigger-export');
                this.exportStatus.type = 'success';

                const fileDownloadUrl = `http://localhost:5000${response.data.download_url}`;
                const hiddenDownloadAnchor = document.createElement('a');
                hiddenDownloadAnchor.href = fileDownloadUrl;
                hiddenDownloadAnchor.target = '_blank';
                document.body.appendChild(hiddenDownloadAnchor);
                hiddenDownloadAnchor.click();
                document.body.removeChild(hiddenDownloadAnchor);

                setTimeout(() => {
                    this.exportStatus.type = 'idle';
                }, 4000);
            } catch (err) {
                this.exportStatus.type = 'idle';
                this.triggerUiError("CSV Export processing stream failed", err);
            }
        }
    }
}
</script>

<style>
@import "../assets/css/CompanyApplicant.css";

/* CLEAN APP-LEVEL CSS OVERRIDES */
.btn-warning {
    background-color: #f59e0b !important;
    color: white !important;
}

.btn-success {
    background-color: #10b981 !important;
    color: white !important;
}

.btn-primary {
    background-color: #3b82f6 !important;
    color: white !important;
}

.ap-hr-resume-btn {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background-color: #ffffff;
    color: #dc2626;
    border: 1px solid #fca5a5;
    padding: 8px 14px;
    font-size: 13px;
    font-weight: 600;
    border-radius: 6px;
    text-decoration: none;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
    transition: all 0.15s ease-in-out;
}

.ap-hr-resume-btn:hover {
    background-color: #fef2f2;
    border-color: #dc2626;
    transform: translateY(-1px);
}
</style>