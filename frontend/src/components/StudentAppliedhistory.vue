<template>
    <div class="ah-workspace-container">
        
        <div v-if="errorNotification" class="ah-floating-error-toast">
            <i class="bi bi-exclamation-triangle-fill"></i>
            <div class="ah-toast-content">
                <strong>System Alert</strong>
                <p>{{ errorNotification }}</p>
            </div>
        </div>
        
        <div class="ah-metrics-deck">
            <div class="ah-metric-text">
                Total Applications Sent: <span class="ah-count-num">{{ totalApplied }}</span>
            </div>
            <div class="ah-metric-divider">|</div>
            <div class="ah-metric-text">
                Placements Confirmed: <span class="ah-count-num ah-success-color">{{ totalOffers }} 🏆</span>
            </div>
        </div>

        <div class="ah-split-workspace">
            
            <div class="ah-left-stream-pane">
                <div 
                    v-for="app in historyList" 
                    :key="app.application_id" 
                    class="ah-job-summary-card"
                    :class="{ 
                        'ah-active-selected-card': selectedApp && selectedApp.application_id === app.application_id,
                        'ah-border-selected': app.status === 'Selected',
                        'ah-border-shortlist': app.status === 'Shortlist',
                        'ah-border-reject': app.status === 'Reject'
                    }"
                    @click="selectAppForDetail(app)"
                >
                    <div class="ah-card-top-line">
                        <span class="ah-card-company">{{ app.company_name }}</span>
                        <span class="ah-card-package">{{ app.salary }} LPA</span>
                    </div>

                    <h3 class="ah-card-role-title">{{ app.title }}</h3>
                    <div class="ah-card-meta-loc">
                        <i class="bi bi-geo-alt-fill"></i> {{ app.location }}
                        <span class="ah-card-type-badge">{{ app.job_type }}</span>
                    </div>

                    <div class="ah-card-status-footer">
                        <span v-if="app.status === 'Selected'" class="ah-badge-status ah-bg-success">
                            <i class="bi bi-patch-check-fill"></i> Placement Confirmed
                        </span>

                        <span v-else-if="app.status === 'Shortlist'" class="ah-badge-status ah-bg-warning">
                            <i class="bi bi-calendar2-check-fill"></i> Shortlisted
                        </span>

                        <span v-else-if="app.status === 'Reject'" class="ah-badge-status ah-bg-danger">
                            <i class="bi bi-x-circle-fill"></i> Application Closed
                        </span>

                        <span v-else class="ah-badge-status ah-bg-muted">
                            <i class="bi bi-hourglass-split"></i> Under Review
                        </span>
                    </div>
                </div>

                <div v-if="historyList.length === 0" class="ah-no-results-box">
                    <i class="bi bi-archive-fill"></i>
                    <p>You haven't applied to any recruitment drives yet.</p>
                </div>
            </div>

            <div class="ah-right-details-pane">
                <div v-if="selectedApp" class="ah-sticky-detail-card">
                    
                    <div class="ah-detail-header">
                        <h2 class="ah-detail-title">{{ selectedApp.title }}</h2>
                        <h4 class="ah-detail-company-sub">{{ selectedApp.company_name }}</h4>
                        <p class="ah-detail-location-sub"><i class="bi bi-geo-alt"></i> {{ selectedApp.location }}</p>
                    </div>

                    <hr class="ah-divider-line" />

                    <div class="ah-detail-scroll-body">
                        
                        <div class="ah-detail-section">
                            <h5>Application Timeline</h5>
                            <div class="ah-timeline-box">
                                <p><strong>Applied On:</strong> {{ selectedApp.applied_at_date }}</p>
                            </div>
                        </div>

                        <div class="ah-detail-section">
                            <h5>Offered Package</h5>
                            <div class="ah-package-box">
                                <strong>CTC Package:</strong> {{ selectedApp.salary }} LPA ({{ selectedApp.job_type }})
                            </div>
                        </div>

                        <div class="ah-detail-section">
                            <h5>Recruitment Cell Updates</h5>
                            
                            <div v-if="selectedApp.status === 'Selected'" class="ah-status-message-box ah-msg-success">
                                <h6>🎉 Congratulations!</h6>
                                <p>Your placement parameters have been officially approved and logged into the campus matrix dashboard. Corporate onboarding schedules will reach your registered email desk.</p>
                            </div>

                            <div v-else-if="selectedApp.status === 'Shortlist'" class="ah-status-message-box ah-msg-warning">
                                <h6>📅 Interview Call!</h6>
                                <p v-if="selectedApp.interview_date">
                                    Your round evaluation is locked. Your interview is scheduled on: 
                                    <strong style="display:block; margin-top:4px; color:#c2410c;">
                                        <i class="bi bi-alarm"></i> {{ selectedApp.interview_date }}
                                    </strong>
                                </p>
                                <p v-else>You have been shortlisted! The interview timeline scheduling parameters are being updated by the HR desk.</p>
                            </div>

                            <div v-else-if="selectedApp.status === 'Reject'" class="ah-status-message-box ah-msg-danger">
                                <h6>✕ Process Closed</h6>
                                <p><strong>HR Feedback:</strong> {{ selectedApp.feedback }}</p>
                            </div>

                            <div v-else class="ah-status-message-box ah-msg-muted">
                                <h6>⏳ Application Pending</h6>
                                <p>{{ selectedApp.feedback }}</p>
                            </div>
                        </div>
                    </div>

                </div>

                <div v-else class="ah-detail-empty-placeholder">
                    <i class="bi bi-folder-symlink-fill ah-placeholder-icon"></i>
                    <h4>Select an Application Log</h4>
                    <p>Click on any tracked drive card from the left grid feed to reveal explicit HR feedback, timeline metrics, and cell confirmation logs.</p>
                </div>
            </div>

        </div>
    </div>
</template>

<script>
import axios from 'axios';

export default {
    name: "StudentAppliedHistory",
    data() {
        return {
            historyList: [],
            totalOffers: 0,
            totalApplied: 0,
            selectedApp: null,
            errorNotification: ""
        };
    },
    created() {
        this.fetchAppliedHistoryStream();
    },
    methods: {
        async fetchAppliedHistoryStream() {
            try {
                const res = await axios.get('/student/dashboard/applied-history');
                this.historyList = res.data.history;
                this.totalOffers = res.data.total_offers;
                this.totalApplied = res.data.total_applied;
                
                if (this.historyList.length > 0) {
                    this.selectedApp = this.historyList[0];
                }
            } catch (err) {
                const msg = err.response?.data?.message || "Failed compiling application matrix streams.";
                this.triggerTopRightError(msg);
            }
        },
        selectAppForDetail(app) {
            this.selectedApp = app;
        },
        triggerTopRightError(message) {
            this.errorNotification = message;
            setTimeout(() => {
                this.errorNotification = "";
            }, 5000);
        }
    }
}
</script>

<style>   
@import "../assets/css/StudentAppliedhistory.css";
</style>