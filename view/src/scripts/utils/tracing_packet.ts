import { PacketProcessing, FlowTable, Instruction, InstructionType, Packet, Match, Action, Flow } from '../remote/net_pb'

/**
 * PacketProcessingData
 */
export interface PacketProcessingData {
  packetProcessing: PacketProcessing
}


/**
 * パケット更新の様子
 */
export interface UpdatePacket {
  packetBefore: Map<string, string>,
  packetAfter: Map<string, string>,
  applyedFlow: Flow,
  applyedActions: string[]
  beforeActionSet: string[]
  afterActionSet: string[]
  applyedActionSet: string[]
  goto: number

  inPort: string
  beforeTable: number
  outPort: string

  isApplyAction: boolean
}


/**
 * フローidのフローを取り出す
 * @param flowTable : フローテーブル
 * @param flowId : フローのid
 * @returns Flow | null
 */
export const getFlow = (flowTable: FlowTable, flowId: number): Flow | null => {
  let flow: Flow = null
  flowTable.getFlowsList().forEach(f => {
    if(f.getFlowId() === flowId){
      flow = f
    }
  })
  return flow
}


/**
 * マッチしたフローの配列から，マッチしたフローテーブルの配列に変換
 * @param matchedFlows : マッチしたフロー
 * @param flowTable : フローテーブル
 * @returns number[] : マッチしたフローテーブルの列
 */
export const matchedFlows2matchedTables = (matchedFlows: number[], flowTable: FlowTable): number[] => {
  const tables: number[] = []
  matchedFlows.forEach(f => {
    tables.push(getFlow(flowTable, f).getTable())
  })
  return tables
}


/**
 * Actionを文字列の配列に変換
 * @param actions : 適用されたアクション
 * @returns string[] : アクションの文字列の配列
 */
export const protoActions2Strings = (actions: Action[]): string[] =>{
  const str: string[] = []
  actions.forEach(a =>{
    str.push(a.getStr())
  })
  return str
}


/**
 * Action Set before/after
 */
interface UpdateActionSet {
  before: string[],
  after: string[]
}


/**
 * 
 * @param beforeFlows : マッチしたFlowの前のflow
 * @param currentWriteActions : 今回書き込むActionSet
 * @returns UpdateActionSet
 */
const getActionSetBeforeAfter = (beforeFlows: Flow[], currentWriteActions: string[]): UpdateActionSet => {
  const beforeActions: string[] = []

  beforeFlows.forEach(flow => {
    const insts: Instruction[] = flow.getActionsList()
    // Instructionの解析
    insts.forEach(inst => {
      if(inst.getType() === InstructionType.OFPIT_WRITE_ACTIONS){
        protoActions2Strings(inst.getActions().getActionsList()).forEach(s => {
          beforeActions.push(s)
        })
      }else if(inst.getType() === InstructionType.OFPIT_CLEAR_ACTIONS){
        beforeActions.splice(0, beforeActions.length)
      }
    })
  })

  const afterActions: string[] = Array.from(beforeActions)
  currentWriteActions.forEach(s => {
    afterActions.push(s)
  })

  return {
    'before': beforeActions, 
    'after': afterActions
  }
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
export const getPacketBeforeAfter = (pkts: Packet[], matchedFlows: number[], currentIndex: number, flowTable: FlowTable): UpdatePacket => {
  // return value
  const updatePacket = {applyedActions: [], applyedActionSet: []} as UpdatePacket
  let isClear = false
  let beforeTable = -1

  // convert map
  updatePacket.packetBefore = pkts[currentIndex].getFieldsMap() as unknown as Map<string, string>

  // for actionset
  const beforeFlows: Flow[] = []
  matchedFlows.slice(0, currentIndex).forEach(flow_number => {
    const f = getFlow(flowTable, flow_number)
    beforeFlows.push(f)
    beforeTable = f.getTable()
  })
  let currentActionSet: string[] = []

  // get next packet
  if(currentIndex < pkts.length - 1){
    const nextIndex = currentIndex +1
    updatePacket.packetAfter = pkts[nextIndex].getFieldsMap() as unknown as Map<string, string>
  }else{
    updatePacket.packetAfter = updatePacket.packetBefore
  }
  
  // get applyed Flow from matched flow id
  const flow: Flow = getFlow(flowTable, 
    matchedFlows[currentIndex])
  updatePacket.applyedFlow = flow

  const insts: Instruction[] = flow.getActionsList()
  // Instructionの解析
  insts.forEach(inst => {
    if(inst.getType() === InstructionType.OFPIT_APPLY_ACTIONS){
      protoActions2Strings(inst.getActions().getActionsList()).forEach(a => {
        updatePacket.applyedActions.push(a)
      })
      updatePacket.isApplyAction = true
    }else if(inst.getType() === InstructionType.OFPIT_WRITE_ACTIONS){
      currentActionSet = protoActions2Strings(inst.getActions().getActionsList())
      updatePacket.applyedActionSet.push(protoInstruction2String(inst))
    }else if(inst.getType() === InstructionType.OFPIT_CLEAR_ACTIONS){
      isClear = true
      updatePacket.applyedActionSet.push(protoInstruction2String(inst))
    }else if(inst.getType() === InstructionType.OFPIT_GOTO_TABLE){
      updatePacket.goto = inst.getGotoTable().getTableId()
    }else if(inst.getType() === InstructionType.OFPIT_WRITE_METADATA){
      updatePacket.applyedActions.push(protoInstruction2String(inst))
    }
  })

  // ActionSetの解析
  const updateActionSet: UpdateActionSet = getActionSetBeforeAfter(beforeFlows, currentActionSet)
  updatePacket.beforeActionSet = updateActionSet.before
  if(isClear){
    updatePacket.afterActionSet = []
  }else{
    updatePacket.afterActionSet = updateActionSet.after
  }


  // in packet / out packet
  if(currentIndex === 0){
    updatePacket.inPort = pkts[currentIndex].getInPort()
  }else{
    updatePacket.inPort = "table = " + beforeTable
  }

  return updatePacket
}


/**
 * 表示する際のフローのインターフェース
 */
export interface showedFlow {
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
const protoInstruction2String = (instruction: Instruction): string => {
  let stringInst: string = ""
  switch (instruction.getType()) {
    case InstructionType.OFPIT_APPLY_ACTIONS:
      stringInst = "Apply(" + protoActions2Strings(instruction.getActions().getActionsList()).join(",") + ")"
      break;
    case InstructionType.OFPIT_GOTO_TABLE:
      stringInst = "Goto(" + instruction.getGotoTable().getTableId().toString() + ")"
      break;
    case InstructionType.OFPIT_WRITE_METADATA:
      stringInst = "WriteMetadata(" + instruction.getWriteMetadata().getMetadata() + "/" + instruction.getWriteMetadata().getMetadataMask() + ")"
      break;
    case InstructionType.OFPIT_WRITE_ACTIONS:
      stringInst = "Write(" + protoActions2Strings(instruction.getActions().getActionsList()).join(",") + ")"
      break;
    case InstructionType.OFPIT_CLEAR_ACTIONS:
      stringInst = "Clear(" + protoActions2Strings(instruction.getActions().getActionsList()).join(",") + ")"
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
const protoInstruction2StringArray = (instructions: Instruction[]): string[] => {
  const insts: string[] = []
  instructions.forEach(inst => {
    insts.push(protoInstruction2String(inst))
  })
  return insts
}


/**
 * 
 * @param matches (Match[])
 * @returns string
 */
export const protoMatches2String = (matches: Match[]): string => {
  let matchString = ""
  matches.forEach(m => {
    if (m.getMask()){
      matchString += m.getFieldName() + "=" + m.getValue() + "/" + m.getMask()
    }else{
      matchString += m.getFieldName() + "=" + m.getValue()
    }
    matchString += ", "
  })
  return matchString
}


/**
 * Flowを表示のためのFlowに変換する
 * @param flow (Flow) : 送られてきたメッセージ
 * @param matchedEntryId (number) : 強調表示するエントリー
 * @returns showedFlow
 */
export const protoFlow2showedFlow = (flow: Flow, matchedEntryId: number): showedFlow => {
  const f = {
    "priority": flow.getPriority(),
    "match": protoMatches2String(flow.getMatchList()),
    "instruction": protoInstruction2StringArray(flow.getActionsList()).join(', '),
    "class": ""
  }
  if(flow.getFlowId() === matchedEntryId){
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
export const protoFlowTable2ArrayForView = (flowTable: FlowTable, tableId: number, matchedEntryId: number): showedFlow[] => {
  const flows: showedFlow[] = []
  flowTable.getFlowsList().forEach(f => {
    if(f.getTable() === tableId){
      flows.push(protoFlow2showedFlow(f, matchedEntryId))
    }
  })
  return flows
}
