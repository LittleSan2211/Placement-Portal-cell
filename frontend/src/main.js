import Vue from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import axios from 'axios';

axios.defaults.baseURL = 'http://localhost:5000';
axios.defaults.withCredentials = true;

// Browser ki najar mein localhost aur 127.0.0.1 do alag domains (origins) hain. 
// Jab frontend localhost se request 127.0.0.1 par bhejta hai, 
// toh browser security (CORS policy) ke chalte cookies ko accept nahi 
// karta ya unhe browser mein save karne se rok deta hai.

// ====================================================================================
// PART 1: REQUEST INTERCEPTOR (Jaate waqt ka Chowkidar)
// Iska kaam hai: Har request ke saath automatic 'accessToken' attach karna, 
// taaki hume har file (Vue component) mein baar-baar token na bhejna pade.
// ====================================================================================

axios.interceptors.request.use(
  (config) => {   //config ek JavaScript Object hai, jisme tumhari request ki saari janam-kundali (details) hoti hai.
    // 1. Browser ke cupboard (localStorage) se token nikalte hain
    const token = localStorage.getItem('accessToken');

    // 2. Agar token mil jata hai, toh use request ke packet par (Header mein) chipka dete hain
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
 
    // 3. Request ko aage backend (Flask) ki taraf bhej dete hain
    return config;
  },
  (error) => {
    // Agar request bhejne mein hi koi dikkat aaye toh error return karo
    return Promise.reject(error);
  }
)

// ====================================================================================
// PART 2: RESPONSE INTERCEPTOR (Aate waqt ka Chowkidar)
// Iska kaam hai: Server se aane wale 401 (Expired Token) error ko pakadna aur 
// background mein token ko naya (refresh) karke request ko dobara bhej dena.
// ====================================================================================

axios.interceptors.response.use(
  (response) => {
    // 1. Agar backend ne data sahi-salamat bhej diya (Status 200), toh bina ched-chad ke data aage bhej do
    return response;
  },
  async (error) => {
    // 2. Agar koi error aaya, toh us request ki janam-kundali (config) nikalte hain
    const originalRequest = error.config;

    // 3. CHECK: Kya error '401' (Expired) hai? Aur kya yeh request pehle retry nahi hui hai?
    if (error.response && error.response.status === 401 && !originalRequest._retry) {

      // Is request par 'retry' ka sticker laga do taaki yeh loop mein na phanse 
      originalRequest._retry = true;  // Loop se bachne ke liye tag lagaya

      try {
        // 4. CHUPKE SE ACTION: Backend ke '/auth/refresh' route par POST request maro
        // withCredentials isliye taaki browser cookie mein rakha 'refreshToken' apne aap bhej de
        const freshAxios = axios.create({
          baseURL: 'http://localhost:5000',
          withCredentials: true
        });

        const res = await freshAxios.post('/auth/refresh', {});

        // 5. SUCCESS: Agar backend ne naya accessToken de diya
        if (res.status === 200) {
          const newAccessToken = res.data.accessToken;

          // Naye token ko cupboard (localStorage) mein update karo
          localStorage.setItem('accessToken', newAccessToken);

          // Purani failed request ke sir par naya token lagao
          originalRequest.headers['Authorization'] = `Bearer ${newAccessToken}`;

          // Us purani request ko FIR SE EXECUTE (Retry) kar do!
          return axios(originalRequest)
        }
      }
      catch (refreshError) {
        // 6. FAIL: Agar 7 din purana Refresh Token bhi expire ho gaya, toh koi chara nahi hai, logout karo
        console.error("Refresh token bhi expire ho gaya. Logging out...", refreshError);
        localStorage.removeItem('accessToken');
        window.location.href = '/login' // Direct login page par bhej do
        return Promise.reject(refreshError);
      }
    }
    // Agar error 401 nahi hai (jaise 404 ya 500), toh error ko normal tarike se component tak jaane do
    return Promise.reject(error);
  }
)

Vue.config.productionTip = false

new Vue({
  router,
  store,
  render: h => h(App)
}).$mount('#app')
