module.exports = {
  css: {
    loaderOptions: {
      scss: {
        additionalData: '@import "./src/assets/scss/prepends.scss";'
      }
    }
  }
};