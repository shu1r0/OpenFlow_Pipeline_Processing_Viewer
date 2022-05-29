import { DEVICE_TYPE, Host, Device, Switch, Edge } from "./devices"
import { ElementDefinition } from 'cytoscape'
import { VNet } from "./vnet"

const count: number[] = [0, 0, 0]

/**
 * Create a cytoscape node. Give it a continuous identifier.
 * 
 * @param element - img element used for creating device
 * @param x - node position
 * @param y - node position
 * @returns Device
 */
export const createDevice = (element: HTMLImageElement, x: number, y: number, vnet?: VNet): Device => {
  let deviceClass: string = ""
  let id: string = ""

  let device: Device
  const deviceDef: ElementDefinition = {
    group: 'nodes',
    data: {
      id: id,
      name: id
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
  
  vnet = vnet ?? null
  // fix position
  if(vnet){
    const position = vnet.getCytoscape().pan()
    const zoom = vnet.getCytoscape().zoom()
    x = (x - position.x)/zoom
    y = (y - position.y)/zoom
    deviceDef.position.x = x
    deviceDef.position.y = y
  }

  if(element.classList[0] === DEVICE_TYPE.OFSWITCH){
    id = 's' + count[0]++
    deviceClass = "switch"
    device = Object.assign(new Switch(), deviceDef)
  }else if(element.classList[0] === DEVICE_TYPE.HOST){
    id = 'h' + count[1]++
    deviceClass = "host"
    device = Object.assign(new Host(), deviceDef)
  }
  device.data.id = id
  device.data.name = id
  device.classes = deviceClass


  return device
}


export const createController = (x?: number, y?: number) => {
  const controller: ElementDefinition = {
    group: 'nodes',
    data: {
      id: "controller",
      name: "controller"
    },
    position: {
      x: x ?? 0,
      y: y ?? 0
    },
    classes: "controller",
    style: {
      'shape': 'rectangle',
      'height': 58,
      'width': 44,
      'background-image': 'img/file_server.jpg'
    }
  }
  return controller
}


/**
 * Create a cytoscape edge. Give it a continuous identifier.
 * @param source 
 * @param target 
 * @returns Edge
 */
export const createEdge = (source: string, target: string): Edge => {
  const id = 'e' + count[2]++
  const edgeDef: ElementDefinition = {
    group: 'edges',
    data: {
      id: id,
      name: id,
      source: source,
      target: target
    },
    classes: "link"
  }
  const edge: Edge = Object.assign(new Edge(), edgeDef)
  return edge
}


let pCounter = 0
/**
 * Create a packet edge. 
 * @param source 
 * @param target 
 * @returns Edge
 */
export const createPacketEdge = (source: string, target: string, id?: string): Edge => {
  id = id ?? 'eXX'
  id = id + '-' + pCounter++
  const edgeDef: ElementDefinition = {
    group: 'edges',
    data: {
      id: id,
      name: id,
      source: source,
      target: target
    },
    classes: "link packet-edge"
  }
  const edge: Edge = Object.assign(new Edge(), edgeDef)
  return edge
}