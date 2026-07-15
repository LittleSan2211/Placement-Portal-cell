import Vue from 'vue'
import VueRouter from 'vue-router'
import HomeView from '../views/HomeView.vue'
import LoginView from '@/views/LoginView.vue'
import LandingPage from '@/views/LandingPage.vue'
import RegisterationView from '@/views/RegisterationView.vue'
import AdminDashboard from '@/views/AdminDashboard.vue'
import AdminPage from '@/components/AdminPage.vue'
import AdminStudent from '@/components/AdminStudent.vue'
import AdminCompany from '@/components/AdminCompany.vue'
import AdminDrive from "@/components/AdminDrive.vue"
import CompanyDashboard from '@/views/CompanyDashboard.vue'
import CompanyHome from '@/components/CompanyHome.vue'
import CompanyDrives from '@/components/CompanyDrives.vue'
import CompanyApplicant from '@/components/CompanyApplicant.vue'
import StudentDashboard from '@/views/StudentDashboard.vue'
import StudentHome from '@/components/StudentHome.vue'
import StudentJobexplore from '@/components/StudentJobexplore.vue'
import StudentAppliedhistory from '@/components/StudentAppliedhistory.vue'
import StudentProfile from '@/components/StudentProfile.vue'


Vue.use(VueRouter)

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView,
    children: [
      {
        path: '',
        component: LandingPage
      },
      {
        path: '/login',
        name: 'login',
        component: LoginView
      },
      {
        path: '/register',
        component: RegisterationView
      },
    ]
  },
  {
    path: '/about',
    name: 'about',
    // route level code-splitting
    // this generates a separate chunk (about.[hash].js) for this route
    // which is lazy-loaded when the route is visited.
    component: () => import(/* webpackChunkName: "about" */ '../views/AboutView.vue')
  },
  {
    path: '/admin-dashboard',
    name: 'admin-dashboard',
    component: AdminDashboard,
    children: [
      {
        path: '',
        component: AdminPage
      },
      {
        path: "students",
        component: AdminStudent
      },
      {
        path: "company",
        component: AdminCompany
      },
      {
        path: "drives",
        component: AdminDrive
      }
    ]
  },
  {
    path: '/company-dashboard',
    name: 'company-dashboard',
    component: CompanyDashboard,
    children: [
      {
        path: '',
        component: CompanyHome
      },
      {
        path: "manage-drives",
        component: CompanyDrives
      },
      {
        path: "manage-applicants",
        component: CompanyApplicant
      }
    ]
  },
  {
    path: "/student",
    name: "student",
    component: StudentDashboard,
    children: [
      {
        path: "",
        component: StudentHome
      },
      {
        path : "profile",
        component: StudentProfile
      },
      {
        path: "job-explore",
        component: StudentJobexplore
      },
      {
        path: "applications",
        component: StudentAppliedhistory
      }
    ]
  }
]

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (to.hash) {
      return {
        selector: to.hash,
        behavior: "smooth"
      }
    }
    return savedPosition || { x: 0, y: 0 }
  }
})

export default router
