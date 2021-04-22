<template>
  <div id="device_menu">
    <img 
      id="switch_device"
      alt="workgroup switch"
      draggable="true"
      @dragstart="dragstartHandler"
      :src="switchSrc"
    >
    <img 
      id="workstation_device"
      alt="workstation"
      draggable="true"
      @dragstart="dragstartHandler"
      :src="workstationSrc"
    >
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue'

export default defineComponent({
  setup(props, ctx){
    
    // image sources
    let switchSrc = ref("img/workgroup_switch.jpg")
    let workstationSrc = ref("img/workstation.jpg")

    let dragged: HTMLImageElement = null;
    /**
     * dragstart event handler
     * @param {DragEvent} event 
     * @returns {void} 
     */
    const dragstartHandler = (event: DragEvent) => {
      dragged = event.target as HTMLImageElement
      /**
       * noticefy to drag
       * @property {HTMLImageElement} dragged - dragged element
       */
      ctx.emit("setDragged", dragged)
    }

    return { 
      switchSrc,
      workstationSrc,
      dragstartHandler
    }
  }
})
</script>


<style lang="scss">
#device_menu{
  // background-color: #dddddd;
  height: 10rem;
  padding: 1rem;
  border-bottom: 3px solid #dddddd;
  img{
    margin: 1rem;
  }
}

</style>