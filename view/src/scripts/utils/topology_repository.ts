import { CommandResult, CommandResultType, GetTraceRequest, GetTraceResult, Host, Link, MininetCommand, StartTracingRequest, StopTracingRequest, Switch } from '../remote/net_pb';

type Node = Host | Switch

type TopologyElement = Link | Node


/**
 * Topology repositoty
 */
class TopologyRepository{

  private nodes: Node[]
  private links: Link[]

  constructor(){
    this.nodes = []
    this.links = []
  }

  addNode(node: Node){
    if(!this.isNode(node.getName())){
      this.nodes.push(node)
    }
  }

  addLink(link: Link){
    if(!this.isLink(link.getName())){
      this.links.push(link)
    }
  }

  isNode(nodeName: string): boolean{
    let isNode = false
    this.nodes.forEach(n => {
      if(n.getName() == nodeName){
        isNode = true
      }
    })
    return isNode
  }

  isLink(linkName: string): boolean {
    let isLink = false
    this.links.forEach(l => {
      if(l.getName() == linkName){
        isLink = true
      }
    })
    return isLink
  }

  getNode(nodeName: string): Node {
    let node: Node = null
    this.nodes.forEach(n => {
      if(n.getName() === nodeName){
        node = n
      }
    })
    return node
  }

  getLink(linkName: string): Link{
    let link: Link = null
    this.links.forEach(l => {
      if(l.getName() === linkName){
        link = l
      }
    })
    return link
  }

  getNodes(){
    return this.nodes
  }

  getLinks(){
    return this.links
  }

}

export const topologyRepository = new TopologyRepository()
