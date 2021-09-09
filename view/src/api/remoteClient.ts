import { TracerNetServiceClient } from "./tracer_net_grpc_web_pb";
import { Link, Node, NodeType, Result } from '../api/tracer_net_pb';

import { DEVICE_TYPE } from '@/vnet/devices';

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

  abstract addLink(link: string, edge1: string, edge2: string): void

  abstract removeLink(link: string): void

  getIp(){
    return this.ip;
  }

  getPort(){
    return this.port
  }
}


export class DummyRemoteClient extends RemoteClient{

  constructor(ip: string, port: string){
    super(ip, port)
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

  addLink(link: string, edge1: string, edge2: string): void {
    console.log("add link!!")
  }

  removeLink(link: string): void {
    console.log("remove link!!")
  }

}