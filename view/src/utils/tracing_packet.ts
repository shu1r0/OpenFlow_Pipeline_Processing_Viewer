import {proto} from '../api/net'


export interface PacketProcessingData {
  packetProcessing: proto.PacketProcessing
}

/**
 * パケット更新の様子
 */
export interface UpdatePacket {
  packetBefore: Map<string, string>,
  packetAfter: Map<string, string>,
  applyedFlow: proto.Flow,
  applyedActions: string[]
}

/**
 * フローidのフローを取り出す
 * @param flowTable : フローテーブル
 * @param flowId : フローのid
 * @returns proto.Flow | null
 */
export const getFlow = (flowTable: proto.FlowTable, flowId: number): proto.Flow | null => {
  flowTable.flows.forEach(f => {
    if(f.flow_id === flowId){
      return f
    }
  })
  return null
}

/**
 * マッチしたフローの配列から，マッチしたフローテーブルの配列に変換
 * @param matchedFlows : マッチしたフロー
 * @param flowTable : フローテーブル
 * @returns number[] : マッチしたフローテーブルの列
 */
export const matchedFlows2matchedTables = (matchedFlows: number[], flowTable: proto.FlowTable): number[] => {
  const tables: number[] = []
  matchedFlows.forEach(f => {
    tables.push(getFlow(flowTable, f).table)
  })
  return tables
}

/**
 * proto.Actionを文字列の配列に変換
 * @param actions : 適用されたアクション
 * @returns string[] : アクションの文字列の配列
 */
export const protoActions2Strings = (actions: proto.Action[]): string[] =>{
  const str: string[] = []
  actions.forEach(a =>{
    str.push(a.str)
  })
  return str
}

/**
 * パケット更新を表示
 * 
 * @param pkts : パケットのArray
 * @param matchedFlows : マッチしたフローのidのArray
 * @param currentIndex : 今参照しているテーブルが何番目(not flow id)か
 * @param flowTable : すべてのフローテーブル
 * @returns UpdatePacket
 */
export const getPacketBeforeAfter = (pkts: proto.Packet[], matchedFlows: number[], currentIndex: number, flowTable: proto.FlowTable): UpdatePacket => {
  const updataPacket = {} as UpdatePacket
  updataPacket.packetBefore = pkts[currentIndex].fields
  if(pkts.length > currentIndex){
    updataPacket.packetAfter = pkts[++currentIndex].fields
    const flow: proto.Flow = getFlow(flowTable, matchedFlows[currentIndex])
    updataPacket.applyedFlow = flow
    const insts: proto.Instruction[] = flow.actions
    insts.forEach(inst => {
      if(inst.type === proto.InstructionType.OFPIT_APPLY_ACTIONS){
        updataPacket.applyedActions = protoActions2Strings(inst.actions.actions)
      }
    })
  }else{
    updataPacket.packetAfter = updataPacket.packetBefore
    updataPacket.applyedActions = ["NoMatch"]
  }
  return updataPacket
}

/**
 * 表示する際のフローのインターフェース
 */
export interface Flow {
  /**
   * flow priority
   */
  priority : number,
  match : string,
  instruction: string,
  class: string
}

/**
 * 表で表示するためにインストラクションを文字列に変換する
 * @param instruction : インストラクション
 * @returns string
 */
const protoInstruction2String = (instruction: proto.Instruction): string => {
  let stringInst: string = ""
  switch (instruction.type) {
    case proto.InstructionType.OFPIT_APPLY_ACTIONS:
      stringInst = "Apply(" + protoActions2Strings(instruction.actions.actions).join(",") + ")"
      break;
    case proto.InstructionType.OFPIT_GOTO_TABLE:
      stringInst = "Goto:" + instruction.goto_table.table_id.toString()
      break;
    case proto.InstructionType.OFPIT_WRITE_METADATA:
      stringInst = "WriteMetadata: " + instruction.write_metadata.metadata + "/" + instruction.write_metadata.metadata_mask
      break;
    case proto.InstructionType.OFPIT_WRITE_ACTIONS:
      stringInst = "Write(" + protoActions2Strings(instruction.actions.actions).join(",") + ")"
      break;
    case proto.InstructionType.OFPIT_CLEAR_ACTIONS:
      stringInst = "Clear(" + protoActions2Strings(instruction.actions.actions).join(",") + ")"
      break;
    default:
      console.error("not supported instruction")
      break;
  }
  return stringInst
}

/**
 * 
 * @param instructions : インストラクション
 * @returns string[]
 */
const protoInstruction2StringArray = (instructions: proto.Instruction[]): string[] => {
  const insts: string[] = []
  instructions.forEach(inst => {
    insts.push(protoInstruction2String(inst))
  })
  return insts
}

/**
 * 
 * @param matches (proto.Match[])
 * @returns string
 */
export const protoMatches2String = (matches: proto.Match[]): string => {
  let matchString = ""
  matches.forEach(m => {
    if (m.mask){
      matchString += m.field_name + "=" + m.value + "/" + m.mask
    }else{
      matchString += m.field_name + "=" + m.value
    }
    matchString += ", "
  })
  return matchString
}

/**
 * proto.Flowを表示のためのFlowに変換する
 * @param flow (proto.Flow) : 送られてきたメッセージ
 * @param matchedEntryId (number) : 強調表示するエントリー
 * @returns Flow
 */
export const protoFlow2Flow = (flow: proto.Flow, matchedEntryId: number): Flow => {
  const f = {
    "priority": flow.priority,
    "match": protoMatches2String(flow.match),
    "instruction": protoInstruction2StringArray(flow.actions).join(', '),
    "class": ""
  }
  if(flow.flow_id === matchedEntryId){
    f.class = "matched_entry"
  }
  return f
}

/**
 * 表示のためにFlowに変換する関数
 * @param flowTable : フローテーブル
 * @param tableId : 表示したいテーブルid
 * @param matchedEntryId : マッチし，強調表示するエントリid
 */
export const protoFlowTable2ArrayForView = (flowTable: proto.FlowTable, tableId: number, matchedEntryId: number): Flow[] => {
  const flows: Flow[] = []
  flowTable.flows.forEach(f => {
    if(f.table === tableId){
      flows.push(protoFlow2Flow(f, matchedEntryId))
    }
  })
  return flows
}
