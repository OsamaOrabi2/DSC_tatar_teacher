// src/plugins/vuetify.js

import { createVuetify } from 'vuetify';
import 'vuetify/styles'; // Global CSS has to be imported
import { aliases, mdi } from 'vuetify/iconsets/mdi';

export default createVuetify({
  icons: {
    defaultSet: 'mdi',
    aliases,
    sets: {
      mdi,
    },
  },
});
