<template>
  <div id="update-action-set">

    <!-- Action Set -->
    <div 
      id="action-set-before-update"
      class="action-set-table">
      <span
        class="action"
        v-for="action in actionSetBefore"
        :key="action.id"
      >
      {{ action }}
      </span>
    </div>
      
    <div class="action-set-update-arrow-container">
      <span class="write-action">
          Write(Output1)
      </span>
      <div class="action-set-update-arrow">
        <svg>
          <marker 
            id="arrow" 
            viewBox="-5 -5 10 10" 
            orient="auto">
            <polygon 
              points="-5,-5 5,0 -5,5" 
              :fill="arrowColor" 
              stroke="none" />
          </marker>
          <line
            id="action-set-update-arrow"
            x1="50" y1="25" x2="250" y2="25" 
            :stroke="arrowColor" 
            stroke-width="10" 
            marker-end="url(#arrow)" /> 
        </svg>
      </div>
    </div>

    <!-- Action Set -->
    <div 
      id="action-set-after-update"
      class="action-set-table">
      <span
        class="action"
        v-for="action in actionSetAfter"
        :key="action.id"
      >
      {{ action }}
      </span>
      </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue'

export default defineComponent({
  name: "UpdateActionSet",
  props: {
    actionSetBefore: {
      type: Array,
      default: () => {
        const defaultList: string[] = []
        return defaultList
      }
    },
    actionSetAfter: {
      type: Array,
      default: () => {
        return ["output: 1"]
      }
    }
  },
  setup(props){
    const arrowColor = ref("#2F3437")
    console.log("UpdateActionSet")
    return {
      arrowColor
    }
  }
})
</script>

<style lang="scss">
#update-action-set{
  display: flex;
  flex-direction: row;
  justify-content: center;
  align-items: center;
  font-size: 1.5rem;

  .action-set-table{
    display: flex;
    flex-direction: column-reverse;
    text-align: center;
    width: 20rem;
    height: 12rem;
    background-color: #eeffee;

    .action{
      display: inline-block;
      width: 100%;
      padding: 0.5rem 0;
      font-size: 1.7rem;
      background-color: palevioletred;
    }
  }
  
  .action-set-update-arrow-container{
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    width: 30rem;
    height: 20rem;
    font-size: 1.5rem;
    color: #2F3437;
    .action-set-update-arrow{
      width: 30rem;
      height: 10rem;
    }
  }
}
</style>
