<template>
    <div class="je-workspace-container">

        <div class="je-control-deck">
            <div class="je-search-box-wrapper">
                <i class="bi bi-search je-search-icon"></i>
                <input type="text" v-model="searchQuery" placeholder="Search by role, company name, or skills..."
                    class="je-search-input" />
            </div>

            <div class="je-filters-group">
                <select v-model="selectedBranch" class="je-filter-dropdown">
                    <option value="ALL">All Branches</option>
                    <option value="CSE">CSE</option>
                    <option value="IT">IT</option>
                    <option value="DS">DS</option>
                    <option value="AIML">AIML</option>
                    <option value="ECE">ECE</option>
                </select>

                <select v-model="selectedJobType" class="je-filter-dropdown">
                    <option value="ALL">All Opportunities</option>
                    <option value="Full Time">Full-Time Jobs</option>
                    <option value="Internship">Internships</option>
                </select>

                <div v-if="errorNotification" class="je-inline-error-badge">
                    <i class="bi bi-exclamation-triangle-fill"></i> {{ errorNotification }}
                </div>
            </div>
        </div>

        <div class="je-split-workspace">

            <div class="je-left-stream-pane">
                <div v-for="job in filteredJobs" :key="job.job_id" class="je-job-summary-card"
                    :class="{ 'je-active-selected-card': selectedJob && selectedJob.job_id === job.job_id }"
                    @click="selectJobForDetail(job)">
                    <div class="je-card-top-line">
                        <span class="je-card-company">{{ job.company_name }}</span>
                        <span class="je-card-package">{{ job.salary }} LPA</span>
                    </div>

                    <h3 class="je-card-role-title">{{ job.title }}</h3>
                    <div class="je-card-meta-loc">
                        <i class="bi bi-geo-alt-fill"></i> {{ job.location }}
                        <span class="je-card-type-badge"
                            :class="job.job_type === 'Internship' ? 'je-bg-purple' : 'je-bg-blue'">
                            {{ job.job_type }}
                        </span>
                    </div>

                    <div class="je-card-footer-ribbon">
                        <span v-if="job.applied_status !== 'NOT_APPLIED'" class="je-status-tag-applied">
                            <i class="bi bi-check-circle-fill"></i> Applied
                        </span>
                        <span v-else-if="!job.is_student_eligible" class="je-status-tag-ineligible">
                            Not Eligible
                        </span>
                        <span v-else class="je-status-tag-open">
                            Active / Open
                        </span>
                    </div>
                </div>

                <div v-if="filteredJobs.length === 0" class="je-no-results-box">
                    <i class="bi bi-folder-xje"></i>
                    <p>No active recruitment drives match your filter criteria.</p>
                </div>
            </div>

            <div class="je-right-details-pane">
                <div v-if="selectedJob" class="je-sticky-detail-card">
                    <div class="je-detail-header">
                        <h2 class="je-detail-title">{{ selectedJob.title }}</h2>
                        <h4 class="je-detail-company-sub">{{ selectedJob.company_name }}</h4>
                        <p class="je-detail-location-sub"><i class="bi bi-geo-alt"></i> {{ selectedJob.location }}</p>
                    </div>

                    <hr class="je-divider-line" />

                    <div class="je-detail-scroll-body">
                        <div class="je-detail-section">
                            <h5>About Company</h5>
                            <p class="je-text-muted">{{ selectedJob.company_about }}</p>
                        </div>

                        <div class="je-detail-section">
                            <h5>Required Skillsets</h5>
                            <div class="je-detail-skills-tags">
                                <span v-for="(skill, sIdx) in splitSkills(selectedJob.skills_required)" :key="sIdx"
                                    class="je-detail-skill-pill">
                                    {{ skill }}
                                </span>
                            </div>
                        </div>

                        <div class="je-detail-section">
                            <h5>Package & Additional Benefits</h5>
                            <div class="je-perks-box">
                                <div><strong style="color: #0f172a;">Salary CTC:</strong> {{ selectedJob.salary }} LPA
                                </div>
                                <div class="je-perks-text"><i class="bi bi-gift-fill"></i> {{ selectedJob.benefits }}
                                </div>
                            </div>
                        </div>

                        <div class="je-detail-section je-eligibility-summary-box">
                            <h5>Eligibility Criteria Matrix</h5>
                            <ul>
                                <li><strong>Target Branches:</strong> {{ selectedJob.eligible_branch }}</li>
                                <li><strong>Cut-off Criteria:</strong> {{ selectedJob.cgpa_required }} CGPA Minimum</li>
                                <li><strong>Target Batch:</strong> {{ selectedJob.eligible_year }} Passing Out</li>
                            </ul>
                        </div>

                        <div class="je-deadline-alert-bar">
                            <i class="bi bi-hourglass-split"></i> Application Deadline: <strong>{{ selectedJob.deadline
                            }}</strong>
                        </div>

                        <div v-if="selectedJob.applied_at_date" class="je-applied-on-badge">
                            <i class="bi bi-calendar-check"></i> You applied for this role on: {{
                                selectedJob.applied_at_date }}
                        </div>
                    </div>

                    <div class="je-detail-action-footer">
                        <button v-if="selectedJob.applied_status !== 'NOT_APPLIED'" class="je-btn-action je-btn-applied"
                            disabled>
                            <i class="bi bi-patch-check-fill"></i> Applied (Status: {{ selectedJob.applied_status }})
                        </button>

                        <button v-else-if="!selectedJob.is_student_eligible" class="je-btn-action je-btn-locked"
                            disabled>
                            <i class="bi bi-exclamation-octagon-fill"></i> Application Locked (CGPA Short)
                        </button>

                        <button v-else @click="triggerJobApplication(selectedJob.job_id)"
                            class="je-btn-action je-btn-trigger-apply">
                            Apply for this Position <i class="bi bi-arrow-right"></i>
                        </button>
                    </div>
                </div>

                <div v-else class="je-detail-empty-placeholder">
                    <i class="bi bi-briefcase-fill je-placeholder-icon"></i>
                    <h4>Select a Recruitment Drive</h4>
                    <p>Click on any job card from the stream pane to view comprehensive role matrices, company
                        benchmarks, and trigger real-time applications.</p>
                </div>
            </div>

        </div>

        <div v-if="showSuccessModal" class="je-modal-overlay">
            <div class="je-success-modal-box">
                <div class="je-modal-icon-ring">
                    <i class="bi bi-check-lg"></i>
                </div>
                <h3>Application Submitted!</h3>
                <p>Bhai, tumhari application success ke sath submit ho gayi hai. Recruiter review metrics panel par
                    status automatic synched ho chuka hai.</p>
                <button @click="closeSuccessModal" class="je-btn-modal-close">Great, Thanks!</button>
            </div>
        </div>

    </div>
</template>
<script>
import axios from 'axios';
export default {
    name: "JobExplore",
    data() {
        return {
            jobsList: [],
            searchQuery: "",
            selectedBranch: "ALL",
            selectedJobType: "ALL",
            selectedJob: null,

            showSuccessModal: false,
            errorNotification: ""
        };
    },
    computed: {
        filteredJobs() {
            return this.jobsList.filter(job => {
                const searchTxt = this.searchQuery.toLocaleLowerCase();
                const matchesSearch =
                    job.title.toLocaleLowerCase().includes(searchTxt) ||
                    job.company_name.toLocaleLowerCase().includes(searchTxt) ||
                    job.skills_required.toLocaleLowerCase().includes(searchTxt);

                const matchesBranch = this.selectedBranch === "ALL" ||
                    job.eligible_branch.toUpperCase().includes(this.selectedBranch.toLocaleUpperCase());

                const cleanSelectedType = this.selectedJobType.replace("-", " ").toLowerCase();
                const cleanJobType = job.job_type ? job.job_type.replace("-", " ").toLowerCase() : "";

                const matchesJobType = this.selectedJobType === "ALL" ||
                    cleanJobType === cleanSelectedType;

                return matchesSearch && matchesBranch && matchesJobType;
            })
        }
    },
    created() {
        this.fetchExploreJobStream();
    },
    methods: {
        async fetchExploreJobStream() {
            try {
                const res = await axios.get('/student/dashboard/explore-jobs');
                this.jobsList = res.data;
                if (this.jobsList.length > 0 && !this.selectedJob) {
                    this.selectedJob = this.jobsList[0];
                } 
            } catch (err) {
                this.triggerInlineError("Failed loading explore job matrix streams.");
            }
        },
        selectJobForDetail(job) {
            this.selectedJob = job;
        },
        splitSkills(skillsString) {
            if (!skillsString) return [];
            return skillsString.split(',').map(s => s.trim()).filter(s => s);
        },
        async triggerJobApplication(jobId) {
            try {
                this.errorNotification = "";
                const response = await axios.post('/student/apply', { job_id: jobId });
                if (response) {
                    this.showSuccessModal = true;
                }
                await this.fetchExploreJobStream();

                this.selectedJob = this.jobsList.find(j => j.job_id === jobId) || null;
            } catch (err) {
                const msg = err.response?.data?.message || "Failed to apply for this application.";
                this.triggerInlineError(msg);
            }
        },
        triggerInlineError(message) {
            this.errorNotification = message;
            setTimeout(() => {
                this.errorNotification = "";
            }, 10000);
        },

        closeSuccessModal() {
            this.showSuccessModal = false;
        }
    }
}
</script>
<style>
@import "../assets/css/StudentJobexplore.css";
</style>