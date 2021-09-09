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
 * @returns ElementDefinition - device obj
 */
export const createDevice = (element: HTMLImageElement, x: number, y: number, vnet?: VNet): ElementDefinition => {
  let deviceClass: string
  let id: string
  if(element.classList[0] === DEVICE_TYPE.OFSWITCH){
    id = 's' + count[0]++
    deviceClass = "switch"
  }else if(element.classList[0] === DEVICE_TYPE.HOST){
    id = 'h' + count[1]++
    deviceClass = "host"
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
    classes: deviceClass,
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
 * @returns ElementDefinition
 */
export const createEdge = (source: string, target: string): ElementDefinition => {
  const edge: ElementDefinition = {
    group: 'edges',
    data: {
      id: 'e' + count[2]++,
      source: source,
      target: target
    },
    classes: "link"
  }
  return edge
}


let pCounter = 0
/**
 * Create a packet edge. 
 * @param source 
 * @param target 
 * @returns ElementDefinition
 */
export const createPacketEdge = (source: string, target: string, id?: string): ElementDefinition => {
  id = id ?? 'eXX'
  id = id + '-' + pCounter++
  const edge: ElementDefinition = {
    group: 'edges',
    data: {
      id: id,
      source: source,
      target: target
    },
    classes: "link packet-edge"
  }
  return edge
}