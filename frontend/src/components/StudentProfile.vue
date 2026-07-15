<template>
    <section class="stu-prof-container">
        <div class="stu-prof-header-zone">
            <h3>Manage Candidate Profile Shell</h3>
            <p>Configure institutional data matrices, metrics, and resume indexing nodes.</p>
        </div>

        <p v-if="feedbackMsg" class="stu-prof-success-toast"><i class="bi bi-patch-check-fill"></i> {{ feedbackMsg }}
        </p>
        <p v-if="errorMsg" class="stu-prof-error-toast"><i class="bi bi-exclamation-triangle-fill"></i> {{ errorMsg }}
        </p>

        <form @submit.prevent="saveProfileData" class="stu-prof-grid-layout" enctype="multipart/form-data">

            <div class="stu-prof-card-block">
                <h4>Institutional Records & Credentials</h4>

                <div class="stu-prof-row-flex">
                    <div class="stu-prof-input-group">
                        <label>Candidate Full Name</label>
                        <input type="text" v-model="profile.full_name" required>
                    </div>
                    <div class="stu-prof-input-group">
                        <label>Primary Contact</label>
                        <input type="text" v-model="profile.contact" required>
                    </div>
                </div>

                <div class="stu-prof-row-flex">
                    <div class="stu-prof-input-group">
                        <label>Enrolled Branch Stream</label>
                        <select v-model="profile.branch">
                            <option value="CSE">Computer Science (CSE)</option>
                            <option value="DS">Data Science (DS)</option>
                            <option value="AIML">Artificial Intelligence (AIML)</option>
                            <option value="IT">Information Technology (IT)</option>
                            <option value="ECE">Electronics (ECE)</option>
                        </select>
                    </div>
                    <div class="stu-prof-input-group">
                        <label>Academic Year</label>
                        <input type="number" v-model="profile.year" min="2000" max="2044" required>
                    </div>
                    <div class="stu-prof-input-group">
                        <label>Cumulative CGPA</label>
                        <input type="number" step="0.01" min="0" max="10" v-model="profile.cgpa" required>
                    </div>
                </div>

                <div class="stu-prof-input-group">
                    <label>Professional Bio / About Me</label>
                    <textarea v-model="profile.about" rows="3"
                        placeholder="Brief statement regarding career tracks..."></textarea>
                </div>
            </div>

            <div class="stu-prof-card-block">
                <h4>Resume & Core Technical Matrix</h4>

                <div class="stu-prof-upload-zone">
                    <label>Verification Resume (Strictly PDF format)</label>
                    <div class="stu-prof-file-input-wrapper">
                        <i class="bi bi-cloud-arrow-up-fill"></i>
                        <input type="file" ref="resumeFile" @change="handleFileSelection" accept=".pdf">
                        <p v-if="selectedFileName">Selected: <strong>{{ selectedFileName }}</strong></p>
                        <p v-else>Drag or click to reference local storage file system.</p>
                    </div>
                    <div v-if="profile.resume_path" class="stu-prof-resume-badge-status">
                        <div style="display: flex; align-items: center; justify-content: space-between; width: 100%;">
                            <div>
                                <i class="bi bi-file-earmark-pdf-fill text-danger" style="font-size: 18px;"></i>
                                <span style="margin-left: 6px; font-weight: 500;">Resume is securely indexed in
                                    database.</span>
                            </div>

                            <a :href="profile.resume_url || getResumePreviewUrl(profile.resume_path)" target="_blank"
                                class="stu-prof-preview-btn">
                                <i class="bi bi-eye-fill"></i> Preview Resume
                            </a>
                        </div>
                    </div>
                </div>

                <div class="stu-prof-input-group">
                    <label>Skills Repository Core (Comma Separated)</label>
                    <input type="text" v-model="profile.skills" placeholder="e.g., Python, Vue.js, SQL, PyTorch">
                </div>

                <div class="stu-prof-input-group">
                    <label>Project / Industrial Experience Logs</label>
                    <textarea v-model="profile.experience" rows="4"
                        placeholder="Detail active work nodes, hackathons..."></textarea>
                </div>

                <button type="submit" class="stu-prof-save-btn" :disabled="isSaving">
                    <span v-if="isSaving"><i class="bi bi-arrow-repeat stu-prof-spin"></i> Syncing Engine...</span>
                    <span v-else><i class="bi bi-shield-lock-fill"></i> Synchronize Profile Changes</span>
                </button>
            </div>

        </form>
    </section>
</template>

<script>
import axios from 'axios';

export default {
    name: "StudentProfile",
    data() {
        return {
            profile: { full_name: "", contact: "", branch: "CSE", year: "", cgpa: "", about: "", skills: "", experience: "", resume_path: "" },
            resumeFileObj: null,
            selectedFileName: "",
            isSaving: false,
            feedbackMsg: "",
            errorMsg: ""
        };
    },
    created() {
        this.fetchProfileSnapshot();
    },
    methods: {
        async fetchProfileSnapshot() {
            try {
                const res = await axios.get('/student/profile');
                this.profile = res.data;
            } catch (err) {
                this.errorMsg = "Error parsing profile parameters from master node.";
            }
        },
        getResumePreviewUrl(resumePath) {
            if (!resumePath) return "";
            const fileName = resumePath.split(/[\\/]/).pop();
            return fileName ? `http://localhost:5000/student/uploads/resumes/${encodeURIComponent(fileName)}` : "";
        },
        handleFileSelection(e) {
            const file = e.target.files[0];
            if (file) {
                if (file.type !== "application/pdf") {
                    this.errorMsg = "Validation drop: Only PDFs are structured for parse indexing.";
                    this.resumeFileObj = null;
                    this.selectedFileName = "";
                    return;
                }
                this.errorMsg = "";
                this.resumeFileObj = file;
                this.selectedFileName = file.name;

                // 🔥 THE MAGIC LINE: Naya file aate hi purana visual indicator hide kar do!
                this.profile.resume_path = "";
            }
        },
        async saveProfileData() {
            this.isSaving = true;
            this.feedbackMsg = "";
            this.errorMsg = "";

            // 🔥 COMPILING MULTIPART FORMDATA FOR THE BLENDED PAYLOAD
            const formData = new FormData();
            formData.append("full_name", this.profile.full_name);
            formData.append("contact", this.profile.contact);
            formData.append("branch", this.profile.branch);
            formData.append("year", this.profile.year);
            formData.append("cgpa", this.profile.cgpa);
            formData.append("about", this.profile.about);
            formData.append("skills", this.profile.skills);
            formData.append("experience", this.profile.experience);

            if (this.resumeFileObj) {
                formData.append("resume", this.resumeFileObj);
            }

            try {
                await axios.post('/student/profile/update', formData, {
                    headers: { 'Accept': 'application/json' }
                });
                this.feedbackMsg = "Profile configuration tables synchronized successfully.";
                await this.fetchProfileSnapshot(); // Auto refresh states
            } catch (err) {
                this.errorMsg = "Transaction aborted by database constraint boundaries.";
            } finally {
                this.isSaving = false; 
            }
        }
    }
}
</script>

<style scoped>
@import "../assets/css/StudentProfile.css";
</style>