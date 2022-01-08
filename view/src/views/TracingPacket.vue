<template>
  <div id="trace-packet">
    <PipelineAndMatch
      @change-table="onChangeTable"
      :pipeline="matchedTables"
      :flow_table="flowTable" />

    <UpdateActionSet
      :actionSetBefore="beforeActionSet"
      :actionSetAfter="afterActionSet"
      :applyedActionSet="applyedActionSet" />

    <UpdatePacket
      :packetBefore="beforePacketFields"
      :packetAfter="afterPacketFields"
      :applyedActions="applyedActions"
      :inPort="inPort"
      :outPorts="outPorts"
      :beforeTable="beforeTable"
      :goto="goto" />

    <div class="option">
      <button @click="close()">close</button>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, PropType, onMounted } from 'vue'

import { getFlow, matchedFlows2matchedTables, getPacketBeforeAfter, protoFlowTable2ArrayForView, PacketProcessingData, showedFlow } from '../scripts/utils/tracing_packet'

import PipelineAndMatch from '../components/tracePacket/PipelineAndMatch.vue'
import UpdateActionSet from '../components/tracePacket/UpdateActionSet.vue'
import UpdatePacket from '../components/tracePacket/UpdatePacket.vue'
import { PacketProcessing } from '../scripts/remote/net_pb'

/**
 * Trace Packet
 * 
 * これはスイッチが選択されたときに追加されます．
 * よって，スイッチのidは得ることができます．
 * パイプラインの情報はデータベースから得る
 * 
 * このコンポーネントは，パケットの経路情報とその付随する情報が必要
 */
export default defineComponent({
  name: "TracePacket",
  components: {
    PipelineAndMatch,
    UpdatePacket,
    UpdateActionSet
  },
  props: {
    /**
     * packets
     */
    packets: {
      type: Array,
      default: () => {
        return ["test", "test"]
      }
    },
    /**
     * 親コンポーネントからパケットの処理内容を取得するメソッド
     * このコンポーネントが作られたときにトリガーしたい
     */
    getPacketProcessing: {
      type: Function as PropType<() => PacketProcessingData>
    }
  },
  setup(props, ctx){

    /**
     * 現在表示しているフローテーブルの順番
     * 
     * 書き換わるのは，子コンポーネントからイベントを受け取ったとき
     */
    let currentShowingFlowTableIndex = 0

    /**
     * これはパケットのデータであり，再代入することでリアクティブになる
     * 
     * Notes:
     *   * 別にreactiveでもいいが，フィルタがめんどい
     */
    const beforePacketFields = ref<Map<string, string>>(new Map())
    const afterPacketFields = ref<Map<string, string>>(new Map())
    // Applyed action (APPLY_ACTION and Write metadata)
    const applyedActions = ref<string[]>(null)

    /**
     * 後で考える
     */
    const beforeActionSet = ref<string[]>([])
    const afterActionSet = ref<string[]>([])
    const applyedActionSet = ref<string[]>([])

    /**
     * input
     */
    const inPort = ref<string>()
    const beforeTable = ref<number>()

    /**
     * output 
     */
    const goto = ref<number>(null)
    const outPorts = ref<string[]>([])

    /**
     * Examples:
     *    `[1, 2, 3]`
     */
    const matchedTables = ref<number[]>(null)

    /**
     * @example :
     * ```
     *    [{
            "priority": 10000, 
            "match": "inPort=1", 
            "instruction": "Apply(pushVlan:1), Goto:2, Write(Output:1)",
            "class" : "matched_entry"
          },{
            "priority": 10000, 
            "match": "inPort=2", 
            "instruction": "Apply(pushVlan:1), Goto:2, Write(Output:2)",
            "class" : ""
          }]
      ```
     */
    const flowTable = ref<showedFlow[]>(null)

    /**
     * update view
     */
    const updateProcessing = (packetProcessing: PacketProcessing) => {
      console.log("update processing")

      const updatePacket = getPacketBeforeAfter(packetProcessing.getPktsList(), packetProcessing.getMatchedFlowsList(), currentShowingFlowTableIndex ,packetProcessing.getFlowTable())
      // console.debug(updatePacket)

      // update packet
      beforePacketFields.value = updatePacket.packetBefore
      // console.debug(beforePacketFields)
      afterPacketFields.value = updatePacket.packetAfter
      // console.debug(afterPacketFields)
      applyedActions.value = updatePacket.applyedActions
      // console.debug(applyedActions)

      const matchedFlow = updatePacket.applyedFlow

      // ActionSet
      beforeActionSet.value = updatePacket.beforeActionSet
      // console.debug(beforeActionSet)
      afterActionSet.value = updatePacket.afterActionSet
      // console.debug(afterActionSet)
      applyedActionSet.value = updatePacket.applyedActionSet

      // MatchedTables
      matchedTables.value = matchedFlows2matchedTables(packetProcessing.getMatchedFlowsList(), packetProcessing.getFlowTable())
      flowTable.value = protoFlowTable2ArrayForView(packetProcessing.getFlowTable(), matchedFlow.getTable(), matchedFlow.getFlowId())

      // next table
      goto.value = updatePacket.goto

      // out ports
      outPorts.value = []
      if(updatePacket.isApplyAction){
        outPorts.value = Array.from(packetProcessing.getOutsMap().keys())
      }

      // inport 
      inPort.value = updatePacket.inPort
      beforeTable.value = updatePacket.beforeTable
    }

    /**
     * アクティブになると，0から表示する
     */
    onMounted(() => {
      //@Warning: エラー回避のため
      // eslint-disable-next-line
      const packetProcessingData: PacketProcessingData = (props.getPacketProcessing as Function)()
      const packetProcessing = packetProcessingData.packetProcessing as PacketProcessing

      updateProcessing(packetProcessing)
    })

    /**
     * 表示するテーブルが変化したときの処理
     */
    const onChangeTable = (nextIndex: number) => {
      currentShowingFlowTableIndex = nextIndex

      // eslint-disable-next-line
      const packetProcessingData: PacketProcessingData = (props.getPacketProcessing as Function)()
      const packetProcessing = packetProcessingData.packetProcessing as PacketProcessing

      updateProcessing(packetProcessing)
    }

    /**
     * send close event
     */
    const close = () => {
      ctx.emit("close")
    }

    // // props.id
    // const packetEx1 = {
    //   "InPort" : "1",
    //   "InPhyPort" : "1",
    //   "EtherSrc" : "b6:37:ea:8b:d6:81",
    //   "EtherDst" : "ff:ff:ff:ff:ff:ff",
    //   "EtherType" : "ARP",
    //   "IPSrc" : "10.0.0.1",
    //   "IPDst" : "10.0.0.15",
    // }

    // const test_table = [{
    //         "priority": 10000, 
    //         "match": "inPort=1", 
    //         "instruction": "Apply(pushVlan:1), Goto:2, Write(Output:1)",
    //         "class" : "matched_entry"
    //       },{
    //         "priority": 10000, 
    //         "match": "inPort=2", 
    //         "instruction": "Apply(pushVlan:1), Goto:2, Write(Output:2)",
    //         "class" : ""
    //       },{
    //         "priority": 10000, 
    //         "match": "inPort=3", 
    //         "instruction": "Apply(pushVlan:1), Goto:2, Write(Output:3)",
    //         "class" : ""
    //       },{
    //         "priority": 10000, 
    //         "match": "inPort=4", 
    //         "instruction": "Apply(pushVlan:1), Goto:2, Write(Output:4)",
    //         "class" : ""
    //       }
    //     ]

    return {
      onChangeTable,
      close,
      matchedTables,
      flowTable,
      beforeActionSet,
      afterActionSet,
      applyedActionSet,
      beforePacketFields,
      afterPacketFields,
      applyedActions,
      inPort,
      beforeTable,
      goto,
      outPorts
    }
  }
})
</script>

<style lang="scss">
#trace-packet{

  position: absolute;
  top: 20px;
  left: 20px;
  display: grid;
  background-color: white;
  border: 1px solid $black;

  grid-template-areas: 
    "option"
    "pipeline-and-match"
    "update-packet"
    "update-action-set";
  grid-auto-rows:
    minmax(1rem, 2rem)
    minmax(30rem, auto)
    minmax(20rem, auto)
    minmax(20rem, auto);
  grid-auto-columns: 
    auto;
  grid-gap: 3px;
  
  #pipeline-and-match{
    grid-area: pipeline-and-match;
  }
  #update-action-set{
    grid-area: update-action-set;
  }
  #update-packet{
    grid-area: update-packet;
  }
  .option{
    grid-area: option;
  }
}
</style>
