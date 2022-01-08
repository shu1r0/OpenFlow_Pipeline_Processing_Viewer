import { PacketTrace } from "../remote/net_pb"


/**
 * 受け取ったパケットの経路を保存しておくためのクラス
 */
class PacketTracesRepository{

  /**
   * packet trace list
   */
  private packetTraces: PacketTrace[]

  constructor(){
    this.packetTraces = []
  }

  /**
   * get packet trace
   * @param id (number) - trace index
   * @returns PacketTrace
   */
  get(id: number): PacketTrace{
    return this.packetTraces[id]
  }

  /**
   * get packet traces
   *  * This method params is filter.
   * 
   * @param src - trace src
   * @param nodes - node in trace
   * @param dst - trace dst
   * @returns PacketTrace[]
   */
  getPacketTraces(src?: string, nodes?: string[], dst?: string): PacketTrace[]{
    const packetTraces: PacketTrace[] = []
    this.packetTraces.forEach(t => {
      // filter param is defined.
      if(src || nodes || dst){
        console.log("get packet trace with filter")
        let pushedTrace = null

        // src
        if(src){
          if(src === t.getArcsList()[0].getSrc()){
            pushedTrace = t
          }
        }
      
        // dst
        if(dst){
          if(dst === t.getArcsList()[0].getDst()){
            pushedTrace = t
          }else{
            pushedTrace = null
          }
        }

        // nodes
        if(nodes){
          let hasEqNs = true
          nodes.forEach(n => {
            let hasEqN = false
            t.getArcsList().forEach(a => {
              if(a.getSrc() === n || a.getDst() === n){
                hasEqN = true
              }
            })
            if(!hasEqN){
              hasEqNs = false
            }
          })
          if(hasEqNs){
            pushedTrace = t
          }else{
            pushedTrace = null
          }
        }

        if(pushedTrace){
          packetTraces.push(pushedTrace)
        }
      }else{
        packetTraces.push(t)
      }
    })
    return packetTraces
  }

  /**
   * add and sort
   * @param packetTrace - added packet trace
   * @returns {number} - added index
   */
  add(packetTrace: PacketTrace): number{
    let index: number
    let add = false
    for(let i = 0; i > this.packetTraces.length; i++){
      if(packetTrace.getTimestamp() >= this.packetTraces[i].getTimestamp()){
        this.packetTraces.splice(i, 0, packetTrace)
        add = true
        index = i
      }
    }
    if(!add){
      index = this.packetTraces.push(packetTrace)
      index = index - 1
    }
    return index
  }

  /**
   * add packet trace list
   * @param packetTraces - added packetTraces
   */
  extend(packetTraces: PacketTrace[]){
    packetTraces.forEach(pt => {
      this.add(pt)
    })
  }

  /**
   * reset this repository
   */
  reset(){
    this.packetTraces = []
  }
}


export const packetTracesRepository = new PacketTracesRepository()
