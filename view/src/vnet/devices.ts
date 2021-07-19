export const DEVICE_TYPE = {
  OFSWITCH: 'ofswitch',
  HOST: 'host'
} as const;
export type DEVICE_TYPE = typeof DEVICE_TYPE[keyof typeof DEVICE_TYPE]


export interface cytoscapeData{
  /** id (required) */
  id: string
}

export interface cytoscapeStyle{
  /** id (required) */
  selector: string
  style: {
    'label': ''
  }
}

/**
 * device position on vnet_canvas
 */
class Pos{
  x: number
  y: number

  constructor(x: number, y: number){
    this.x = x
    this.y = y
  }

  public getPos(){
    return {
      'x': this.x,
      'y': this.y
    }
  }
}

/**
 * Device class.
 * * provide an interface to interact with cytoscape
 * * act as a model to hold information about the device
 * 
 * @note
 * maybe delete this
 */
export abstract class Device{
  /** cytoscape data */
  private data: cytoscapeData
  /** position */
  private pos: Pos
  /** cytoscape style */
  private style: cytoscapeStyle

  constructor(data: cytoscapeData, pos: Pos, style: cytoscapeStyle){
    this.data = data
    this.pos = pos
    this.style = style
  }

  public getData(){
    return this.data
  }

  public getPos(){
    return this.pos.getPos()
  }

  public getStyle(){
    return this.style
  }
}