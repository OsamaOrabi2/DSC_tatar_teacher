// src/main.js

import { createApp } from 'vue';
import App from './App.vue';
import vuetify from './plugins/vuetify';
import '@mdi/font/css/materialdesignicons.css'; // Ensure you are using css-loader

createApp(App)
  .use(vuetify)
  .mount('#app');

