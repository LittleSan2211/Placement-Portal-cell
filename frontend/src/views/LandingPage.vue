<template>
    <div class="landing-portal-root">
        <!-- Ambient decorative blobs across the theme -->
        <div class="portal-ambient-blob blob-top"></div>
        <div class="portal-ambient-blob blob-mid"></div>

        <!-- HERO SECTION -->
        <div class="hero" id="home">
            <div class="hero-overlay-shade"></div>
            <div class="hero-h1">
                <h1>Welcome To The <span>Placement Portal</span></h1>
                <p>Empowering Students & Recruiters Through Smart Placements</p>
                <div class="btnSection">
                    <!-- 🔥 @click listener lagaya login par bhejnewala -->
                    <button class="btn-primary" @click="goToLogin()">Join US</button>
                    <button class="btn-secondary">Reports</button>
                </div>
            </div>
        </div>

        <!-- ABOUT SECTION -->
        <div class="about" id="about">
            <div class="about-container-card">
                <div class="badge-pill">About Us</div>
                <p class="about-p1">Find Out More About Us</p>
                <p class="about-p2">PS Study Placement Portal</p>
                <p class="about-p3">Building The Future Of Smart Campus Placements</p>
                
                <h1 class="about-h12">Creating Smarter Connections Between Talent & Recruiters</h1>
                <p class="about-p12">
                    The PS Portal creates smarter and more efficient connections between talented
                    students and recruiters through a modern, automated placement ecosystem.<br><br>
                    Designed to simplify the recruitment journey, the platform enables students
                    to explore opportunities, track applications, and manage their placement progress seamlessly, 
                    while recruiters can efficiently conduct placement drives, shortlist
                    candidates, and streamline hiring workflows. By combining intelligent automation
                    with a student-centric experience, PS Portal aims to transform traditional placement
                    processes into a faster, more transparent, and opportunity-driven ecosystem for both
                    students and organizations.
                </p>
                <div class="about-p13-wrapper">
                    <p class="about-p13"><i class="bi bi-globe"></i> PS STUDY PROGRAMS</p>
                </div>
            </div>
        </div>

        <!-- ECOSYSTEM SECTION -->
        <div class="userSection" id="userSection">
            <div class="u-hs">
                <h1 class="u-h1">Our Placement Ecosystem</h1>
                <p class="u-p1">We empower students with meaningful career opportunities and help recruiters discover<br>the right talent through a modern and streamlined placement ecosystem.</p>
            </div>
            
            <div class="u-bs">
                <div class="u-bs1">
                    <div class="u-icon">
                        <i class="bi bi-mortarboard"></i>
                    </div>
                    <h1>PS Study Student</h1>
                    <p>Students enrolled in PS study programs consult this section to understand the operational process.</p>
                </div>
                
                <div class="u-bs2">
                    <div class="u-icon">
                        <i class="bi bi-building"></i>
                    </div>
                    <h1>Recruiter</h1>
                    <p>Recruiters refer to this section for detailed information on the entire process of the placement.</p>
                </div>
                
                <div class="u-bs3">
                    <div class="u-icon">
                        <i class="bi bi-diagram-3"></i>
                    </div>
                    <h1>Partnership</h1>
                    <p>Industries refer to this section if their aim to contribute more substantially beyond the job offerings.</p>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: "LandingPage",
    // 🔥 Methods block add kiya jisme redirect ka logic hai
    methods: {
        goToLogin() {
            this.$router.push('/login'); // Yeh use seedha login route par push kar dega
        }
    }
}
</script>