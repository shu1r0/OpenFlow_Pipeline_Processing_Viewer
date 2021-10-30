<template>
  <div id="pipeline-and-match">

    <div id="pipeline">
      <!-- in packet -->
      <span id="in-packet">In packet</span>

      <!-- table and arrow  (複数テーブルにやる) -->
      <svg class="pipeline-arrow">
        <marker 
          id="arrow" 
          viewBox="-5 -5 10 10" 
          orient="auto">
          <polygon 
            points="-5,-5 5,0 -5,5" 
            fill="black" 
            stroke="none" />
        </marker>
        <line
          id="pipeline-arrow"
          x1="10" y1="20" x2="40" y2="20" 
          stroke="black" 
          stroke-width="4" 
          marker-end="url(#arrow)" /> 
      </svg>
      <template 
        v-for="(tableNumber, index) in pipeline"
        :key="tableNumber.id">
        <span 
          class="table"
          @click="changeTable(index)">
          {{ tableNumber }}
        </span>
        <svg class="pipeline-arrow">
          <use xlink:href="#pipeline-arrow" />
        </svg>
      </template>

      <!-- out packet -->
      <span id="out-packet">Out packet</span>
    </div>

    <!-- flow table and match entry -->
    <div id="match-container">
      <table id="match">
        <tr class="flow-entry-element-header">
          <th class="flow-entry-element-header">priority</th>
          <th class="flow-entry-element-header">match</th>
          <th class="flow-entry-element-header">instruction</th>
        </tr>
        <template
          v-for="flow_entry in flow_table" 
          :key="flow_entry.id">
          <tr :class="flow_entry.class">
            <td>{{ flow_entry.priority }}</td>
            <td>{{ flow_entry.match }}</td>
            <td>{{ flow_entry.instruction }}</td>
          </tr>
        </template>
      </table>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import { Flow } from '../../utils/tracing_packet'

export default defineComponent({
  name: "PipelineAndMatch",
  props: {
    /**
     * pipeline
     */
    pipeline: {
      type: Array,
      default: () => [1, 2, 3],
      required: true
    },
    /**
     * flow table
     */
    flow_table: {
      type: Array
    }
  },
  setup(props, ctx){
    const changeTable = (clickedIndex: number) => {
      console.log("click index " + clickedIndex.toString())
      ctx.emit('change-table', clickedIndex)
    }

    return {
      changeTable
    }
  }
})
</script>

<style lang="scss">
#pipeline-and-match{
  display: grid;
  grid-template-areas: 
    "pipeline"
    "match";
  grid-auto-rows: auto;
  grid-auto-columns: auto;
  justify-content: center;

  #pipeline{
    grid-area: "pipeline";
    display: inline-flex;
    flex-direction: row;
    flex-wrap: nowrap;
    justify-content: center;
    align-items: center;

    span{
      display: inline-block;
      width: 4rem;
      height: 4rem;
      margin: 2rem;
    }
    .table{
      display: table-cell;
      // background-color: red;
      border: 1.5px solid #cccccc;
      font-size: 2rem;
      padding: 0;
      text-align: center;
      vertical-align: bottom;
    }
    svg.pipeline-arrow{
      display: inline-block;
      width: 50px;
      height: 40px;
      margin: 20px 10px;
    }
  }

  table, th, td{
    border: 1px solid black;
    border-collapse: collapse;
  }
  #match-container{
    overflow-y: scroll;
    height: 10rem;
  }
  #match{
    grid-area: match;
    width: 50rem;
    height: auto;
    text-align: center;
    margin: 0 auto;
    .matched_entry{
      background-color: yellow;
    }
    th{
      font-size: 1.7rem;
    }
    td{
      font-size: 1.5rem;
    }
  }
}
</style>
