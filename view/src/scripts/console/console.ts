import { Terminal } from 'xterm'
import { FitAddon } from 'xterm-addon-fit'
import 'xterm/css/xterm.css'
import 'xterm/lib/xterm.js'
import { CommandResult, CommandResultType } from '../../scripts/remote/net_pb'

import { changeableVNet, VNet } from '../../scripts/vnet/vnet'
import { RemoteClient } from '../remote/remoteClient'


// ansi code https://en.wikipedia.org/wiki/ANSI_escape_code
const ESCAPE = "\x1b["

export const RED_ANSI = ESCAPE + "31m"
export const GREEN_ANSI = ESCAPE + "32m"
export const YELLOW_ANSI = ESCAPE + "33m"
export const BLUE_ANSI = ESCAPE + "34m"
export const CYAN_ANSI = ESCAPE + "36m"
export const GRAY_ANSI = ESCAPE + "90m"
export const BRIGHT_RED_ANSI = ESCAPE + "91m"
export const BRIGHT_BLUE_ANSI = ESCAPE + "94m"
export const RESET_STYLE = ESCAPE + "0m"


export const color = (color: string, str: string): string => {
  return color + str + RESET_STYLE
}

const ERASE_FROM_CURSOR_THROUGH_END = ESCAPE + "0K"
const ERASE_FROM_BEGINNING_THROUGH_CURSOR = ESCAPE + "1K"
const ERASE_LINE = ESCAPE + "2K"

const CURSOR_FORWARD = ESCAPE + "C"
const CURSOR_BACK = ESCAPE + "D"

const cursorForward = (n: number): string => {
  let s = ""
  for(let i = 0; i < n; i++){
    s += CURSOR_FORWARD
  }
  return s
}

const cursorBack = (n: number): string => {
  let s = ""
  for(let i = 0; i < n; i++){
    s += CURSOR_BACK
  }
  return s
}

/** 
 * Web Console
 */
export class VNetConsole {

  /**
   * xterm instance
   */
  private term: Terminal

  /**
   * virtual network instance
   */
  private vnet: VNet

  /**
   * remote client instance
   */
  private remoteClient: RemoteClient

  /**
   * Pre command
   * @param command {string} - command
   * @returns string
   */
  private preCommand: (command: string) => string = (command: string) => {return command}

  /**
   * introduction message
   */
  introduction: string = color(BRIGHT_BLUE_ANSI ," Wellcome! This is Web CLI like Mininet CLI. ")

  /**
   * console prompt
   */
  prompt = 'mininet> '

  /**
   * console buffer
   */
  buffer = ""

  /**
   * command history
   */
  history: string[] = []


  constructor(vnet?: VNet) {
    this.vnet = vnet ?? changeableVNet
    this.remoteClient = this.vnet.getRemoteClient()

    this.term = new Terminal({
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
  }

  /**
   * Console start
   * @param elementId (string) - mount element
   */
  start(elementId: string) {
    // setup xterm
    const fitAddon = new FitAddon()
    this.term.loadAddon(fitAddon)
    this.term.open(document.getElementById(elementId) as HTMLElement)
    fitAddon.fit()

    // write introduction
    this.write(this.introduction)

    // set Event
    this.term.onKey(e => {
      this.onKey(e)
    })

    // enable copy and paste
    this.term.attachCustomKeyEventHandler((key: KeyboardEvent) => {
      if (key.code === 'KeyC' || key.code === 'KeyV') {
        if (key.ctrlKey) {
          return false
        }
      }
      return true
    })
  }

  /**
   * Write Prompt
   */
  writePrompt() {
    this.term.writeln('')
    this.term.write(this.prompt)
  }

  /**
   * write
   * @param s {string} - written string
   */
  write(s: string){
    this.term.write(s)
  }

  /**
   * writeln
   * @param s {string} - written string
   */
  writeln(s: string){
    this.term.writeln(s)
  }

  /**
   * write error
   * @param s {string} - written string
   */
  writeError(s: string){
    this.term.write(color(BRIGHT_RED_ANSI, "ERROR: " + s))
  }


  /**
   * onKey Event Handler
   * @param e 
   */
  private onKey(e: any){
    const ev = e.domEvent
    const printable = !(ev.altKey || ev.altGraphKey || ev.ctrlKey || ev.metaKey)

    // eslint-disable-next-line
    // @ts-ignore
    let cursorX: number = this.term._core.buffer.x

    // note: ev.key causes Parsing Error
    if (ev.keyCode === 8){  // backspace
      if(cursorX > prompt.length){
        const lengthFromCursor = this.prompt.length + this.buffer.length - cursorX
        const beforeCursorX = cursorX
        this.write(cursorBack(1))
        this.write(ERASE_FROM_CURSOR_THROUGH_END)
        this.write(this.buffer.slice(beforeCursorX - this.prompt.length))
        this.write(cursorBack(lengthFromCursor))
        this.buffer = this.buffer = this.buffer.slice(0, beforeCursorX - this.prompt.length - 1) + this.buffer.slice(beforeCursorX - this.prompt.length)
      }
    }else if(printable){
      switch (ev.key){
        case "Enter":
          // exec command
          if(this.buffer !== ""){
              this.term.writeln('')
              this.history.push(this.buffer)
              this.commandHandler(this.buffer)
              this.buffer = ""
          }
          break
        case "Tab":
          console.log("tab")
          break
        case "ArrowDown":
          // this.write(e.key)
          break
        case "ArrowLeft":
          if(cursorX > this.prompt.length){
            this.write(e.key)
          }
          break
        case "ArrowRight":
          if(cursorX < this.prompt.length + this.prompt.length){
            this.write(e.key)
          }
          break
        case "ArrowUp":
          // this.write(e.key)
          break
        default:  // print key
          if(cursorX >= this.prompt.length + this.buffer.length) {
            this.write(e.key)
            this.buffer += e.key
          }else{
            const lengthFromCursor = this.prompt.length + this.buffer.length - cursorX
            this.write(ERASE_FROM_CURSOR_THROUGH_END)
            this.write(e.key + this.buffer.slice(cursorX - this.prompt.length))
            this.write(cursorBack(lengthFromCursor))
            this.buffer = this.buffer.slice(0, cursorX - this.prompt.length) + e.key + this.buffer.slice(cursorX - this.prompt.length)
          }
          break
      }
    }
  }

  /**
   * command handler
   * @param command {string} - command
   */
  private commandHandler(command: string){
    /**
     * output command handler for remote client
     */
    const commandResultHandler = (command: CommandResult) => {
      const str = command.getResult()
      if(command.getType() === CommandResultType.OUTPUT){
        this.write(str)
      }else if(command.getType() === CommandResultType.ERROR){
        this.writeError(str)
      }else if(command.getType() === CommandResultType.END_SIGNAL){
        this.writePrompt()
      }
    }

    command = this.preCommand(command)

    if(command){
      // set command handler
      this.remoteClient.execMininetCommand(command, commandResultHandler)
    }else{
      this.writePrompt()
    }
  }

  /**
   * set precommand function
   * @param p 
   */
  setPreCommand(p: (command: string) => string) {
    this.preCommand = p
  }
}

export const netConsole = new VNetConsole()
