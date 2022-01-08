<template>
  <div id="update-packet">

    <!-- Inport -->
    <transition name="packet-update-arrow">
      <div class="packet-update-arrow-container before">

        <span>{{ input }}</span>

        <div class="packet-update-arrow before">
          <svg>
            <marker 
              id="arrow" 
              viewBox="-5 -5 10 10" 
              orient="auto">
              <polygon 
                points="-5,-5 5,0 -5,5"
                :fill="arrowColor" 
                :stroke="arrowColor" />
            </marker>
            <line
              id="packet-update-arrow"
              x1="5" y1="50" x2="25" y2="50" 
              :stroke="arrowColor" 
              stroke-width="5" 
              marker-end="url(#arrow)" /> 
          </svg>
        </div>

      </div>
    </transition>
    

    <!-- before action packet -->
    <transition name="packet-before-update">
      <table id="packet-before-update"
        class="packet-header-table">
        <tr 
          v-for="[key, value] in Array.from(packetBefore.entries())"
          :key="key">
          <th>{{ key }}</th><td>{{ value }}</td>
        </tr>
      </table>
    </transition>
      
    <!-- before to after -->
    <transition name="packet-update-arrow">
      <div class="packet-update-arrow-container">
        <!-- applyed action (Apply Action, Write Metadata) -->
        <span 
          class="packet-apply-action"
          v-for="applyedAction in applyedActions"
          :key="applyedAction.id">
          {{ applyedAction }}
        </span>
        <div class="packet-update-arrow">
          <svg>
            <marker 
              id="arrow" 
              viewBox="-5 -5 10 10" 
              orient="auto">
              <polygon 
                points="-5,-5 5,0 -5,5"
                :fill="arrowColor" 
                :stroke="arrowColor" />
            </marker>
            <line
              id="packet-update-arrow"
              x1="50" y1="20" x2="250" y2="20" 
              :stroke="arrowColor" 
              stroke-width="10" 
              marker-end="url(#arrow)" /> 
          </svg>
        </div>
      </div>
    </transition>

    <!-- After action packet -->
    <transition name="packet-update-arrow">
      <table id="packet-after-update"
        class="packet-header-table">
        <tr 
          v-for="[key, value] in Array.from(packetAfter.entries())"
          :key="key">
          <th>{{ key }}</th><td>{{ value }}</td>
        </tr>
      </table>
    </transition>

    <!-- Out Port -->
    <transition name="packet-update-arrow">

      <div class="packet-update-arrow-container after">
        <div class="packet-update-arrow after">
          <svg>
            <marker 
              id="arrow" 
              viewBox="-5 -5 10 10" 
              orient="auto">
              <polygon 
                points="-5,-5 5,0 -5,5"
                :fill="arrowColor" 
                :stroke="arrowColor" />
            </marker>
            <line
              id="packet-update-arrow"
              x1="5" y1="50" x2="25" y2="50" 
              :stroke="arrowColor" 
              stroke-width="5" 
              marker-end="url(#arrow)" /> 
          </svg>
        </div>

        <span>{{ output }} <br> {{ goto_s }}</span>

      </div>
    </transition>

  </div>
</template>

<script lang="ts">
import { defineComponent, ref, watchEffect, PropType } from 'vue'

/**
 * パケットのアップデートを表示．
 * 
 * This component required the information following:
 * * packet
 * * updated packet
 * * chaged information
 * 
 * @todo:
 *    * インポートなどにどこのポートかを表示する
 */
export default defineComponent({
  name: "UpdatePacket",
  props: {
    /**
     * 更新する前のパケット
     */
    packetBefore: {
      type: Map,
      default: ()=>{  // test data
        return {
          "InPort" : "1",
          "InPhyPort" : "1",
          "EtherSrc" : "b6:37:ea:8b:d6:81",
          "EtherDst" : "ff:ff:ff:ff:ff:ff",
          "EtherType" : "ARP",
          "IPSrc" : "10.0.0.1",
          "IPDst" : "10.0.0.15",
        }
      }
    },
    /**
     * 更新された後のパケット
     */
    packetAfter: {
      type: Map,
      default: ()=>{  // test data
        return {
          "InPort" : "1",
          "InPhyPort" : "1",
          "EtherSrc" : "b6:37:ea:8b:d6:81",
          "EtherDst" : "ff:ff:ff:ff:ff:ff",
          "EtherType" : "ARP",
          "VlanID" : "1",
          "IPSrc" : "10.0.0.1",
          "IPDst" : "10.0.0.15",
        }
      }
    },
    /**
     * 適用されたアクション(Applyed Action, Write metadata)
     */
    applyedActions: {
      type: Array,
      default: ()=>{  // test data
        return [""]
      }
    },
    /**
     * in port
     */
    inPort: {
      type: String
    },
    /**
     * out ports
     */
    outPorts: {
      type: Array as PropType<string[]>
    },
    /**
     * before Table
     */
    beforeTable: {
      type: Number
    },
    /**
     * got table
     */
    goto: {
      type: Number
    }
  },
  setup(props){
    // pass
    const arrowColor = ref("#2F3437")
    const input = ref("")
    const output = ref("")
    const goto_s = ref("")

    /**
     * input string
     * 
     * todo: inputをrefで宣言しなくちゃいけなくね？
     */
    watchEffect(() => {
      let i = ""
      if(props.inPort){
        i += "in: " + props.inPort
      }
      if(props.beforeTable){
        i += "beforeTable: " + props.beforeTable
      }
      input.value = i
    })

    /**
     * output string
     */
    watchEffect(() => {
      if(props.outPorts){
        output.value = "out: " + props.outPorts
      }
      if(props.goto){
        goto_s.value = "goto: " + props.goto
      }
    })

    return {
      arrowColor,
      input,
      output,
      goto_s
    }
  }
})
</script>

<style lang="scss">
#update-packet{
  $packet_frame_color: $black;

  display: flex;
  flex-direction: row;
  justify-content: center;
  align-items: center;

  .packet-header-table{
    width: auto;
    height: auto;
    // background-color: #ffeeee;
    font-size: 1.3rem;
    border: 1px solid $packet_frame_color;
    border-collapse: collapse;
    th, td{
      border: 0.5px solid $packet_frame_color;
      border-collapse: collapse;
      padding: 2px;
    }
  }

  .packet-before-update-enter{
    opacity: 0;
  }
  .packet-before-update-enter-active{
    transition: opacity 100s;
  }
  .packet-before-update-enter-to{
    opacity: 1;
  }
  // .packet-before-update-leave{}
  // .packet-before-update-leave-active{}
  // .packet-before-update-leave-to{}


  .packet-update-arrow-container{
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    width: 35rem;
    height: 20rem;
    font-size: 1.5rem;
    color: $black;

    &.before{
      display: flex;
      flex-direction: row;
      justify-content: center;
      align-items: center;
      width: 10rem;
    }
    &.after{
      display: flex;
      flex-direction: row;
      justify-content: center;
      align-items: center;
      width: 10rem;
    }

    .packet-update-arrow{
      width: 30rem;
      height: 10rem;
      &.after{
        width: 4rem;
      }
      &.before{
        width: 4rem;
      }

      .packet-apply-action {
        margin: 0 0.5rem;
      }
    }
  }
}
</style>
