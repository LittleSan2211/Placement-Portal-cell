<template>
    <section class="comp-container">
        <div class="comp-header-row">
            <div class="comp-header-left">
                <h3>Corporate Partner Management</h3>
                <p>Approve new profiles, analyze ranking sheets, and handle system level accessibility.</p>
            </div>
            <div class="comp-header-right">
                <button class="comp-export-btn"><i class="bi bi-download"></i><span>Export Partner Sheet</span></button>
            </div>
        </div>

        <p v-if="statError" class="comp-error-banner">
            <i class="bi bi-exclamation-triangle-fill"></i> {{ statError }}
        </p>

        <div class="comp-metrics-grid">
            <div class="comp-metric-card">
                <div class="comp-icon-box comp-blue-box"><i class="bi bi-buildings-fill"></i></div>
                <span class="comp-card-label">TOTAL COMPANIES</span>
                <span class="comp-card-value">{{ metrics.total }}</span>
                <p class="comp-card-sub">Registered hiring firms</p>
            </div>
            <div class="comp-metric-card">
                <div class="comp-icon-box comp-orange-box"><i class="bi bi-clock-history"></i></div>
                <span class="comp-card-label">PENDING VERIFICATION</span>
                <span class="comp-card-value-warning">{{ metrics.pending }}</span>
                <p class="comp-card-sub">Profiles awaiting verification</p>
            </div>
            <div class="comp-metric-card">
                <div class="comp-icon-box comp-green-box"><i class="bi bi-shield-check"></i></div>
                <span class="comp-card-label">TOTAL APPROVED</span>
                <span class="comp-card-value">{{ metrics.approved }}</span>
                <p class="comp-card-sub">Verified active networks</p>
            </div>
            <div class="comp-metric-card">
                <div class="comp-icon-box comp-red-box"><i class="bi bi-slash-circle-fill"></i></div>
                <span class="comp-card-label">BLACKLISTED</span>
                <span class="comp-card-value-danger">{{ metrics.blacklisted }}</span>
                <p class="comp-card-sub">Banned due to compliance skip</p>
            </div>
        </div>

        <div class="comp-split-row">
            <div class="comp-split-left-table">
                <h3>New Validation Requests</h3>
                <div class="comp-table-responsive">
                    <table class="comp-inner-table">
                        <thead>
                            <tr>
                                <th>Company Details</th>
                                <th>Industry / Sector</th>
                                <th>Location</th>
                                <th>Validations</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="comp in pendingList" :key="comp.id">
                                <td class="comp-title-td">{{ comp.name }}</td>
                                <td><span class="comp-sector-badge">{{ comp.industry }}</span></td>
                                <td><i class="bi bi-geo-alt text-muted"></i> {{ comp.location }}</td>
                                <td class="comp-action-inline-cell">
                                    <button class="comp-mini-btn comp-btn-check"
                                        @click="triggerAction(comp.id, 'Approve')" title="Approve Company"><i
                                            class="bi bi-check-lg"></i></button>
                                    <button class="comp-mini-btn comp-btn-cross"
                                        @click="triggerAction(comp.id, 'Reject')" title="Reject Profile"><i
                                            class="bi bi-x-lg"></i></button>
                                </td>
                            </tr>
                            <tr v-if="pendingList.length === 0">
                                <td colspan="4" class="comp-empty-state-text">Abhi koi nayi registration request pending
                                    nahi hai.</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <div class="comp-split-right-ranking">
                <h3>Top 10 High-Package Partners</h3>
                <div class="comp-ranking-stack">
                    <div v-for="(partner, idx) in topPartners" :key="idx" class="comp-ranking-tile">
                        <div class="comp-tile-left-block">
                            <span class="comp-idx-num">0{{ idx + 1 }}</span>
                            <div class="comp-text-avatar">{{ partner.name.charAt(0) }}</div>
                            <div class="comp-tile-info">
                                <h4>{{ partner.name }}</h4>
                                <p>{{ partner.industry }}</p>
                            </div>
                        </div>
                        <div class="comp-tile-right-block">
                            <span class="comp-salary-pill">{{ (partner.max_salary / 100000).toFixed(1) }} LPA</span>
                        </div>
                    </div>
                    <div v-if="topPartners.length === 0" class="comp-empty-state-text">No salary statistics tracks
                        tracked yet.</div>
                </div>
            </div>
        </div>

        <div class="comp-master-table-wrapper">
            <div class="comp-table-header-controls">
                <h3>Corporate Database Directory</h3>
                <div class="comp-search-box">
                    <i class="bi bi-search"></i>
                    <input type="text" v-model="searchQuery" placeholder="Search corporate by name or domain sector...">
                </div>
            </div>

            <table class="comp-master-grid">
                <thead>
                    <tr>
                        <th>Partner ID</th>
                        <th>Corporate Name</th>
                        <th>Industry Domain</th>
                        <th>Geographical Location</th>
                        <th>Workflow Status</th>
                        <th>Administrative Control</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="company in filteredCompanies" :key="company.id">
                        <td class="comp-mono-id">#COMP-{{ company.id }}</td>
                        <td class="comp-title-td">{{ company.name }}</td>
                        <td><span class="comp-sector-badge">{{ company.industry }}</span></td>
                        <td>{{ company.location }}</td>
                        <td>
                            <span
                                :class="['comp-status-pill', company.is_blacklist ? 'comp-pill-black' : (company.approval_status === 'Approved' ? 'comp-pill-green' : 'comp-pill-orange')]">
                                {{ company.is_blacklist ? 'Blacklisted' : company.approval_status }}
                            </span>
                        </td>
                        <td class="comp-final-actions">
                            <button v-if="!company.is_blacklist" class="comp-action-btn comp-ban-op"
                                title="Blacklist Corporate" @click="triggerAction(company.id, 'Blacklist')"><i
                                    class="bi bi-slash-circle"></i></button>
                            <button v-else class="comp-action-btn comp-activate-op" title="Restore Visibility"
                                @click="triggerAction(company.id, 'Activate')"><i
                                    class="bi bi-check-circle"></i></button>
                            <button class="comp-action-btn comp-remove-op" title="Delete Profile Records"
                                @click="triggerAction(company.id, 'Remove')"><i class="bi bi-trash3"></i></button>
                        </td>
                    </tr>
                    <tr v-if="filteredCompanies.length === 0">
                        <td colspan="6" class="comp-empty-state-text">System database directories are empty or
                            unmatched.</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </section>
</template>

<script>
import axios from 'axios'

export default {
    name: "AdminCompany",
    data() {
        return {
            metrics: { total: 0, pending: 0, approved: 0, blacklisted: 0 },
            companies: [],
            topPartners: [],
            searchQuery: "",
            statError: ""
        }
    },
    computed: {
        pendingList() {
            return this.companies.filter(c => c.approval_status === 'PENDING' && !c.is_blacklist);
        },
        filteredCompanies() {
            return this.companies.filter(c => {
                return c.name.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
                    c.industry.toLowerCase().includes(this.searchQuery.toLowerCase());
            });
        }
    },
    created() {
        this.fetchCorporateNetwork();
    },
    methods: {
        async fetchCorporateNetwork() {
            try {
                this.statError = "";
                const res = await axios.get('/admin/companies');
                this.metrics = res.data.metrics;
                this.companies = res.data.companies;
                this.topPartners = res.data.topPartners;
            } catch (err) {
                this.statError = "Corporate network registers synchronizing errors.";
                console.error(err);
            }
        },
        async triggerAction(id, actionName) {
            if (actionName === 'Remove' && !confirm("Kya aap sach me is company ka data delete karna chahte hain?")) return;
            try {
                this.statError = "";
                await axios.post('/admin/companies/action', { company_id: id, action: actionName });
                await this.fetchCorporateNetwork(); // Auto refresh analytics and states maps instantly
            } catch (err) {
                this.statError = `Operation ${actionName} transaction aborted by database validation constraints.`;
            }
        }
    }
}
</script>

<style scoped>
@import "../assets/css/AdminCompany.css";
</style>