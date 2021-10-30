<template>
  <div
    id="tracing_vnet_view"
    class="tracing_vnet">

  
    <button @click="startTrace()">start trace</button>
    <button @click="startTraceInterval()">get trace</button>
    <button @click="stopTraceInterval()">stop</button>

    
    <div
      id="vnet_and_list">
      <!-- canvas -->
      <div
        id="tracing_vnet_canvas" />
      
      <!-- list -->
      <div id="packet_list" class="packet_list">
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
            <td>{{ trace.protocol }}</td>
            <td>
              {{ traceToString(trace) }}
            </td>
          </tr>
  
        </table>
      </div>

      <Console />
    </div>

    <!-- ここにレンダリング(予定) -->
    <tracing-packet
      v-if="isShowingPacketProcessing"
      :getPacketProcessing="getPacketProcessingForTracinPacket">
    </tracing-packet>

  </div>
</template>

<script lang="ts">
import { defineComponent, onActivated, onDeactivated, onMounted, ref, reactive } from 'vue'
import TracingPacket from './TracingPacket.vue'
import Console from '../components/tracingVNet/Console.vue'

import { changeableVNet, TracingVNet } from '../vnet/vnet'
import { proto } from '../api/net'
import { PacketProcessingData } from '../utils/tracing_packet'
import { traceToString, getPacketProcessing } from '../utils/tracing_vnet'
import { packetTracesRepository } from '../utils/packet_traces_repository'

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
    // const trace_list = ref<proto.PacketTrace[]>([])
    const trace_list = reactive([])


    let getTraceInterval: number = -1

    /**
     * 現在，描画している経路
     */
    let drawingPacketTrace: proto.PacketTrace = null
    let drawingPacketTraceid: number = null

    let isShowingPacketProcessing = ref(false)
    let showingPacketProcessing = ref<proto.PacketProcessing>(null)
    let showingPacketProcessingSwitch = ref("")

    let trace_list_test: proto.PacketTrace[] = []
    const trace1 = new proto.PacketTrace()
    trace1.protocol = 'icmp'
    const arc11 = new proto.PacketArc()
    arc11.src = 'h0'
    arc11.dst = 's1'
    const arc12 = new proto.PacketArc()
    arc12.src = 's1'
    arc12.dst = 's0'
    const arc13 = new proto.PacketArc()
    arc13.src = 's0'
    arc13.dst = 's2'
    const arc14 = new proto.PacketArc()
    arc14.src = 's2'
    arc14.dst = 'h3'
    trace1.arcs = [arc11, arc12, arc13, arc14]

    const trace2 = new proto.PacketTrace()
    trace2.protocol = 'icmp'
    const arc21 = new proto.PacketArc()
    arc21.src = 'h3'
    arc21.dst = 's2'
    const arc22 = new proto.PacketArc()
    arc22.src = 's2'
    arc22.dst = 's0'
    const arc23 = new proto.PacketArc()
    arc23.src = 's0'
    arc23.dst = 's1'
    const arc24 = new proto.PacketArc()
    arc24.src = 's1'
    arc24.dst = 'h0'
    trace2.arcs = [arc21, arc22, arc23, arc24]

    trace_list_test.push(trace1)
    trace_list_test.push(trace2)

    /**
     * TracingVNetを初期化
     */
    onActivated(() => {
      // trace_list.value = trace_list_test
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
    })

    /**
     * draw a trace on vnet
     */
    const drawTrace = (trace: proto.PacketTrace, index: number) => {
      vnet.removeAllPacketEdges()
      drawingPacketTrace = trace
      trace.arcs.forEach(arc => {
        vnet.addPacketEdge(arc.src, arc.dst)
      })
    }

    /**
     * パケットの処理の様子を可視化する機能
     */
    const showPacketProcessing = (packetProcessing: proto.PacketProcessing) => {
      isShowingPacketProcessing.value = true
      showingPacketProcessing.value = packetProcessing
      showingPacketProcessingSwitch.value = packetProcessing.switch
    }

    /**
     * スイッチがタップされたときの処理
     */
    const tapEventNodeHandler = (switchId: string) => {
      const pktproc: proto.PacketProcessing = getPacketProcessing(drawingPacketTrace, switchId)[0]
      showPacketProcessing(pktproc)
    }

    /**
     * パイプライン可視化機能へ渡す関数
     */
    const getPacketProcessingForTracinPacket = (): PacketProcessingData => {
      const data: PacketProcessingData | any = {}
      data.packetProcessing = showingPacketProcessing.value
      return data
    }

    const startTrace = () => {
      changeableVNet.getRemoteClient().startTracing()
    }

    const startTraceInterval = () => {
      const getTrace = () => {
        changeableVNet.getRemoteClient().getTrace()
        trace_list.splice(0, trace_list.length)
        packetTracesRepository.getPacketTraces().forEach(t => {
          console.log("push to list")
          console.log(t)
          trace_list.push(t)
        })
      }
      getTraceInterval = setInterval(getTrace.bind(changeableVNet.getRemoteClient()), 1000)
    }

    const stopTraceInterval = () => {
      clearInterval(getTraceInterval)
    }


    return {
      startTrace,
      startTraceInterval,
      stopTraceInterval,
      drawTrace,
      traceToString,
      getPacketProcessingForTracinPacket,
      trace_list,
      vnet,
      showingPacketProcessing
    }
  },
})
</script>


<style lang="scss">
.tracing_vnet{
  // background-color: #eeeeee;

  #vnet_and_list{
    display: grid;
    grid-template-areas: 
      "vnet-canvas trace-list"
      "console trace-list";
    grid-auto-columns: 
      minmax(70rem, 110rem)
      minmax(30rem, 50rem);
    grid-auto-rows: 
      minmax(20rem, 70rem)
      20rem;
    

    #tracing_vnet_canvas{
      grid-area: vnet-canvas;
      position: relative;  // basis for the position of child elements
      height: 1000px;
      width: auto;

      *{
        position: absolute;
      }
    }

    #packet_list {
      grid-area: trace-list;
    }
  }

  .packet_list{
  font-size: 2rem;

  table, tr, th, td{
    border: 1px solid black;
    border-collapse: collapse;
  }

  #packet_list_table{
    width: 100%;
  }
}
}
</style>
