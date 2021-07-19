import { DEVICE_TYPE } from "./devices"
import { ElementDefinition } from 'cytoscape'
import { VNet } from "./vnet"

const count: number[] = [0, 0, 0]
/**
 * Create a cytoscape node. Give it a continuous identifier.
 * 
 * @param element - img element used for creating device
 * @param x - node position
 * @param y - node position
 * @returns obj - device obj
 */
export const createDevice = (element: HTMLImageElement, x: number, y: number, vnet?: VNet) => {
  let id: string
  if(element.classList[0] === DEVICE_TYPE.OFSWITCH){
    id = 's' + count[0]++
  }else if(element.classList[0] === DEVICE_TYPE.HOST){
    id = 'h' + count[1]++
  }
  vnet = vnet ?? null
  // fix position
  if(vnet){
    const position = vnet.getCytoscape().pan()
    const zoom = vnet.getCytoscape().zoom()
    x = (x - position.x)/zoom
    y = (y - position.y)/zoom
  }
  const device: ElementDefinition = {
    group: 'nodes',
    data: {
      id: id
    },
    position: {
      x: x,
      y: y
    },
    style: {
      'shape': "rectangle",
      'height': element.offsetHeight,
      'width': element.offsetWidth,
      'background-image': element.src
    }
  }
  return device
}

/**
 * Create a cytoscape edge. Give it a continuous identifier.
 * @param source 
 * @param target 
 * @returns 
 */
export const createEdge = (source: string, target: string) => {
  const edge: ElementDefinition = {
    group: 'edges',
    data: {
      id: 'e' + count[2]++,
      source: source,
      target: target
    }
  }
  return edge
}