<template>
  <div id="device_menu">
    <img 
      id="switch_device"
      alt="workgroup switch"
      draggable="true"
      @dragstart="dragstartHandler"
      :src="deviceSrc"
    >
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'

export default defineComponent({
  props: {
    deviceSrc: String
  },
  setup(props, ctx){
    console.log(props)
    let dragged: HTMLElement = null;
    
    const dragstartHandler = (event: DragEvent) => {
      dragged = event.target as HTMLElement
      // event.dataTransfer.setData("text", dragged.id)
      console.log(dragged)
      ctx.emit("setDragged", dragged)
    }

    return { dragstartHandler }
  }
})
</script>


<style lang="scss">
#device_menu{
  background-color: #dddddd;
}

</style>