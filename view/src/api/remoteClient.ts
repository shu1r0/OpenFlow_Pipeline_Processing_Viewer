import { TracerNetServiceClient } from "./tracer_net_grpc_web_pb";
import { Link, Node, NodeType, Result } from '../api/tracer_net_pb';

import { DEVICE_TYPE } from '@/vnet/devices';

export abstract class RemoteClient{
  private ip: string
  private port: string

  constructor(ip: string, port: string){
    this.ip = ip
    this.port = port
  }

  abstract addDevice(type: DEVICE_TYPE, device_id: string): void

  abstract removeDevce(type: DEVICE_TYPE, device_id: string): void

  abstract addLink(link: string, edge1: string, edge2: string): void

  abstract removeLink(link: string): void

  createNodeMessage(type: DEVICE_TYPE, device_id: string): Node{
    const nodeMsg = new Node()
    if(type === DEVICE_TYPE.OFSWITCH){
      nodeMsg.setNodeType(NodeType.SWITCH)
    }else if(type === DEVICE_TYPE.HOST){
      nodeMsg.setNodeType(NodeType.HOST)
    }
    nodeMsg.setName(device_id)
    return nodeMsg
  }

  createLinkMessage(link: string, edge1: string, edge2: string): Link{
    const linkMsg = new Link()
    linkMsg.setName(link)
    linkMsg.setHostName1(edge1)
    linkMsg.setHostName2(edge2)
    return linkMsg
  }

  getIp(){
    return this.ip;
  }

  getPort(){
    return this.port
  }
}

// export class RESTRemoteClient extends RemoteClient{
//   constructor(ip: string, port: string){
//     super(ip, port)
//   }

//   addDevice(type: DEVICE_TYPE, device_id: string): void{
    
//   }
// }

// export class gRPCRemoteClient extends RemoteClient{
//   private grpc_client: TracerNetServiceClient

//   constructor(ip: string, port: string){
//     super(ip, port)
//     this.grpc_client = new TracerNetServiceClient('http://' + this.getIp() + ':' + this.getPort())
//   }

//   addDevice(type: DEVICE_TYPE, device_id: string){
//     const nodeReq = this.createNodeMessage(type, device_id)

//     this.grpc_client.addNode(nodeReq, {}, (err: any, response: Result)=>{
//       console.log(err)
//       const status = response.getStatus()
//       console.log("status from grpc server is " + status)
//     })
//   }
// }


export class DummyRemoteClient extends RemoteClient{
  constructor(ip: string, port: string){
    super(ip, port)
  }


  addDevice(type: DEVICE_TYPE, device_id: string): void {
    // pass
  }
  removeDevce(type: DEVICE_TYPE, device_id: string): void {
    // pass
  }
  addLink(link: string, edge1: string, edge2: string): void {
    // pass
  }
  removeLink(link: string): void {
    // pass
  }

}