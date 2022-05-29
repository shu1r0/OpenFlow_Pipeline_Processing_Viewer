import { Css, EdgeDataDefinition, ElementDefinition, ElementGroup, NodeDataDefinition, Position } from 'cytoscape'


/**
 * device type
 */
export const DEVICE_TYPE = {
  OFSWITCH: 'ofswitch',
  HOST: 'host'
} as const;
export type DEVICE_TYPE = typeof DEVICE_TYPE[keyof typeof DEVICE_TYPE]


/**
 * Device class.
 * * provide an interface to interact with cytoscape
 * * act as a model to hold information about the device
 * 
 * @note
 * maybe delete this
 */
export class CytoscapeElement implements ElementDefinition{
  group?: ElementGroup;
  data: NodeDataDefinition | EdgeDataDefinition;
  scratch?: any;
  position?: Position;
  renderedPosition?: Position;
  selected?: boolean;
  selectable?: boolean;
  locked?: boolean;
  grabbable?: boolean;
  classes?: string;
  style?: any;
  css?: Css.Node | Css.Edge;

  getId(){
    return this.data.id
  }

  getName(){
    return this.data.name
  }
}

export class Host extends CytoscapeElement {
  private ip?: string
  private mac?: string

  constructor(){
    super();
  }

  getIp(){
    return this.ip
  }

  getMac(){
    return this.mac
  }
}

export class Switch extends CytoscapeElement {
  private dpid?: string

  constructor(){
    super();
  }

  getDpid(){
    return this.dpid
  }
}

export class Edge extends CytoscapeElement {

  constructor(){
    super();
  }

  getNode1(){
    return this.data.source
  }

  getNode2(){
    return this.data.target
  }
}

export type Device = Host | Switch
