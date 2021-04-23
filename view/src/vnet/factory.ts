import { DEVICE_TYPE } from "./devices"

const count: number[] = [0, 0, 0]
/**
 * Create a cytoscape node. Give it a continuous identifier.
 * 
 * @param element - img element used for creating device
 * @param x - node position
 * @param y - node position
 * @returns obj - device obj
 */
export const createDevice = (element: HTMLImageElement, x: number, y: number) => {
  let id: string
  if(element.classList[0] === DEVICE_TYPE.OFSWITCH){
    id = 's' + count[0]++
  }else if(element.classList[0] === DEVICE_TYPE.HOST){
    id = 'h' + count[1]++
  }
  const device = {
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
  const edge = {
    group: 'edges',
    data: {
      id: 'e' + count[2]++,
      source: source,
      target: target
    }
  }
  return edge
}