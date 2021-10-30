<template>
  <div id="trace-packet">
    <PipelineAndMatch
      @change-table="onChangeTable"
      :pipeline="matchedTables"
      :flow_table="flowTable"></PipelineAndMatch>
    <UpdateActionSet
      :actionSetBefore="beforeActionSet"
      :actionSetAfter="afterActionSet"></UpdateActionSet>
    <UpdatePacket></UpdatePacket>

    <button @click="close()">close</button>
  </div>
</template>

<script lang="ts">
import { defineComponent, onActivated, ref, PropType } from 'vue'

import { proto } from '../api/net'
import { getFlow, matchedFlows2matchedTables, getPacketBeforeAfter, Flow, protoFlowTable2ArrayForView, PacketProcessingData } from '../utils/tracing_packet'

import PipelineAndMatch from '../components/tracePacket/PipelineAndMatch.vue'
import UpdateActionSet from '../components/tracePacket/UpdateActionSet.vue'
import UpdatePacket from '../components/tracePacket/UpdatePacket.vue'

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
    const beforePacketFields = ref<Map<string, string>>(null)
    const afterPacketFileds = ref<Map<string, string>>(null)
    const applyedActions = ref<string[]>(null)

    /**
     * 後で考える
     */
    const beforeActionSet = ref<string[]>(null)
    const afterActionSet = ref<string[]>(null)

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
    const flowTable = ref<Flow[]>(null)

    /**
     * update view
     */
    const updateProcessing = (packetProcessing: proto.PacketProcessing) => {
      const updatePacket = getPacketBeforeAfter(packetProcessing.pkts, packetProcessing.matched_flows, currentShowingFlowTableIndex ,packetProcessing.flow_table)

      // update packet
      beforePacketFields.value = updatePacket.packetBefore
      afterPacketFileds.value = updatePacket.packetAfter
      applyedActions.value = updatePacket.applyedActions

      const matchedFlow = updatePacket.applyedFlow

      // ActionSet
      console.warn("Not Implement")
      beforeActionSet.value = []
      afterActionSet.value = []

      // MatchedTables
      matchedTables.value = matchedFlows2matchedTables(packetProcessing.matched_flows, packetProcessing.flow_table)
      flowTable.value = protoFlowTable2ArrayForView(packetProcessing.flow_table, matchedFlow.table, matchedFlow.flow_id)
    }

    /**
     * アクティブになると，0から表示する
     */
    onActivated(() => {
      //@Warning: エラー回避のため
      // eslint-disable-next-line
      const packetProcessingData: PacketProcessingData = (props.getPacketProcessing as Function)()
      const packetProcessing = packetProcessingData.packetProcessing as proto.PacketProcessing

      updateProcessing(packetProcessing)
    })

    /**
     * 表示するテーブルが変化したときの処理
     */
    const onChangeTable = (nextIndex: number) => {
      currentShowingFlowTableIndex = nextIndex

      // eslint-disable-next-line
      const packetProcessingData: PacketProcessingData = (props.getPacketProcessing as Function)()
      const packetProcessing = packetProcessingData.packetProcessing as proto.PacketProcessing

      updateProcessing(packetProcessing)
    }

    const close = () => {
      ctx.emit("close")
    }

    // props.id
    const packetEx1 = {
      "InPort" : "1",
      "InPhyPort" : "1",
      "EtherSrc" : "b6:37:ea:8b:d6:81",
      "EtherDst" : "ff:ff:ff:ff:ff:ff",
      "EtherType" : "ARP",
      "IPSrc" : "10.0.0.1",
      "IPDst" : "10.0.0.15",
    }

    const test_table = [{
            "priority": 10000, 
            "match": "inPort=1", 
            "instruction": "Apply(pushVlan:1), Goto:2, Write(Output:1)",
            "class" : "matched_entry"
          },{
            "priority": 10000, 
            "match": "inPort=2", 
            "instruction": "Apply(pushVlan:1), Goto:2, Write(Output:2)",
            "class" : ""
          },{
            "priority": 10000, 
            "match": "inPort=3", 
            "instruction": "Apply(pushVlan:1), Goto:2, Write(Output:3)",
            "class" : ""
          },{
            "priority": 10000, 
            "match": "inPort=4", 
            "instruction": "Apply(pushVlan:1), Goto:2, Write(Output:4)",
            "class" : ""
          }
        ]

    return {
      onChangeTable,
      close,
      matchedTables,
      flowTable,
      beforeActionSet,
      afterActionSet
    }
  }
})
</script>

<style lang="scss">
#trace-packet{
  display: grid;
  grid-template-areas: 
    "pipeline-and-match"
    "update-packet"
    "update-action-set";
  grid-auto-rows:
    minmax(20rem, auto)
    minmax(20rem, auto)
    minmax(20rem, auto);
  grid-auto-columns: 
    auto;
  
  #pipeline-and-match{
    grid-area: pipeline-and-match;
  }
  #update-action-set{
    grid-area: update-action-set;
  }
  #update-packet{
    grid-area: update-packet;
  }
}
</style>
