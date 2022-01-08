<template>
  <div id="device_menu">
    <img 
      id="switch_device"
      :class="DEVICE_TYPE.OFSWITCH"
      alt="workgroup switch"
      draggable="true"
      @dragstart="dragstartHandler"
      :src="switchSrc"
    >
    <img 
      id="workstation_device"
      :class="DEVICE_TYPE.HOST"
      alt="workstation"
      draggable="true"
      @dragstart="dragstartHandler"
      :src="workstationSrc"
    >
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue'
import { DEVICE_TYPE } from '../scripts/vnet/devices'

export default defineComponent({
  setup(props, ctx){
    
    // image sources
    let switchSrc = ref("img/workgroup_switch.jpg")
    let workstationSrc = ref("img/workstation.jpg")

    /**
     * dragstart event handler. 
     * emit 'setDragged' event
     * @param event 
     * @returns void 
     */
    const dragstartHandler = (event: DragEvent) => {
      const dragged = event.target as HTMLImageElement
      /**
       * noticefy to drag
       * @property {HTMLImageElement} dragged - dragged element
       */
      ctx.emit("setDragged", dragged)
    }

    return { 
      switchSrc,
      workstationSrc,
      dragstartHandler,
      DEVICE_TYPE
    }
  }
})
</script>


<style lang="scss">
#device_menu{
  // background-color: #dddddd;
  height: 9rem;
  padding: 0 1rem;
  border-bottom: 3px solid #dddddd;
  img{
    margin: 1rem 1.5rem;
  }
}

</style>