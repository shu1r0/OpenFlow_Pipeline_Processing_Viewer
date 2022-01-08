<template>
    <div id="console"></div>
</template>

<script lang="ts">
import { defineComponent, onMounted, PropType } from 'vue'
import { changeableVNet } from '../../scripts/vnet/vnet'

import { Terminal } from 'xterm'
import { FitAddon } from 'xterm-addon-fit'
import 'xterm/css/xterm.css'
import 'xterm/lib/xterm.js'
import { CommandResult, CommandResultType } from '../../scripts/remote/net_pb'


export default defineComponent({
  setup(props, ctx){
      // ansi code https://en.wikipedia.org/wiki/ANSI_escape_code
      const ESCAPE = "\x1b["
      const RED_ANSI = ESCAPE + "31m"
      const GREEN_ANSI = ESCAPE + "32m"
      const YELLOW_ANSI = ESCAPE + "33m"
      const BLUE_ANSI = ESCAPE + "34m"
      const CYAN_ANSI = ESCAPE + "36m"
      const GRAY_ANSI = ESCAPE + "90m"
      const BRIGHT_RED_ANSI = ESCAPE + "91m"
      const BRIGHT_BLUE_ANSI = ESCAPE + "94m"
      const RESET_STYLE = ESCAPE + "0m"
      
      const color = (color: string, str: string) => {
          return color + str + RESET_STYLE
      }

      /**
       *  pre command
       */
      const preCommand = (command: string): any => {
        const commands = command.split(' ')
        if(commands.length > 0){
            if(commands[0] === "viewer"){
                command = null  // no send server
                commands.splice(0, 1)  // del viewer
                ctx.emit("viewer", commands)
            }
        }
        return command
      }

    /**
     * command callback 
     * set command handler to remote client
     * 
     * @param command {string} : command
     * @param writeln {(s: string) => void} : write method (out)
     * @param writePrompt {() => void} : write prompt (out)
     */
    const commandHandler = (command: string, term: Terminal, writePrompt: ()=> void): void => {
      
      /**
       * output command handler for remote client
       */
      const commandHandler = (command: CommandResult) => {
        const str = command.getResult()
        if(command.getType() === CommandResultType.OUTPUT){
          term.write(str)
        }else if(command.getType() === CommandResultType.ERROR){
          term.write(color(BRIGHT_RED_ANSI, "Error!! " + str))
        }else if(command.getType() === CommandResultType.END_SIGNAL){
          writePrompt()
        }
      }

      command = preCommand(command)

      if(command){
        /**
         * exec on server
         */
        const remoteClient = changeableVNet.getRemoteClient()
        // set command handler
        remoteClient.execMininetCommand(command, commandHandler)
      }
    }

      onMounted(()=>{
          /**
           * terminal object
           */
          const term = new Terminal({
              rendererType: "canvas", //Rendering type
              rows: 15, //Rows 
              convertEol: true, //When enabled, the cursor will be set to the beginning of the next line
              scrollback: 30, //The amount of rollback in the terminal
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
          // command history
          const history: string[] = []

          // introduction
          term.write(color(BRIGHT_BLUE_ANSI ," Wellcome! This is Web CLI like Mininet CLI. "))
          writePrompt()

          // Input key
          // key code https://developer.mozilla.org/en-US/docs/Web/API/KeyboardEvent/key/Key_Values
          term.onKey(e => {
              const ev = e.domEvent
              const printable = !(ev.altKey || ev.ctrlKey || ev.metaKey)

              // note: ev.key causes Parsing Error
              if (ev.keyCode === 8){  // backspace
                  // eslint-disable-next-line
                  // @ts-ignore
                  if(term._core.buffer.x > prompt.length){
                      term.write('\b \b')
                      buffer = buffer.slice(0, -1)
                  }
              }else if(printable){
                  switch (ev.key){
                    case "Enter":
                        // exec command
                        if(buffer !== ""){
                            term.writeln('')
                            history.push(buffer)
                            commandHandler(buffer, term, writePrompt)
                            buffer = ""
                        }
                        break
                    case "Tab":
                        console.log("tab")
                        break
                    case "ArrowDown":
                        console.log("down")
                        break
                    case "ArrowLeft":
                        console.log("left")
                        break
                    case "ArrowRight":
                        console.log("right")
                        break
                    case "ArrowUp":
                        console.log("up")
                        break
                    default:
                        term.write(e.key)
                        buffer += e.key
                        break
                  }
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