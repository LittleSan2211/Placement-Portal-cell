<template>
    <div class="modal-overlay" @click.self="$emit('close')">
        <div class="modal-wrapper">
            <!-- Header -->
            <div class="modal-header-block">
                <h3>
                    <i class="bi bi-briefcase-fill" style="color: #4f46e5; margin-right: 8px;"></i>
                    {{ isAdminMode ? 'Create Dynamic Drive (Admin Override)' : 'Launch New Placement Drive' }}
                </h3>
                <i class="bi bi-x-lg modal-close-cross-btn" @click="$emit('close')"></i>
            </div>

            <!-- Form Body -->
            <form @submit.prevent="handleSubmitForm" class="modal-form-body">
                <div class="form-group-item">
                    <label>Job Profile / Title</label>
                    <input type="text" v-model="formData.title" placeholder="e.g. Associate Data Scientist" required />
                </div>

                <!-- Admin specific selector (Vue 2 Standard Option loop) -->
                <div v-if="isAdminMode" class="form-group-item">
                    <label>Assign to Corporate Company</label>
                    <select v-model="formData.company_id" required>
                        <option value="" disabled>Select target corporate channel</option>
                        <option v-for="comp in companiesList" :key="comp.id" :value="comp.id">
                            {{ comp.name }}
                        </option>
                    </select>
                </div>

                <div class="form-group-item">
                    <label>Compensation Package (CTC per Annum)</label>
                    <input type="text" v-model="formData.salary" placeholder="e.g. 12 LPA" required />
                </div>

                <div class="form-group-item">
                    <label>Job Location</label>
                    <input type="text" v-model="formData.location" placeholder="e.g. Bengaluru, India (Hybrid)" required />
                </div>

                <div class="form-group-item">
                    <label>Application Deadline</label>
                    <input type="date" v-model="formData.deadline" required />
                </div>

                <div class="form-group-item">
                    <label>Technical Core Skills Required</label>
                    <textarea v-model="formData.skills" rows="3" placeholder="e.g. Python, SQL, Tableau, Pandas (Comma separated)"></textarea>
                </div>

                <!-- Action Footer -->
                <div class="modal-footer-action-row">
                    <button type="button" class="btn-secondary-cancel" @click="$emit('close')">Cancel</button>
                    <button type="submit" class="btn-indigo-submit">Deploy Drive</button>
                </div>
            </form>
        </div>
    </div>
</template>

<script>
export default {
    name: "CreateDriveModal",
    props: {
        isAdminMode: {
            type: Boolean,
            default: false
        },
        companiesList: {
            type: Array,
            default: () => []
        }
    },
    data() {
        return {
            formData: {
                title: "",
                salary: "",
                location: "",
                deadline: "",
                skills: "",
                company_id: ""
            }
        };
    },
    methods: {
        handleSubmitForm() {
            // Parent dashboard component ko updated data trigger emit karne ke liye
            this.$emit("submit-drive", { ...this.formData });
        }
    }
};
</script>

<style scoped>
@import '../assets/css/ModalPopup.css';
</style>