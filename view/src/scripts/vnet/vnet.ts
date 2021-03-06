/**
 * 仮想的なネットワークに関するモジュール
 * 
 * Cytoscapeのラッパークラスを用意する．
 * 
 * ## Style
 * 仮想ネットワークでは，スイッチなどのデバイス画像以外は，クラスによりスタイルを決定する．
 * スタイルについては，`https://github.com/cytoscape/cytoscape.js/blob/b9b0797c85e8bf8e8c071b0acd08d0b4e790de19/documentation/md/style.md`_ を参照．
 * 
 * ## Multi Virtual Network
 */

import cytoscape, { EventObject, Core, CollectionReturnValue, CytoscapeOptions, NodeSingular, EdgeSingular, ElementDefinition, CollectionArgument } from 'cytoscape'
import { Host, Switch, Edge } from './devices'
import { createDevice, createEdge, createPacketEdge, createController } from './factory'
import { RemoteClient } from '../remote/remoteClient'
// @ts-ignore
import gtip from 'cytoscape-qtip'

console.log(gtip)
gtip(cytoscape)


/**
 * a interface for mounting to HTML Element
 */
interface Mountable{
  
  /**
   * Mount element
   * @param element {HTMLElement} : Mounted element
   */
  setupCytoscape(element: HTMLElement): void

  /**
   * set up from vnet
   * @param vnet {VirtualNetworkBase} : network
   * @param element {HTMLElement} : element
   */
  setupFrom(vnet: VNet, element: HTMLImageElement): void
}


/**
 * VNet BaseClass
 */
abstract class VirtualNetworkBase{

  /**
   * cytoscape obj
   */
  cytoscape: Core;

  /**
   * Element Definitions of ofswitch
   */
  switches: {[key: string]: Switch} = {}

  /**
   * Element Definitions of host
   */
  hosts: {[key: string]: Host} = {}

  /**
   * Element Definitions of edge
   */
  edges: {[key: string]: Edge} = {}

  /**
   * add device from HTMLImageElement
   * 
   * @param element : added HTMLElement
   * @param x : x position
   * @param y : y position
   * @param style : Device Style
   */
  abstract addDevice(element: HTMLImageElement, x: number, y: number, style?: StyleSheet): CollectionReturnValue

  /**
   * add edge
   * 
   * @param node1 : node1
   * @param node2 : node2
   * @param style : edge style
   */
  abstract addEdge(node1: string, node2: string, style?: StyleSheet): CollectionReturnValue

  /**
   * remove element
   * 
   * @param id : removed element id
   */
  abstract remove(id: string): CollectionReturnValue

  /**
   * Container
   * 
   * @returns HTMLElement
   */
  getContainer(){
    return this.cytoscape.container()
  }

  /**
   * get Cytoscape
   * @returns Core
   */
  getCytoscape(){
    return this.cytoscape
  }

  /**
   * get element by id
   * @param id element id
   * @returns CollectionReturnValue
   */
  get(id: string){
    return this.cytoscape.$id(id)
  }
}


/**
 * Vertual Network Base
 */
export class VNet extends VirtualNetworkBase{

  /**
   * Cytoscape Options
   */
  options: CytoscapeOptions = {}

  /**
   * tappedEdges
   */
  private tappedEdges: string[] = []

  /**
   * remote client
   */
  private remoteClient: RemoteClient = null

  constructor(remoteClient?: RemoteClient){
    super()
    this.remoteClient = remoteClient
  }

  /**
   * getter for client
   * @returns RemoteClient
   */
  getRemoteClient(){
    return this.remoteClient
  }

  /**
   * setter for client
   * @param remoteClient remote client
   */
  setRemoteClient(remoteClient: RemoteClient){
    this.remoteClient = remoteClient
  }

  /**
   * setup from property
   * 
   * Note:
   *     * 追加するデバイスがない場合，返り値の値は信用できない
   */
  setUpDefaultElements(){
    const shape = {
      top: 99999,
      bottom: -99999,
      left: 99999,
      right: -99999
    }
    const updateShape = (e: ElementDefinition) => {
      const x = e.position.x
      const y = e.position.y
      if(y < shape.top){
        shape.top = y
      }
      if(y > shape.bottom){
        shape.bottom = y
      }
      if(x < shape.left){
        shape.left = x
      }
      if(x > shape.right){
        shape.right = x
      }
    }
    if(this.cytoscape){
      for(const [_, value] of Object.entries(this.switches)){
        updateShape(value)
        this.cytoscape.add(Object.assign(value))
      }
      for(const [_, value] of Object.entries(this.hosts)){
        updateShape(value)
        this.cytoscape.add(Object.assign(value))
      }
      for(const [_, value] of Object.entries(this.edges)){
        this.cytoscape.add(Object.assign(value))
      }
    }else{
      console.error("no cytoscape instance")
    }
    if(shape.top === 99999){
      shape.top = 0
      shape.bottom = 0
      shape.left = 0
      shape.right = 0
    }
    return shape
  }

  /**
   * add edge event listener
   * 
   * Note:
   *  * タイムアウト処理を行う
   *  * ほかをタップすれば消えるように死体
   */
  setupNodeEvents(){
    this.cytoscape.on('tap', 'node', (event: EventObject) => {
      const target = event.target
      this.tappedEdges.push(target.id())

      if(this.tappedEdges.length >= 2){
        if(this.tappedEdges[0] !== this.tappedEdges[1]){
          this.addEdge(this.tappedEdges[0], this.tappedEdges[1], undefined, true)
        }
        this.tappedEdges = []
      }
    })

    /**
     * テスト
     */
    this.cytoscape.on('mouseover', 'node', (event: EventObject) => {
      const target = event.target
      console.log(target)

    //   target.gtip({
    //     content: 'hello',
    //     show: {
    //       event: event.type,
    //       ready: true
    //     },
    //     hide: {
    //       event: 'mouseout unfocus'
    //     }
    //   }, event)
    })
  }

  /**
   * add device
   * @param element : added node's element
   * @param x : x座標
   * @param y : y座標
   * @returns CollectionReturnValue
   */
  addDevice(element: HTMLImageElement, x: number, y: number, style?: StyleSheet, remote=false){
    const addedNode = createDevice(element, x, y, this)
    if(addedNode instanceof Switch){
      this.switches[addedNode.data.id] = addedNode
    }else if(addedNode instanceof Host){
      this.hosts[addedNode.data.id] = addedNode
    }
    if(style){
      addedNode.style = style
    }
    const collection: CollectionReturnValue = this.cytoscape.add(Object.assign(addedNode))

    if(this.remoteClient && remote){
      this.remoteClient.addDevice(addedNode)
    }else{
      console.warn("There is no remote client.")
    }

    return collection
  }

  /**
   * add edge
   * @param node1 : node
   * @param node2 : node
   * @returns CollectionReturnValue
   */
  addEdge(node1: string, node2: string, style?: StyleSheet, remote=false){
    const addedEdge = createEdge(node1, node2)
    this.edges[addedEdge.data.id] = addedEdge
    if(style){
      addedEdge.style = style
    }
    const collection: CollectionReturnValue = this.cytoscape.add(Object.assign(addedEdge))

    if(this.remoteClient && remote){
      this.remoteClient.addLink(addedEdge)
    }else{
      console.warn("There is no remote client.")
    }

    return collection
  }

  /**
   * remove element
   * @param id element id
   * @returns CollectionReturnValue
   */
  remove(id: string, remote=false){
    const e: CollectionArgument = this.get(id)
    const removedElement: CollectionReturnValue = this.cytoscape.remove(e)
    if(id in this.switches){
      delete this.switches[id]
      if(this.remoteClient && remote){
        this.remoteClient.removeSwitch(id)
      }else{
        console.warn("There is no remote client.")
      }
    }else if(id in this.hosts){
      delete this.hosts[id]
      if(this.remoteClient && remote){
        this.remoteClient.removeHost(id)
      }else{
        console.warn("There is no remote client.")
      }
    }else if(id in this.edges){
      delete this.edges[id]
      if(this.remoteClient && remote){
        this.remoteClient.removeLink(id)
      }else{
        console.warn("There is no remote client.")
      }
    }

    return removedElement
  }
}


/**
 * VNet for CreatingVNet View
 */
class ChangeableVNet extends VNet implements Mountable{

  constructor(remoteClient?: RemoteClient){
    super(remoteClient)
  }

  setupCytoscape(element: HTMLElement): void {
    this.options.container = element
    this.options.style = [{
      selector: '*',
      style: {
        'label': 'data(name)'
      }
    }]
    this.cytoscape = cytoscape(this.options)

    this.setupNodeEvents()
  }
  
  /**
   * 
   * @param vnet copyed vnet
   */
  setupFrom(vnet: VNet, element: HTMLImageElement){
    throw new Error('Method not implemented.')
  }
}


/**
 * パケットの経路を表示するためのクラス
 * 
 * このクラスにはパケットの経路の保存とそれらの表示があります．
 */
export class TracingVNet extends VNet implements Mountable{

  /**
   * パケット経路用の辺
   */
  private packetEdges: {[key: string]: ElementDefinition} = {}

  /**
   * 引数 ``element`` と ``vnet`` が指定されている場合は，その値に基づき初期化を行う．
   */
  constructor(remoteClient?: RemoteClient, element?: HTMLElement, vnet?: VNet){
    super(remoteClient)

    if(element && vnet){
      console.log("TracingVNet setup from vnet and element")
      this.setupFrom(vnet, element)
    }
  }

  /**
   * setupCytoscape
   * 
   * @param element : mounted element
   */
  setupCytoscape(element: HTMLElement): void {
    this.options.container = element
    this.options.style = [{
      selector: 'nodes',
      style: {
        'label': 'data(name)'
      }
    },{
      selector: '.link',
      style: {
        'background-opacity': 0.5,
      }
    },{
      selector: '.packet-edge',
      style: {
        'target-arrow-color': '#ee2222',
        'target-arrow-shape': 'triangle',
        'line-color': '#ee2222',
        'curve-style': 'bezier',
        'width' : 5
        // 'control-point-distance': 10,
        // 'z-index': 2,
      }
    }]
    this.cytoscape = cytoscape(this.options)
  }
  
  /**
   * vnetの情報からsetupする
   * @param vnet {VNet} - 仮想ネットワークインスタンス
   * @param element {HTMLElement} - マウントする要素
   */
  setupFrom(vnet: VNet, element: HTMLElement){
    this.setupCytoscape(element)
    this.setProperties(vnet.switches, vnet.hosts, vnet.edges)
    const shape = this.setUpDefaultElements()
    this.addController((shape.right - shape.left)/2 + shape.left, shape.top - 50)
  }

  private setProperties(switches: {[key: string]: Switch}, hosts: {[key: string]: Host}, edges: {[key: string]: Edge}){
    this.switches = switches
    this.hosts = hosts
    this.edges = edges
  }

  /**
   * tap event
   * @param callback : event callback
   */
  onTapEventsInSwitch(callback: (nodeId: string) => void){
    this.cytoscape.on('tap', '.switch', (event: EventObject) => {
      callback(event.target.id())
    })
  }

  private addController(x: number, y: number){
    const controller = createController(x, y)
    const collection = this.cytoscape.add(Object.assign(controller))
    for(const [_, value] of Object.entries(this.switches)){
      const edge = createEdge(controller.data.id, value.data.id)
      this.cytoscape.add(Object.assign(edge))
    }
    return collection
  }

  /**
   * add packet edge
   * @param node1 node1
   * @param node2 node2
   * @param style edge style (option)
   * @returns CollectionReturnValue
   */
  addPacketEdge(node1: string, node2: string, style?: StyleSheet){
    const addedEdge = createPacketEdge(node1, node2)
    this.packetEdges[addedEdge.data.id] = addedEdge
    if(style){
      addedEdge.style = style
    }
    const collection: CollectionReturnValue = this.cytoscape.add(Object.assign(addedEdge))
    return collection
  }

  /**
   * remove element (Override Method)
   * @param id : removed element id
   * @returns CollectionReturnValue
   */
  remove(id: string): CollectionReturnValue {
    let removedElement: CollectionReturnValue = null
    if(id in this.packetEdges){
      delete this.packetEdges[id]
      const e: CollectionArgument = this.get(id)
      removedElement = this.cytoscape.remove(e)
    }else{
      removedElement = super.remove(id)
    }

    return removedElement
  }

  removeAllPacketEdges(){
    for(const [_, value] of Object.entries(this.packetEdges)){
      this.remove(value.data.id)
    }
  }
}

/**
 * changeable vnet instance
 */
export const changeableVNet: ChangeableVNet = new ChangeableVNet()
