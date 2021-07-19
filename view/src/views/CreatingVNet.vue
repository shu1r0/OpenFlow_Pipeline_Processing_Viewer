<template>
  <div 
    id="creating_vnet_view"
    class="creating_vnet">

    <MenuDevices
      id="device_menu"
      @setDragged="setDragged" />
    <div
      id="vnet_canvas"
      @drop="dropHandler"
      @dragover="dragoverHandler" />

  </div>
</template>

<script lang="ts">
import { defineComponent, onMounted } from 'vue'
import MenuDevices from '../components/MenuDevices.vue'
import { VNet } from '../vnet/vnet'
import { CollectionReturnValue } from 'cytoscape'

import { DummyRemoteClient, RemoteClient } from '../api/remoteClient'
import { DEVICE_TYPE } from '@/vnet/devices'

export default defineComponent({
  name: "CreatingVNet",
  components: {
    MenuDevices
  },
  prop: {},
  setup(props, ctx){
    // cytescape obj
    let vnet: VNet = null
    // dragged element (if no element is dragged, this is null)
    let dragged: HTMLImageElement = null
    // client
    const grpc_client: RemoteClient = new DummyRemoteClient('10.0.0.109', '50051')

    onMounted(()=>{
      if(vnet === null){
        vnet = new VNet(document.getElementById('vnet_canvas'))
      }
    })
    
    /**
     * handle setDragged event from MenuDevices component
     * @param d - dragged element
     */
    const setDragged = (d: HTMLImageElement) => {
      dragged = d
    }

    /**
     * dragover event handler. prevent default action.
     * @param event
     */
    const dragoverHandler = (event: DragEvent) => {
      event.preventDefault()
    }

    /**
     * Drop event handler. 
     * Create the device when an element is dropped on the canvas
     * @param event
     */
    const dropHandler = (event: DragEvent) => {
      event.preventDefault()
      const dropTarget: HTMLImageElement = event.target as HTMLImageElement
      const offsetX: number = event.offsetX
      const offsetY: number = event.offsetY 
      
      // where to make the switch
      if(dragged){
        const createdDvice: CollectionReturnValue = vnet.addDevice(dragged, offsetX, offsetY)
        grpc_client.addDevice(dragged.className as DEVICE_TYPE, createdDvice.id())
        dragged = null
      }
    }

    return { 
      setDragged, 
      dragoverHandler, 
      dropHandler 
    }
  }
})
</script>

<style lang="scss">
.creating_vnet{
  // background-color: #eeeeee;

  #vnet_canvas{
    position: relative;  // basis for the position of child elements
    height: 1000px;
    width: auto;

    *{
      position: absolute;
    }
  }
}
</style>