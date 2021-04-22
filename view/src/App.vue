<template>
  <header id="header">
    <h1>仮タイトル</h1>
  </header>
  <div id="nav">
    <div class="nav-item">
      <router-link to="/">CreatingVet</router-link>
    </div>
    <div class="nav-item">
      <router-link to="/trace">Trace</router-link>
    </div>
  </div>
  <div id="wrapper">
    <router-view />
  </div>
</template>

<style lang="scss">

html {
  font-size: 62.5%; /* 1rem -> 10px */
}

#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  // text-align: center;
  color: #2c3e50;
  display: grid;
  grid-template-areas: 
    " header header"
    " nav wrapper";
  grid-auto-rows: 
    10rem
    minmax(50rem, auto);
  grid-auto-columns: 
    5rem
    auto;
  grid-gap: 1rem;
  
  #header{
    grid-area: header;
    background-color: #f0f0f9;
  }

  #nav {
    grid-area: nav;
    background-color: #f0f0f9;
    word-break : break-all;  // refrain
    font-size: 1.5rem;
    // padding: 30px;
    .nav-item{
      display: grid;
      background-color: antiquewhite;
      width: 5rem;
      height: 5rem;
      justify-items: center;
      a {
        font-weight: bold;
        color: #2c3e50;
      }
      a.router-link-exact-active {
        color: #42b983;
      }
    }
  }

  #wrapper{
    grid-area: wrapper;
    // background-color: #42b983;
  }

}

</style>
