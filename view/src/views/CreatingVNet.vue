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
import { createDevice, createEdge } from '../vnet/factory'
import cytoscape, { EventObject } from 'cytoscape'
import { Core } from "cytoscape"

export default defineComponent({
  name: "CreatingVNet",
  components: {
    MenuDevices
  },
  prop: {},
  setup(props, ctx){
    // cytoscape obj
    //@note move parent component????
    let cy: Core = null
    // temporary list to create edge
    let edge: string[] = []
    // dragged element (if no element is dragged, this is null)
    let dragged: HTMLImageElement = null

    onMounted(()=>{
      cy = cytoscape({
        container: document.getElementById('vnet_canvas'),
        style: [
          {
            selector: '*',
            style: {
              'label': 'data(id)'
            }
          }
        ]
      })
      // 'tap' event handler on node
      //@note set timeout
      cy.on('tap', 'node', function(event: EventObject){
        let target = event.target
        edge.push(target.id())
        if(edge.length >= 2){
          if( edge[0] !== edge[1]){
            cy.add(Object.assign(createEdge(edge[0], edge[1])))
          }
          edge = []
        }
      })
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
      const offsetX = event.offsetX
      const offsetY = event.offsetY 
      
      // where to make the switch
      if(dragged){
        const v = cy.add(Object.assign(createDevice(dragged, offsetX, offsetY)))
        dragged = null
        console.log(v[0])
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