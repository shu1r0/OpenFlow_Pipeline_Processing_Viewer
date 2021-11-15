import { io, Socket } from 'socket.io-client';

import { DEVICE_TYPE } from '@/vnet/devices';
import { proto } from './net'
import { packetTracesRepository } from '../utils/packet_traces_repository'

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
  abstract addDevice(type: DEVICE_TYPE, name: string): void

  /**
   * add host to mininet
   * @param name : host name
   * @param ip : host ip address
   * @param mac : host mac address
   */
  abstract addHost(name: string, ip?: string, mac?: string): void

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
  abstract addSwitch(name: string, datapath_id: string): void

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
  abstract addLink(link: string, node1: string, node2: string): void

  /**
   * remove link
   * @param link : link name
   */
  abstract removeLink(link: string): void

  /**
   * execute mininet command
   * @param command : executed command
   */
  abstract execMininetCommand(command: string, commandHandler: (command: proto.CommandResult) => void): void

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

  addDevice(type: DEVICE_TYPE, name: string): void{
    console.log("add Device")
  }

  addHost(name: string, ip?: string, mac?: string): void {
    console.log("add host!!")
  }
  removeHost(name: string): void {
    console.log("remove host!!")
  }
  addSwitch(name: string, datapath_id: string): void {
    console.log("add switch!!")
  }
  removeSwitch(name: string): void {
    console.log("remove switch!!")
  }

  addLink(link: string, node1: string, node2: string): void {
    console.log("add link!!")
  }

  removeLink(link: string): void {
    console.log("remove link!!")
  }

  execMininetCommand(command: string, commandHandler: (command: proto.CommandResult) => void): void {
    console.log("exec mininet command")
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

  private execMininetCommandResultHandler: (command: proto.CommandResult) => void = null

  constructor(ip: string, port: string, namespace?: string){
    super(ip, port)
    this.namespace = namespace || ""
    this.socket = io('http://' + this.getIp() + ":" + this.getPort() + "/" + this.namespace)
    this.setupEvent()
  }

  setupEvent(){
    this.socket.on("connect", () => {
      console.log("connect!!")
    })
    
    this.socket.on("disconnect", () => {
      console.log("disconnect!!")
    })

    this.socket.on('get_trace', (data) => {
      const getTraceResult =  proto.GetTraceResult.deserialize(data)
      const packetTraces = getTraceResult.packet_traces
      console.log("receive packet trace")
      console.log(packetTraces)
      packetTracesRepository.extend(packetTraces)
    })

    this.socket.on('exec_mininet_command_result', (data) => {
      console.log("receive mininet command result")
      console.log(data)
      const result = proto.CommandResult.deserialize(data)
      this.execMininetCommandResultHandler(result)
    })
  }

  /**
   * connect to server
   */
  connect(){
    this.socket.connect()
  }
  
  /**
   * emit to server
   * @param event : event name
   * @param data : sent data
   */
  emit(event: string, data: any){
    console.log("try to emit event=" + event + " data=" + data)
    this.socket.emit(event, data)
  }

  /**
   * start tracing request
   */
  startTracing(all=true){
    const req = new proto.StartTracingRequest()
    req.option = 1
    this.emit('start_tracing', req.serialize())
  }

  /**
   * stop tracing request
   */
  stopTracing(){
    const req = new proto.StopTracingRequest()
    req.option = 1
    this.emit('stop_tracing', req.serialize())
  }

  addDevice(type: DEVICE_TYPE, name: string): void {
    if(type === DEVICE_TYPE.OFSWITCH){
      this.addSwitch(name)
    }else if(type === DEVICE_TYPE.HOST){
      this.addHost(name)
    }
  }

  addHost(name: string, ip?: string, mac?: string): void {
    const host = new proto.Host()
    host.name = name
    host.ip = ip
    host.mac = mac
    this.emit('add_host', host.serialize())
  }

  removeHost(name: string): void {
    const host = new proto.Host()
    host.name = name
    this.emit('remove_host', host.serialize())
  }

  addSwitch(name: string, datapath_id?: string): void {
    const sw = new proto.Switch()
    sw.name = name
    sw.datapath_id = datapath_id
    this.emit('add_switch', sw.serialize())
  }

  removeSwitch(name: string): void {
    const sw = new proto.Switch()
    sw.name = name
    this.emit('remove_switch', sw.serialize())
  }

  addLink(link: string, node1: string, node2: string): void {
    const l = new proto.Link()
    l.name = link
    l.host1 = node1
    l.host2 = node2
    this.emit('add_link', l.serialize())
  }

  removeLink(link: string): void {
    const l = new proto.Link()
    l.name = link
    this.emit('remove_link', l.serialize())
  }

  execMininetCommand(command: string, commandHandler: (command: proto.CommandResult) => void): void{
    this.execMininetCommandResultHandler = commandHandler
    const c = new proto.MininetCommand()
    c.command = command
    this.emit('exec_mininet_command', c.serialize())
  }

  getTrace() {
    const r = new proto.GetTraceRequest()
    r.option = 0
    this.emit('get_trace', r.serialize())
  }
  
}
