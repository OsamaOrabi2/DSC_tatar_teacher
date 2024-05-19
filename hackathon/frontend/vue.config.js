/*
const { defineConfig } = require('@vue/cli-service')
module.exports = defineConfig({
  transpileDependencies: true
})
*/
// vue.config.js

module.exports = {
  devServer: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000', // Django backend URL
        changeOrigin: true
      }
    }
  },

  pluginOptions: {
    vuetify: {
			// https://github.com/vuetifyjs/vuetify-loader/tree/next/packages/vuetify-loader
		}
  }
};
