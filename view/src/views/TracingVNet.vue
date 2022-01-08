<template>
  <div
    id="tracing_vnet_view"
    class="tracing_vnet">

  
    <button class="start_trace" @click="startTrace()">start trace</button>
    <button class="start_interval" @click="startTraceInterval()">start interval</button>
    <button class="stop_interval" @click="stopTraceInterval()">stop interval</button>

    
    <div
      id="vnet_and_list">
      <!-- canvas -->
      <div
        id="tracing_vnet_canvas" />
      
      <!-- list -->
      <div id="packet_list" class="packet_list">
        <!-- filter -->
        <!-- <select name="nodes" id="node-select">
          <option @click="getTrace()">all</option>
          <option 
            v-for="(trace, index) in trace_list"
            :key="trace.id"
            :value="index"
            @click="getTrace(trace.getArcsList()[0].getSrc())">
              {{ trace.getArcsList()[0].getSrc() }}
          </option>
        </select> -->

        <table id="packet_list_table">
          <tr>
            <th>protocol</th>
            <th>route</th>
          </tr>

          <tr
              class="trace"
              v-for="(trace, index) in trace_list"
              :key="trace.id"
              @click="drawTrace(trace, index)">
            <td>{{ trace.getProtocol() }}</td>
            <td>
              {{ traceToString(trace) }}
            </td>
          </tr>
  
        </table>
      </div>

      <!-- Mininet CLI -->
      <Console />
    </div>

    <!-- ここにレンダリング(予定) -->
    <TracingPacket
      v-if="isShowingPacketProcessing"
      :getPacketProcessing="getPacketProcessingForTracinPacket"
      @close="closePacketProcessing()" />

  </div>
</template>

<script lang="ts">
import { defineComponent, onActivated, onDeactivated, onMounted, ref, reactive } from 'vue'
import TracingPacket from './TracingPacket.vue'
import Console from '../components/tracingVNet/Console.vue'

import { changeableVNet, TracingVNet } from '../scripts/vnet/vnet'
import { PacketProcessingData } from '../scripts/utils/tracing_packet'
import { traceToString, getPacketProcessing } from '../scripts/utils/tracing_vnet'
import { packetTracesRepository } from '../scripts/utils/packet_traces_repository'
import { PacketTrace, PacketProcessing, PacketArc } from '../scripts/remote/net_pb'

export default defineComponent({
  name: 'TracingVNet',
  components: {
    TracingPacket,
    Console
  },
  setup(props, context) {
    onMounted(() => {
      console.log("TracingVNet view mounted")
    })

    /**
     * tracing vnet
     */
    let vnet: TracingVNet = null

    /**
     * 表示される経路情報のリスト
     */
    const trace_list = ref<PacketTrace[]>([])
    // const trace_list = reactive([])

    /**
     * trace interval
     */
    let getTraceInterval: number = null

    /**
     * 現在，描画している経路
     */
    let drawingPacketTrace: PacketTrace = null
    let drawingPacketTraceid: number = null

    /**
     * パケットの処理
     */
    let isShowingPacketProcessing = ref(false)
    let showingPacketProcessing = ref<PacketProcessing>(null)
    let showingPacketProcessingSwitch = ref("")

    /**
     * TracingVNetを初期化
     */
    onActivated(() => {
      console.log("TracingVNet view activated")
      const e = document.getElementById("tracing_vnet_canvas")
      vnet = new TracingVNet(changeableVNet.getRemoteClient(), e, changeableVNet)
      vnet.onTapEventsInSwitch(tapEventNodeHandler)
    })

    /**
     * destroy tracing vnet
     */
    onDeactivated(() => {
      console.log("TracingVNet view deactivated")
      vnet.cytoscape.destroy()
      vnet = null
      stopTraceInterval()
    })

    /**
     * draw a trace on vnet
     */
    const drawTrace = (trace: PacketTrace, index: number) => {
      vnet.removeAllPacketEdges()
      drawingPacketTrace = trace
      trace.getArcsList().forEach(arc => {
        vnet.addPacketEdge(arc.getSrc(), arc.getDst())
      })
    }

    /**
     * パケットの処理の様子を可視化する機能
     */
    const showPacketProcessing = (packetProcessing: PacketProcessing) => {
      isShowingPacketProcessing.value = true
      showingPacketProcessing.value = packetProcessing
      showingPacketProcessingSwitch.value = packetProcessing.getSwitch()
    }

    /**
     * close tracing packet processing
     */
    const closePacketProcessing = () => {
      isShowingPacketProcessing.value = false
    }

    /**
     * スイッチがタップされたときの処理
     */
    const tapEventNodeHandler = (switchId: string) => {
      const pktprocs = getPacketProcessing(drawingPacketTrace, switchId)
      console.log("show packet processing")
      console.log(pktprocs)
      if(pktprocs.length > 0){
        showPacketProcessing(pktprocs[0])
      }
    }

    /**
     * パイプライン可視化機能へ渡す関数
     * 
     * paketProcessingDataのゲッター
     */
    const getPacketProcessingForTracinPacket = (): PacketProcessingData => {
      const data: PacketProcessingData | any = {}
      data.packetProcessing = showingPacketProcessing.value
      return data
    }

    /**
     * Tracing Start
     */
    const startTrace = () => {
      changeableVNet.getRemoteClient().startTracing()
    }

    /**
     * Trace List Update
     */
    const getTrace = (src?: string, nodes?: string[], dst?: string) => {
      changeableVNet.getRemoteClient().getTrace()
      trace_list.value = packetTracesRepository.getPacketTraces(src, nodes, dst)
    }

    /**
     * set getTrace Interval
     */
    const startTraceInterval = () => {
      if(getTraceInterval === null){
        getTraceInterval = setInterval(getTrace.bind(changeableVNet.getRemoteClient()), 1500)
      }
    }

    /**
     * stop Interval
     */
    const stopTraceInterval = () => {
      if(getTraceInterval){
        clearInterval(getTraceInterval)
        getTraceInterval = null
      }
    }

    const viewCommand = (args: string[]) => {
      if(args.length < 2) {
        return -1
      }
      switch (args[0]) {
        case "filter":
          
          break;
        default:
          break;
      }
    }


    return {
      startTrace,
      startTraceInterval,
      stopTraceInterval,
      drawTrace,
      traceToString,
      getTrace,
      getPacketProcessingForTracinPacket,
      trace_list,
      vnet,
      showingPacketProcessing,
      closePacketProcessing,
      isShowingPacketProcessing,
      showingPacketProcessingSwitch
    }
  },
})
</script>


<style lang="scss">
.tracing_vnet{
  // background-color: #eeeeee;
  position: relative;  // basis for the position of child elements

  button {
    background: $navy;
    color: $white;
  }

  #vnet_and_list{
    display: grid;

    grid-template-areas: 
      "vnet-canvas trace-list"
      "console trace-list";
    grid-auto-columns: 
      minmax(70rem, 85rem)
      minmax(30rem, 50rem);
    grid-auto-rows: 
      minmax(20rem, 60rem)
      20rem;
    

    #tracing_vnet_canvas{
      grid-area: vnet-canvas;
      height: 800px;
      width: auto;
    }

    #packet_list {
      grid-area: trace-list;
    }
  }

  .packet_list{
  font-size: 2rem;
  border: 1px solid $black;
  border-collapse: collapse;

  table, tr, th, td{
    border: 1px solid $black;
    border-collapse: collapse;
  }

  #packet_list_table{
    width: 100%;
  }

}
}
</style>
