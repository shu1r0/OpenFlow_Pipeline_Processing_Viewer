<template>
  <div id="trace-packet">
    <PipelineAndMatch></PipelineAndMatch>
    <UpdateActionSet></UpdateActionSet>
    <UpdatePacket></UpdatePacket>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue'
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
    }
  },
  setup(props, ctx){
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
