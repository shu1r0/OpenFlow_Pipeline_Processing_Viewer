<template>
  <header id="header">
    <h1>タイトル</h1>
  </header>

  <div id="nav">
    <div class="nav-item">
      <router-link to="/">Mininet</router-link>
    </div>
    <div class="nav-item">
      <router-link to="/trace">Trace</router-link>
    </div>
  </div>

  <div id="wrapper">
    <router-view v-slot="{ Component }">
      <keep-alive>
        <component :is="Component" />
      </keep-alive>
    </router-view>
  </div>
</template>

<script lang="ts">
import { defineComponent } from "vue";

export default defineComponent({
  name: "App"
})
</script>

<style lang="scss">

html {
  font-size: 62.5%; /* 1rem -> 10px */
}

#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  display: grid;
  grid-template-areas: 
    " header header"
    " nav wrapper";
  grid-auto-rows: 
    7rem
    minmax(50rem, auto);
  grid-auto-columns: 
    5rem
    auto;
  grid-gap: 1rem;
  
  #header{
    grid-area: header;
    // background-color: #f0f0f9;
    border-bottom: 0.5rem solid #2c3e50;
    // padding: 1.5rem;
    h1{
      margin: 1rem 2rem;
      font-size: 2.5rem;
    }
  }

  #nav {
    grid-area: nav;
    background-color: #f0f0f9;
    word-break : break-all;  // refrain
    font-size: 1.3rem;
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
