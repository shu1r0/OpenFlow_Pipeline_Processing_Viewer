<template>
  <div
    id="tracing_vnet_view"
    class="tracing_vnet">
    
    <div
      id="tracing_vnet_canvas" />

    <button @click="onClick()">test arc</button>
  </div>
</template>

<script lang="ts">
import { defineComponent, onActivated, onDeactivated, onMounted } from 'vue'

import { changeableVNet, TracingVNet } from '../vnet/vnet'

export default defineComponent({
  name: 'TracingVNet',
  setup() {
    onMounted(() => {
      console.log("TracingVNet view mounted")
    })
    let vnet: TracingVNet = null
    onActivated(() => {
      console.log("TracingVNet view activated")
      const e = document.getElementById("tracing_vnet_canvas")
      vnet = new TracingVNet(null, e, changeableVNet)
      console.log(vnet)
    })

    onDeactivated(() => {
      console.log("TracingVNet view deactivated")
      vnet.cytoscape.destroy()
      vnet = null
    })

    const onClick = () => {
      vnet.addPacketEdge("h0", "s0")
    }
    return {
      onClick
    }
  },
})
</script>


<style lang="scss">
.tracing_vnet{
  // background-color: #eeeeee;

  #tracing_vnet_canvas{
    position: relative;  // basis for the position of child elements
    height: 1000px;
    width: auto;

    *{
      position: absolute;
    }
  }
}
</style>
