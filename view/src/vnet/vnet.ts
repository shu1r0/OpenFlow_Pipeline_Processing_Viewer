import cytoscape, { EventObject, Core, CollectionReturnValue, CytoscapeOptions, NodeSingular, EdgeSingular } from 'cytoscape'
import { createDevice, createEdge } from '../vnet/factory'
// @ts-ignore
import gtip from 'cytoscape-qtip'

console.log(gtip)
gtip(cytoscape)

export class VNet{
  private cytoscape: Core;
  private tappedEdges: string[] = []
  private options: CytoscapeOptions = {}
  private deviceStyle: StyleSheet = null
  private edgeStyle: StyleSheet = null

  constructor(element: HTMLElement){
    this.options.container = element
    this.options.style = [{
      selector: '*',
      style: {
        'label': 'data(id)'
      }
    }]
    this.cytoscape = cytoscape(this.options)
    // @ts-ignore
    console.log(this.cytoscape.gtip)
    this.setupEvents()
  }

  /**
   * template method for to setup event listener
   */
  setupEvents() {
    this.setupAddEdgeEvent()
  }

  /**
   * add edge event listener
   * 
   * Note:
   *  * タイムアウト処理を行う
   *  * ほかをタップすれば消えるように死体
   */
  setupAddEdgeEvent(){
    this.cytoscape.on('tap', 'node', (event: EventObject) => {
      const target = event.target
      this.tappedEdges.push(target.id())

      if(this.tappedEdges.length >= 2){
        if(this.tappedEdges[0] !== this.tappedEdges[1]){
          this.addEdge(this.tappedEdges[0], this.tappedEdges[1])
        }
        this.tappedEdges = []
      }
    })

    this.cytoscape.on('mouseover', 'node', (event: EventObject) => {
      const target = event.target
      console.log(target.gtip)
      target.gtip({
        content: 'hello',
        show: {
          event: event.type,
          ready: true
        },
        hide: {
          event: 'mouseout unfocus'
        }
      }, event)
    })
  }

  /**
   * Container
   */
  getContainer(){
    return this.cytoscape.container()
  }

  getCytoscape(){
    return this.cytoscape
  }

  /**
   * add device
   * @param element : added node's element
   * @param x : x座標
   * @param y : y座標
   * @returns CollectionReturnValue
   */
  addDevice(element: HTMLImageElement, x: number, y: number){
    const addedNode = createDevice(element, x, y, this)
    const collection: CollectionReturnValue = this.cytoscape.add(Object.assign(addedNode))
    // if(this.deviceStyle){
    //   collection.style(this.deviceStyle)
    // }
    return collection
  }

  /**
   * add edge
   * @param node1 : node
   * @param node2 : node
   * @returns CollectionReturnValue
   */
  addEdge(node1: string, node2: string){
    const edge_obj = createEdge(node1, node2)
    const collection: CollectionReturnValue = this.cytoscape.add(Object.assign(edge_obj))
    // if(this.edgeStyle){
    //   collection.style(this.edgeStyle)
    // }
    return collection['!']
  }

  /**
   * 
   * @returns nodes
   */
  getNodes(){
    const nodes: string[] = []
    this.cytoscape.nodes().forEach((node: NodeSingular) => {
      nodes.push(node.id())
    })
    return nodes
  }

  /**
   * 
   * @returns links
   */
  getLinks(): {link: string; edges: string[]} {
    const nodes: any = {}
    this.cytoscape.edges().forEach((edge: EdgeSingular) => {
      const edges: string[] = []
      edges.push(edge.source().id())
      edges.push(edge.target().id())
      nodes[edge.id()] = edges
    })
    return nodes
  }
}


const createVNet = (element: HTMLElement) => {
  return new VNet(element)
}