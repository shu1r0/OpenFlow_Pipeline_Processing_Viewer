import { proto } from '../api/net'

/**
 * get packet processing
 * 
 * @todo:
 *    * 同じスイッチで複数のarcがある場合に分けることができない
 * @param trace : packet trace
 * @param switchId : switch name
 * @returns proto.PacketProcessing[] : 現状はただの配列
 */
export const getPacketProcessing = (trace: proto.PacketTrace, switchId: string): proto.PacketProcessing[] => {
  const processes: proto.PacketProcessing[] = []
  trace.arcs.forEach(arc => {
    if(arc.packet_processing.switch === switchId){
      processes.push(arc.packet_processing)
    }
  })
  return processes
}


/**
 * ただ，リストで表示するための文字列を出力
 * * utilに移行するのもあり
 */
export const traceToString = (trace: proto.PacketTrace) => {
  let traceStr = ""
  trace.arcs.forEach(arc => {
    if(traceStr === ""){
      traceStr = arc.src + ' -> ' + arc.dst
    }else{
      traceStr = traceStr + ' -> ' + arc.dst
    }
  })
  return traceStr
}