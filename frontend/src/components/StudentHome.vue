<template>
    <div class="sd-analytics-container">
        
        <div class="sd-metrics-row">
            <div class="sd-card-metric">
                <div class="sd-icon-box sd-blue-tint"><i class="bi bi-send-check-fill"></i></div>
                <div class="sd-meta-data">
                    <span class="sd-lbl-text">Total Applied</span>
                    <h2 class="sd-value-num">{{ metrics.applied }}</h2>
                </div>
            </div>
            
            <div class="sd-card-metric">
                <div class="sd-icon-box sd-amber-tint"><i class="bi bi-person-check-fill"></i></div>
                <div class="sd-meta-data">
                    <span class="sd-lbl-text">Shortlisted Drives</span>
                    <h2 class="sd-value-num">{{ metrics.shortlisted }}</h2>
                </div>
            </div>
            
            <div class="sd-card-metric">
                <div class="sd-icon-box sd-green-tint"><i class="bi bi-trophy-fill"></i></div>
                <div class="sd-meta-data">
                    <span class="sd-lbl-text">Offers Received</span>
                    <h2 class="sd-value-num">{{ metrics.offers }}</h2>
                </div>
            </div>
        </div>

        <div class="sd-section-wrapper">
            <h4 class="sd-block-title">
                <i class="bi bi-lightning-charge-fill"></i> Elite Openings (High CTC Packages)
            </h4>
            
            <div class="sd-high-packages-grid">
                <div v-for="(job, index) in highPackages" :key="index" class="sd-pkg-card">
                    <div class="sd-pkg-header">
                        <span class="sd-company-badge">{{ job.company_name }}</span>
                        <span class="sd-pkg-amount">{{ job.package_lpa }} LPA</span>
                    </div>
                    <h4 class="sd-role-txt">{{ job.role_title }}</h4>
                    <p class="sd-loc-txt"><i class="bi bi-geo-alt-fill"></i> {{ job.location }}</p>
                </div>
                
                <div v-if="highPackages.length === 0" class="sd-empty-box-span">
                    No high packages listed currently.
                </div>
            </div>
        </div>

        <div class="sd-bottom-split-grid">
            
            <div class="sd-trends-table-card">
                <h4 class="sd-block-title">
                    <i class="bi bi-graph-up-arrow"></i> Market Demand Matrix (Trending Roles)
                </h4>
                
                <div class="sd-table-scroll-wrapper">
                    <table class="sd-custom-trends-table">
                        <thead>
                            <tr>
                                <th>#</th>
                                <th>Trending Job Profile</th>
                                <th class="sd-txt-center">Active Openings</th>
                                <th class="sd-txt-right">Avg Package</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="(row, idx) in trendingRoles" :key="idx">
                                <td>{{ idx + 1 }}</td>
                                <td class="sd-bold-td">{{ row.role }}</td>
                                <td class="sd-txt-center">
                                    <span class="sd-count-badge">{{ row.total_companies }}</span>
                                </td>
                                <td class="sd-txt-right sd-premium-ctc">{{ row.avg_package }} LPA</td>
                            </tr>
                            <tr v-if="trendingRoles.length === 0">
                                <td colspan="4" class="sd-no-data-msg">No ongoing placement trends found.</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <div class="sd-skills-panel-card">
                <h4 class="sd-block-title">
                    <i class="bi bi-cpu-fill"></i> Essential Skills in Trend
                </h4>
                <p class="sd-panel-desc">Master these highly requested skills based on current recruitment drives.</p>
                
                <div class="sd-skills-tags-cluster">
                    <span v-for="(skill, sIdx) in trendingSkills" :key="sIdx" class="sd-skill-pill-tag">
                        <i class="bi bi-check2-circle"></i> {{ skill }}
                    </span>
                    <div v-if="trendingSkills.length === 0" class="sd-empty-skills">Updating hot skill parameters...</div>
                </div>
            </div>

        </div>

    </div>
</template>

<script>
import axios from 'axios';

export default {
    name: "StudentDashboardHome",
    data() {
        return {
            metrics: { applied: 0, shortlisted: 0, offers: 0 },
            highPackages: [],
            trendingRoles: [],  
            trendingSkills: []  
        };
    },
    created() {
        this.loadTopMetrics();
        this.loadHighPackages();
        this.loadMarketTrends(); 
    },
    methods: {
        async loadTopMetrics() {
            try {
                const res = await axios.get('/student/dashboard/top-metrics');
                this.metrics = res.data;
            } catch (err) {
                console.error("Error loading top cards:", err);
            }
        },
        async loadHighPackages() {
            try {
                const res = await axios.get('/student/dashboard/high-packages');
                this.highPackages = res.data;
            } catch (err) {
                console.error("Error loading high packages:", err);
            }
        },
        async loadMarketTrends() {
            try {
                const res = await axios.get('/student/dashboard/market-trends');
                this.trendingRoles = res.data.trending_roles;
                this.trendingSkills = res.data.trending_skills;
            } catch (err) {
                console.error("Error loading intelligence grids:", err);
            }
        }
    }
}
</script>
<style scoped> 
@import "../assets/css/StudentHome.css";
</style>