<template>
  <div
    id="tracing_vnet_view"
    class="tracing_vnet">

    <div
      id="vnet_and_list">
      <div
        id="tracing_vnet_canvas" />
      
      <div id="packet_list" class="packet_list">
        <table id="packet_list_table">
          <tr>
            <th>protocol</th>
            <th>route</th>
          </tr>
          <tr
              class="trace"
              v-for="trace in trace_list_test"
              :key="trace.id"
              @click="drawTrace(trace)">
            <td>{{ trace.protocol }}</td>
            <td>
              {{ traceToString(trace) }}
            </td>
          </tr>
        </table>
      </div>
    </div>

    <button @click="onClick()">test arc</button>
  </div>
</template>

<script lang="ts">
import { defineComponent, onActivated, onDeactivated, onMounted, ref } from 'vue'

import { changeableVNet, TracingVNet } from '../vnet/vnet'
import { proto } from '../api/net'

export default defineComponent({
  name: 'TracingVNet',
  setup(props, context) {
    onMounted(() => {
      console.log("TracingVNet view mounted")
    })

    /**
     * tracing vnet
     */
    let vnet = null

    /**
     * TracingVNetを初期化
     */
    onActivated(() => {
      console.log("TracingVNet view activated")
      const e = document.getElementById("tracing_vnet_canvas")
      vnet = new TracingVNet(changeableVNet.getRemoteClient(), e, changeableVNet)
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
    const drawTrace = (trace: proto.PacketTrace) => {
      vnet.removeAllPacketEdges()
      trace.arcs.forEach(arc => {
        vnet.addPacketEdge(arc.src, arc.dst)
      })
    }

    const traceToString = (trace: proto.PacketTrace) => {
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


    /**
     * テストコード
     */
    const onClick = () => {
      vnet.addPacketEdge("h0", "s1")
      vnet.addPacketEdge("s1", "s0")
      vnet.addPacketEdge("s0", "s2")
      vnet.addPacketEdge("s2", "h3")
    }

    const trace_list_test = []
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

    return {
      onClick,
      drawTrace,
      traceToString,
      trace_list_test,
      vnet
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
      "vnet-canvas trace-list";
    grid-auto-columns: 
      minmax(70rem, 110rem)
      minmax(30rem, 50rem);
    grid-auto-rows: 
    minmax(20rem, 100rem);
    

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
