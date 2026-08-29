<template>
    <section class="stu-container">
        <div class="stu-header-row">
            <div class="stu-header-left">
                <h3>Student Management</h3>
                <p>Monitor campus registrations, manage profiles, and control system access states.</p>
            </div>
            <div class="stu-header-right">
                <button class="stu-export-btn"><i class="bi bi-download"></i><span>Export Roll List</span></button>
            </div>
        </div>

        <div class="stu-metrics-row">
            <div class="stu-metric-card">
                <div class="stu-card-top">
                    <div class="stu-icon-box stu-blue-box"><i class="bi bi-people-fill"></i></div>
                </div>
                <span class="stu-card-label">TOTAL REGISTERED</span>
                <span class="stu-card-value">{{ totalStudentsCount }}</span>
                <p class="stu-card-sub">Enrolled students in platform</p>
            </div>

            <div class="stu-metric-card">
                <div class="stu-card-top">
                    <div class="stu-icon-box stu-green-box"><i class="bi bi-patch-check-fill"></i></div>
                </div>
                <span class="stu-card-label">PLACED STUDENTS</span>
                <span class="stu-card-value">{{ placedStudentsCount }}</span>
                <p class="stu-card-sub">Conversion metrics active</p>
            </div>

            <div class="stu-metric-card">
                <div class="stu-card-top">
                    <div class="stu-icon-box stu-gray-box"><i class="bi bi-pause-circle-fill"></i></div>
                </div>
                <span class="stu-card-label">DEACTIVATED</span>
                <span class="stu-card-value">{{ deactivatedCount }}</span>
                <p class="stu-card-sub">Opted-out or freeze state</p>
            </div>

            <div class="stu-metric-card">
                <div class="stu-card-top">
                    <div class="stu-icon-box stu-red-box"><i class="bi bi-slash-circle-fill"></i></div>
                </div>
                <span class="stu-card-label">BLACKLISTED</span>
                <span class="stu-card-value-danger">{{ blacklistedCount }}</span>
                <p class="stu-card-sub">Banned due to policy breach</p>
            </div>
        </div>

        <div class="stu-search-filter-row">
            <div class="stu-search-wrapper">
                <i class="bi bi-search"></i>
                <input type="text" v-model="searchQuery" placeholder="Search by name, ID or contact...">
            </div>
            <div class="stu-dropdowns-group">
                <select v-model="statusFilter">
                    <option value="All">All Status</option>
                    <option value="Active">Active</option>
                    <option value="Placed">Placed</option>
                    <option value="Deactivated">Deactivated</option>
                    <option value="Blacklisted">Blacklisted</option>
                </select>
                <select v-model="branchFilter">
                    <option value="All">All Branches</option>
                    <option value="CSE">Computer Science</option>
                    <option value="DS">Data Science</option>
                    <option value="EEE">Electronics</option>
                    <option value="ECE">ECE</option>
                    <option value="AIML">AIML</option>
                </select>
            </div>
        </div>

        <div class="stu-table-wrapper">
            <h3>Registered Students ({{ filteredStudents.length }})</h3>
            <table class="stu-data-table">
                <thead>
                    <tr>
                        <th>Student ID</th>
                        <th>Name & Contact</th>
                        <th>Branch & CGPA</th>
                        <th>Placement Status</th>
                        <th>Account Status</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="student in filteredStudents" :key="student.id">
                        <td class="stu-font-mono stu-bold-id">#STU-{{ student.id }}</td>
                        <td>
                            <div class="stu-cell-stack">
                                <span class="stu-primary-text">{{ student.name }}</span>
                                <span class="stu-sub-text">{{ student.email }}</span>
                            </div>
                        </td>
                        <td>
                            <div class="stu-cell-stack">
                                <span class="stu-primary-text">{{ student.branch }}</span>
                                <span class="stu-highlight-blue">CGPA: {{ student.cgpa }}</span>
                            </div>
                        </td>
                        <td>
                            <span
                                :class="['stu-trend-badge', student.placement_status === 'Placed' ? 'stu-badge-green' : 'stu-badge-orange']">
                                {{ student.placement_status }}
                            </span>
                        </td>
                        <td>
                            <span :class="['stu-pill', getStatusClass(student.account_status)]">
                                {{ student.account_status }}
                            </span>
                        </td>
                        <td class="stu-actions-mix">
                            <button class="stu-btn-icon stu-view" @click="viewProfile(student.id)"
                                title="View Profile"><i class="bi bi-eye"></i></button>

                            <button v-if="student.account_status !== 'Blacklisted'" class="stu-btn-icon stu-ban"
                                title="Blacklist Student" @click="updateStatus(student.id, 'Blacklisted')">
                                <i class="bi bi-slash-circle"></i>
                            </button>
                            <button
                                v-if="student.account_status !== 'Deactivated' && student.account_status !== 'Blacklisted'"
                                class="stu-btn-icon stu-pause" title="Deactivate Student"
                                @click="updateStatus(student.id, 'Deactivated')">
                                <i class="bi bi-pause-circle"></i>
                            </button>
                            <button v-if="student.account_status !== 'Active'" class="stu-btn-icon stu-check"
                                title="Activate Account" @click="updateStatus(student.id, 'Active')">
                                <i class="bi bi-check-circle"></i>
                            </button>
                        </td>
                    </tr>
                    <tr v-if="filteredStudents.length === 0">
                        <td colspan="6" class="stu-empty-row">Koi bacha is search criteria se match nahi hua.</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </section>
</template>

<script>
import axios from 'axios'

export default {
    name: "AdminStudent",
    data() {
        return {
            students: [],
            searchQuery: "",
            statusFilter: "All",
            branchFilter: "All"
        }
    },
    computed: {
        totalStudentsCount() {
            return this.students.length;
        },
        placedStudentsCount() {
            return this.students.filter(s => s.placement_status === 'Placed').length;
        },
        deactivatedCount() {
            return this.students.filter(s => s.account_status === 'Deactivated').length;

        },
        blacklistedCount() {
            return this.students.filter(s => s.account_status === 'Blacklisted').length;
        },
 
        filteredStudents() {
            return this.students.filter(student => {
                const nameMatch = student.name ? student.name.toLowerCase().includes(this.searchQuery.toLowerCase()) : false;
                const idMatch = student.id ? student.id.toString().includes(this.searchQuery) : false;
                const emailMatch = student.email ? student.email.toLowerCase().includes(this.searchQuery.toLowerCase()) : false;

                const matchesSearch = nameMatch || idMatch || emailMatch;

                const matchesStatus = this.statusFilter === "All" ||
                    (this.statusFilter === "Placed" && student.placement_status === "Placed") ||
                    (this.statusFilter === "Active" && student.account_status === "Active") ||
                    student.account_status === this.statusFilter;

                const matchesBranch = this.branchFilter === "All" || student.branch === this.branchFilter;

                return matchesSearch && matchesStatus && matchesBranch;
            });
        }
    },
    created() {
        this.fetchStudentsList();
    },
    methods: {
        async fetchStudentsList() {
            try {
                const res = await axios.get('/admin/students');
                this.students = res.data;
            } catch (error) {
                console.error("Error loading students list:", error);
            }
        },
        async updateStatus(id, newStatus) {
            try {
                await axios.post(`/admin/students/update-status`, { student_id: id, status: newStatus });
                const student = this.students.find(s => s.id === id);
                if (student) student.account_status = newStatus;
            } catch (error) {
                alert("Status update karne mein dikkat aayi.");
            }
        },
        getStatusClass(status) {
            if (status === 'Active') return 'stu-pill-active';
            if (status === 'Deactivated') return 'stu-pill-deactive';
            return 'stu-pill-blacklist';
        },
        viewProfile(id) {
            alert("Student profile view modal layout incoming for ID: #STU-" + id);
        }
    }
}
</script>

<style scoped>
@import "../assets/css/AdminStudent.css"
</style>