import { proto } from '../api/net'


/**
 * 受け取ったパケットの経路を保存しておくためのクラス
 */
class PacketTracesRepository{

  private packetTraces: proto.PacketTrace[]

  constructor(){
    this.packetTraces = []
  }

  get(id: number){
    return this.packetTraces[id]
  }

  getPacketTraces(){
    return this.packetTraces
  }

  add(packetTrace: proto.PacketTrace){
    const len = this.packetTraces.push(packetTrace)
    return len - 1
  }

  extend(packetTraces: proto.PacketTrace[]){
    packetTraces.forEach(pt => {
      this.add(pt)
    })
  }

  reset(){
    this.packetTraces = []
  }
}


export const packetTracesRepository = new PacketTracesRepository()
