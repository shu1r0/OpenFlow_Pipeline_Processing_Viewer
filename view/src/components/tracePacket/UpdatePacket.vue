<template>
  <div id="update-packet">

    <transition name="packet-update-arrow">
      <!-- before action -->
      <div class="packet-update-arrow-container before">
        <span>Inport: 1</span>
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
    
    <transition name="packet-before-update">
      <table id="packet-before-update"
        class="packet-header-table">
        <tr 
          v-for="(value, key) in packetBefore"
          :key="key">
          <th>{{ key }}</th><td>{{ value }}</td>
        </tr>
      </table>
    </transition>
      
    <transition name="packet-update-arrow">
      <div class="packet-update-arrow-container">
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

    <transition name="packet-update-arrow">
      <table id="packet-after-update"
        class="packet-header-table">
        <tr 
          v-for="(value, key) in packetAfter"
          :key="key">
          <th>{{ key }}</th><td>{{ value }}</td>
        </tr>
      </table>
    </transition>

    <transition name="packet-update-arrow">
      <!-- after action -->
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
        <span>Goto: 2</span>
      </div>
    </transition>

  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue'

/**
 * パケットのアップデートを表示．
 * 
 * This component required the information following:
 * * packet
 * * updated packet
 * * chaged information
 */
export default defineComponent({
  name: "UpdatePacket",
  props: {
    /**
     * 更新する前のパケット
     */
    packetBefore: {
      type: Object,
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
      type: Object,
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
     * 適用されたアクション
     */
    applyedActions: {
      type: Array,
      default: ()=>{  // test data
        return ["pushVlan: 1"]
      }
    }
  },
  setup(props){
    // pass
    const arrowColor = ref("#2F3437")

    return {
      arrowColor
    }
  }
})
</script>

<style lang="scss">
#update-packet{
  display: flex;
  flex-direction: row;
  justify-content: center;
  align-items: center;

  .packet-header-table{
    width: auto;
    height: auto;
    // background-color: #ffeeee;
    font-size: 1.3rem;
    border: 1px solid #dddddd;
    border-collapse: collapse;
    th, td{
      border: 0.5px solid #dddddd;
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
    width: 30rem;
    height: 20rem;
    font-size: 1.5rem;
    color: #2F3437;

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
    }
  }
}
</style>
