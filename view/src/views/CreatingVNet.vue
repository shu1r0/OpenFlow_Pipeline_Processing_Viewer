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
import cytoscape from 'cytoscape'

export default defineComponent({
  name: "CreatingVNet",
  components: {
    MenuDevices
  },
  prop: {},
  setup(props, ctx){
    // cytoscape obj
    let cy: any = null
    // temporary list to create edge
    let edge: number[] = []
    // dragged element (if no element is dragged, this is null)
    let dragged: HTMLImageElement = null

    onMounted(()=>{
      cy = cytoscape({
        container: document.getElementById('vnet_canvas'),
        style: [
          {
            selector: 'node',
            style: {
              'shape': "rectangle",
              'label': 'data(id)',
              'height': 50,
              'width': 100,
              'background-image': 'url(img/workgroup_switch.jpg)'
            }
          }
        ]
      })
      console.log(cy)
      // 'tap' event handler on node
      cy.on('tap', 'node', function(event: any){
        let target = event.target
        edge.push(target.id())
        if(edge.length >= 2){
          if( edge[0] !== edge[1]){
            cy.add({
              group: 'edges',
              data: {
                id: 'e' + Math.floor(Math.random()*100),
                source: edge[0],
                target: edge[1]
              }
            })
          }
          edge = []
        }
      })
    })
    
    const setDragged = (d: HTMLImageElement) => {
      dragged = d
    }

    const dragoverHandler = (event: DragEvent) => {
      event.preventDefault()
      const dragged: HTMLImageElement = event.target as HTMLImageElement
      // console.log(dragged)
    }

    /**
     * drop event handler
     * Create the device when an element is dropped on the canvas
     * @property {DragEvent} event
     */
    const dropHandler = (event: DragEvent) => {
      event.preventDefault()
      const dropTarget: HTMLImageElement = event.target as HTMLImageElement
      const offsetX = event.offsetX
      const offsetY = event.offsetY 
      
      // where to make the switch
      if(dragged){
        // const draggedCopy = dragged.cloneNode(true) as HTMLImageElement
        // draggedCopy.style.top = offsetY + "px"
        // draggedCopy.style.left = offsetX + "px"
        // dropTarget.appendChild(draggedCopy)
        cy.add({
          group: 'nodes',
          data: {
            id: 's' + Math.floor(Math.random()*100),
            image: 'img/workgroup_switch.jpg'
          },
          position: {
            x: offsetX,
            y: offsetY
          },
          style: {
            'shape': "rectangle",
            'height': dragged.offsetHeight,
            'width': dragged.offsetWidth,
            'background-image': dragged.src
          }
        })
        dragged = null
        console.log(cy.nodes())
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