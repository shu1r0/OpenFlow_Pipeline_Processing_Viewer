<template>
    <div id="console"></div>
</template>

<script lang="ts">
import { defineComponent, onMounted, PropType } from 'vue'

import 'xterm/css/xterm.css'
import 'xterm/lib/xterm.js'
import { netConsole } from '../../scripts/console/console'


export default defineComponent({
  setup(props, ctx){

      /**
       *  pre command
       */
      const preCommand = (command: string): string => {
        const commands = command.split(' ')
        if(commands.length > 0){
            if(commands[0] === "view"){
                commands.splice(0, 1)  // del "viewer"
                ctx.emit("view", commands)
                return ""
            }
        }
        return command
      }

      onMounted(() => {
        netConsole.setPreCommand(preCommand)
        netConsole.start("console")
      })
  }
})
</script>

<style lang="scss">
.console{
  grid-area: console;
}
</style>