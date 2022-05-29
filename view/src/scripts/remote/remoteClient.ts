import { io, Socket } from 'socket.io-client';

import * as devices from '@/scripts/vnet/devices';

import { packetTracesRepository } from '../utils/packet_traces_repository'
import { topologyRepository } from '../utils/topology_repository'
import { CommandResult, CommandResultType, GetTraceRequest, GetTraceResult, Host, Link, MininetCommand, StartTracingRequest, StopTracingRequest, Switch } from './net_pb';

/**
 * A client connect to the server.
 */
export abstract class RemoteClient{

  /**
   * server ip address
   */
  private ip: string

  /**
   * server port number
   */
  private port: string

  constructor(ip: string, port: string){
    this.ip = ip
    this.port = port
  }

  /**
   * connect to server
   */
  abstract connect(): void

  /**
   * start tracing
   */
  abstract startTracing(): void

  /**
   * stop tracing
   */
  abstract stopTracing(): void

  /**
   * add device
   * This is a more abstract method.
   * @param type : device type
   * @param name : device name
   */
  abstract addDevice(device: devices.Device): void

  /**
   * add host to mininet
   * @param name : host name
   * @param ip : host ip address
   * @param mac : host mac address
   */
  abstract addHost(host: devices.Host): void

  /**
   * remove host
   * @param name : host name
   */
  abstract removeHost(name: string): void

  /**
   * add openflow switch
   * @param name : switch name
   * @param datapath_id : switch datapath id
   */
  abstract addSwitch(ofswitch: devices.Switch): void

  /**
   * remove openflow switch
   * @param name : switch name
   */
  abstract removeSwitch(name: string): void

  /**
   * 
   * @param link : link name
   * @param node1 : node1
   * @param node2 : node2
   */
  abstract addLink(link: devices.Edge): void

  /**
   * remove link
   * @param link : link name
   */
  abstract removeLink(link: string): void

  /**
   * execute mininet command
   * @param command : executed command
   */
  abstract execMininetCommand(command: string, commandHandler: (command: CommandResult) => void): void

  /**
   * get packet trace request
   */
  abstract getTrace(): void

  /**
   * target ip address
   * @returns string
   */
  getIp(){
    return this.ip;
  }

  /**
   * target port number
   * @returns string
   */
  getPort(){
    return this.port
  }
}


/**
 * Debug client
 */
export class DummyRemoteClient extends RemoteClient{

  constructor(ip?: string, port?: string){
    super(ip ?? "127.0.0.1", port ?? "8080")
  }

  connect(){
    console.log("connect to server")
  }

  startTracing(){
    console.log("start tracing")
  }

  stopTracing(){
    console.log("stop tracing")
  }

  addDevice(device: devices.Device): void{
    console.log("add Device")
  }

  addHost(host: devices.Host): void {
    console.log("add host!!")
  }
  removeHost(name: string): void {
    console.log("remove host!!")
  }
  addSwitch(ofswitch: devices.Switch): void {
    console.log("add switch!!")
  }
  removeSwitch(name: string): void {
    console.log("remove switch!!")
  }

  addLink(link: devices.Edge): void {
    console.log("add link!!")
  }

  removeLink(link: string): void {
    console.log("remove link!!")
  }

  execMininetCommand(command: string, commandHandler: (command: CommandResult) => void): void {
    console.log("exec mininet command")
    const dummyResult = new CommandResult()
    dummyResult.setType(CommandResultType.OUTPUT)
    dummyResult.setResult("command result of " + command)
    console.log(dummyResult)
    commandHandler(dummyResult)
    const dummyResult2 = new CommandResult()
    dummyResult.setType(CommandResultType.END_SIGNAL)
    commandHandler(dummyResult2)
  }

  getTrace(): void{
    console.log("get trace")
  }

}


/**
 * WebSocket Client
 */
export class WSClient extends RemoteClient {

  /**
   * Socket
   */
  private socket: Socket;

  /**
   * Web Socket Namespace
   */
  private namespace = ""

  /**
   * handler for mininet command result
   */
  private execMininetCommandResultHandler: (command: CommandResult) => void = null

  constructor(ip: string, port: string, namespace?: string){
    super(ip, port)
    this.namespace = namespace || ""
    this.socket = io('http://' + this.getIp() + ":" + this.getPort() + "/" + this.namespace)
    this.setupEvent()
  }

  setupEvent(){
    /**
     * all event
     */
    this.socket.prependAny((event, ...args) => {
      console.log(`got ${event}`);
    })

    /**
     * connect event
     */
    this.socket.on("connect", () => {
      console.log("connect!!")
    })
    
    /**
     * disconnect event
     */
    this.socket.on("disconnect", () => {
      console.log("disconnect!!")
    })
    
    /**
     * get trace event
     */
    this.socket.on('get_trace', (data) => {
      const getTraceResult =  GetTraceResult.deserializeBinary(data)
      const packetTraces = getTraceResult.getPacketTracesList()
      console.log(packetTraces)
      packetTracesRepository.extend(packetTraces)
    })

    /**
     * exec mininet command result command
     */
    this.socket.on('exec_mininet_command_result', (data) => {
      const result = CommandResult.deserializeBinary(data)
      this.execMininetCommandResultHandler(result)
    })
  }

  /**
   * connect to server
   */
  connect(){
    console.log("try to connect")
    this.socket.connect()
  }
  
  /**
   * emit to server
   * @param event : event name
   * @param data : sent data
   */
  protected emit(event: string, data: any, callback?: (d: any)=>void){
    console.log("try to emit event=" + event + " data=" + data)
    this.socket.emit(event, data, (data: any) => {
      console.log(event + " response ")
      console.log(data)
      if(callback){
        callback(data)
      }
    })
  }

  /**
   * start tracing request
   */
  startTracing(all=true){
    const req = new StartTracingRequest()
    req.setOption(1)
    this.emit('start_tracing', req.serializeBinary())
  }

  /**
   * stop tracing request
   */
  stopTracing(){
    const req = new StopTracingRequest()
    req.setOption(1)
    this.emit('stop_tracing', req.serializeBinary())
  }

  addDevice(device: devices.Device): void {
    if(device instanceof devices.Switch){
      this.addSwitch(device)
    }else if(device instanceof devices.Host){
      this.addHost(device)
    }
  }

  addHost(host: devices.Host): void {
    const hostMsg = new Host()
    hostMsg.setName(host.getName())
    hostMsg.setIp(host.getIp())
    hostMsg.setMac(host.getMac())
    this.emit('add_host', hostMsg.serializeBinary(), (data) => {
      const ackHost = Host.deserializeBinary(data)
      console.log(ackHost)
      // add repository
      topologyRepository.addNode(ackHost)
    })
  }

  removeHost(name: string): void {
    const host = new Host()
    host.setName(name)
    this.emit('remove_host', host.serializeBinary())
  }

  addSwitch(ofswitch: devices.Switch): void {
    const sw = new Switch()
    sw.setName(ofswitch.getId())
    sw.setDatapathId(ofswitch.getDpid())
    this.emit('add_switch', sw.serializeBinary(), (data) => {
      const ackSwitch = Switch.deserializeBinary(data)
      console.log(ackSwitch)
      // add repository
      topologyRepository.addNode(ackSwitch)
    })
  }

  removeSwitch(name: string): void {
    const sw = new Switch()
    sw.setName(name)
    this.emit('remove_switch', sw.serializeBinary())
  }

  addLink(link: devices.Edge): void {
    const l = new Link()
    l.setName(link.getId())
    l.setHost1(link.getNode1())
    l.setHost2(link.getNode2())
    this.emit('add_link', l.serializeBinary(), (data) => {
      const ackLink = Link.deserializeBinary(data)
      console.log(ackLink)
      // add repository
      topologyRepository.addLink(ackLink)
    })
  }

  removeLink(link: string): void {
    const l = new Link()
    l.setName(link)
    this.emit('remove_link', l.serializeBinary())
  }

  /**
   * exec mininet command
   * @param command : sent command
   * @param commandHandler : command result handler
   */
  execMininetCommand(command: string, commandHandler: (command: CommandResult) => void): void{
    this.execMininetCommandResultHandler = commandHandler
    const c = new MininetCommand()
    c.setCommand(command)
    this.emit('exec_mininet_command', c.serializeBinary())
  }

  getTrace() {
    const r = new GetTraceRequest()
    r.setOption(0)
    this.emit('get_trace', r.serializeBinary())
  }
  
}
