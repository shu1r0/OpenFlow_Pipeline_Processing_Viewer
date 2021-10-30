<template>
    <div id="console"></div>
</template>

<script lang="ts">
import { defineComponent, onMounted, PropType } from 'vue'
import { changeableVNet } from '../../vnet/vnet'
import { proto } from '../../api/net'

import { Terminal } from 'xterm'
import { FitAddon } from 'xterm-addon-fit'
import 'xterm/css/xterm.css'
import 'xterm/lib/xterm.js'


export default defineComponent({
  // props: {
  //   // todo: やや濃いからもう，remoteClientから受け取ることにする
  //   commandHandler: {
  //     type: Function as PropType<(command: string, writeln: (s: string)=> void, writePrompt: ()=> void) => void>
  //   }
  // },
  setup(props){
    const commandHandler = (command: string, writeln: (s: string)=> void, writePrompt: ()=> void): void => {
      const commandHandler = (command: proto.CommandResult) => {
        const str = command.result
        if(command.type === proto.CommandResultType.OUTPUT){
          writeln(str)
        }else if(command.type === proto.CommandResultType.ERROR){
          writeln("Error!! " + str)
        }else if(command.type === proto.CommandResultType.END_SIGNAL){
          writePrompt
        }
      }
      const remoteClient = changeableVNet.getRemoteClient()
      remoteClient.execMininetCommand(command, commandHandler)
    }

      onMounted(()=>{
          const term = new Terminal({
              rendererType: "canvas", //Rendering type
              rows: 20, //Rows 
              convertEol: true, //When enabled, the cursor will be set to the beginning of the next line
              scrollback: 10, //The amount of rollback in the terminal
              disableStdin: false, //Whether input should be disabled
              cursorStyle: "underline", //Cursor style
              cursorBlink: true, //Cursor blinks
              theme: {
                  foreground: "#fefefe", //Font
                  background: "#101010", //Background color
                  cursor: "#fefefe" //Set cursor
              }
          })
          // addon
          const fitAddon = new FitAddon()
          term.loadAddon(fitAddon)
          term.open(document.getElementById('console') as HTMLElement)
          fitAddon.fit()

          // terminal prompt
          const prompt = 'mininet> '
          const writePrompt = () => {
              term.writeln('')
              term.write(prompt)
          }

          // command buffer
          let buffer = ""

          // term.writeln('Hello')
          writePrompt()

          // Input key
          term.onKey(e => {
              const ev = e.domEvent
              const printable = !ev.altKey && !ev.ctrlKey && !ev.metaKey

              if(ev.key === 'Enter'){
                  // exec command
                  if(buffer !== ""){
                      term.writeln('')
                      commandHandler(buffer, term.writeln, writePrompt)
                      buffer = ""
                  }

                  // writePrompt()
              }
              // note: ev.key causes Parsing Error
              else if (ev.keyCode === 8){  // backspace
                  // eslint-disable-next-line
                  // @ts-ignore
                  if(term._core.buffer.x > prompt.length){
                      term.write('\b \b')
                      buffer = buffer.slice(0, -1)
                  }
              }else if(printable){
                  term.write(e.key)
                  buffer += e.key
              }
          })
      })
  }
})
</script>

<style lang="scss">
.console{
  grid-area: console;
}
</style>