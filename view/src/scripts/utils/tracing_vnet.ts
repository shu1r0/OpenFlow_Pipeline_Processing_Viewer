// import { proto } from '../../api/net'

import { PacketTrace, PacketProcessing } from "../remote/net_pb"


/**
 * get packet processing
 * 
 * @todo:
 *    * 同じスイッチで複数のarcがある場合に分けることができない
 * @param trace : packet trace
 * @param switchId : switch name
 * @returns PacketProcessing[] : 現状はただの配列
 */
export const getPacketProcessing = (trace: PacketTrace, switchId: string): PacketProcessing[] => {
  console.log("search packet processing (trace, switch)")
  console.log(trace)
  console.log(switchId)
  const processes: PacketProcessing[] = []
  trace.getArcsList().forEach(arc => {
    if(arc.getPacketProcessing() && arc.getPacketProcessing().getSwitch() === switchId){
      processes.push(arc.getPacketProcessing())
    }
  })
  return processes
}


/**
 * ただ，リストで表示するための文字列を出力
 * * utilに移行するのもあり
 */
export const traceToString = (trace: PacketTrace) => {
  let traceStr = ""
  trace.getArcsList().forEach(arc => {
    if(traceStr === ""){
      traceStr = arc.getSrc() + ' -> ' + arc.getDst()
    }else{
      traceStr = traceStr + ' -> ' + arc.getDst()
    }
  })
  return traceStr
}