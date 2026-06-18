import { createApp } from 'vue'
import { createPinia } from 'pinia'
import Vant from 'vant'
import 'vant/lib/index.css'
import '@vant/touch-emulator'

import App from './App.vue'
import router from './router'
import './assets/styles/main.less'
import AppTabbar from './components/AppTabbar.vue'

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(Vant)

app.component('AppTabbar', AppTabbar)

app.mount('#app')
