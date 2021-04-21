<template>
  <div 
    id="creating_vnet_view"
    class="creating_vnet">
    <MenuDevices
      id="device_menu"
      deviceSrc="img/workgroup_switch.jpg"
      @setDragged="setDragged" />
    <div 
      id="vnet_canvas"
      @drop="dropHandler"
      @dragover="dragoverHandler" />
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import MenuDevices from '../components/MenuDevices.vue'

export default defineComponent({
  name: "CreatingVNet",
  components: {
    MenuDevices
  },
  prop: {},
  setup(props, ctx){
    console.log(props)

    let dragged: HTMLElement = null
    
    const setDragged = (d: HTMLElement) => {
      dragged = d
    }

    const dragoverHandler = (event: DragEvent) => {
      event.preventDefault()
      const dragged: HTMLElement = event.target as HTMLElement
      // console.log(dragged)
    }

    const dropHandler = (event: DragEvent) => {
      event.preventDefault()
      const dropTarget: HTMLElement = event.target as HTMLElement
      const draggedCopy = dragged.cloneNode(true)
      dropTarget.appendChild(draggedCopy)
      
    }

    return { setDragged, dragoverHandler, dropHandler }
  }
})
</script>

<style lang="scss">
.creating_vnet{
  background-color: #eeeeee;

  #vnet_canvas{
    height: 1000px;
    width: 1000px;
  }
}
</style>