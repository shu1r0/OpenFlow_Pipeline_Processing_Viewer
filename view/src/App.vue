<template>
  <header id="header">
    <h1>P2V</h1>
  </header>

  <!-- navigation -->
  <div id="nav">
    <div class="nav-item">
      <router-link to="/">Mininet</router-link>
    </div>
    <div class="nav-item">
      <router-link to="/tracing_net">trace net</router-link>
    </div>
    <!-- <div class="nav-item">
      <router-link to="/tracing_packet">trace packet</router-link>
    </div> -->
  </div>

  <!-- main content wrapper -->
  <div id="wrapper">
    <router-view v-slot="{ Component }">
      <keep-alive>
        <component :is="Component" />
      </keep-alive>
    </router-view>
  </div>

</template>

<script lang="ts">
import { defineComponent, onMounted } from "vue";
import { DummyRemoteClient, RemoteClient, WSClient } from "./scripts/remote/remoteClient";
import { changeableVNet } from './scripts/vnet/vnet'

import Configuration from './config/config'

export default defineComponent({
  name: "App",
  setup(){

    /**
     * remote client and set client to vnet
     */
    let remoteClient: RemoteClient = new WSClient(Configuration.WS_SERVER_ADDRESS, Configuration.WS_SERVER_PORT, Configuration.WS_NAMESPACE)
    if(Configuration.USE_DUMMY_CLIENT){
      remoteClient = new DummyRemoteClient()
    }
    changeableVNet.setRemoteClient(remoteClient)


    /**
     * document title
     */
    document.title = "P2V"

    onMounted(() => {
      /**
       * connection to remote client
       */
      remoteClient.connect()
    })
  }
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
  color: $black;

  display: grid;
  grid-template-areas: 
    " header header"
    " nav wrapper";
  grid-auto-rows: 
    5rem
    minmax(50rem, auto);
  grid-auto-columns: 
    5rem
    auto;
  grid-gap: 1rem;
  
  #header{
    grid-area: header;
    // background-color: #f0f0f9;
    border-bottom: 0.5rem solid $navy;
    // padding: 1.5rem;
    h1{
      margin: 1rem 2rem;
      font-size: 2.5rem;
    }
  }

  #nav {
    grid-area: nav;
    border-right: 1px solid $navy;
    background-color: $white;
    word-break : break-all;  // refrain
    font-size: 1.3rem;
    // padding: 30px;

    .nav-item{
      display: grid;
      background-color: $white;
      width: 5rem;
      height: 5rem;
      justify-items: center;

      a {
        font-weight: bold;
        color: $navy;
        border: 1px solid $navy;
      }
      a.router-link-exact-active {
        color: $white;
        background-color: $navy;
        border: 2px solid $navy;
      }
    }
  }

  #wrapper{
    grid-area: wrapper;
    // background-color: #42b983;
  }

}

</style>
