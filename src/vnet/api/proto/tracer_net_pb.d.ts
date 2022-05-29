import * as jspb from 'google-protobuf'



export class Node extends jspb.Message {
  getNodeType(): NodeType;
  setNodeType(value: NodeType): Node;

  getName(): string;
  setName(value: string): Node;

  getNodeTypeCase(): Node.NodeTypeCase;

  getNameCase(): Node.NameCase;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): Node.AsObject;
  static toObject(includeInstance: boolean, msg: Node): Node.AsObject;
  static serializeBinaryToWriter(message: Node, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): Node;
  static deserializeBinaryFromReader(message: Node, reader: jspb.BinaryReader): Node;
}

export namespace Node {
  export type AsObject = {
    nodeType: NodeType,
    name: string,
  }

  export enum NodeTypeCase { 
    _NODE_TYPE_NOT_SET = 0,
    NODE_TYPE = 1,
  }

  export enum NameCase { 
    _NAME_NOT_SET = 0,
    NAME = 2,
  }
}

export class Link extends jspb.Message {
  getName(): string;
  setName(value: string): Link;

  getHostName1(): string;
  setHostName1(value: string): Link;

  getHostName2(): string;
  setHostName2(value: string): Link;

  getNameCase(): Link.NameCase;

  getHostName1Case(): Link.HostName1Case;

  getHostName2Case(): Link.HostName2Case;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): Link.AsObject;
  static toObject(includeInstance: boolean, msg: Link): Link.AsObject;
  static serializeBinaryToWriter(message: Link, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): Link;
  static deserializeBinaryFromReader(message: Link, reader: jspb.BinaryReader): Link;
}

export namespace Link {
  export type AsObject = {
    name: string,
    hostName1: string,
    hostName2: string,
  }

  export enum NameCase { 
    _NAME_NOT_SET = 0,
    NAME = 1,
  }

  export enum HostName1Case { 
    _HOST_NAME1_NOT_SET = 0,
    HOST_NAME1 = 2,
  }

  export enum HostName2Case { 
    _HOST_NAME2_NOT_SET = 0,
    HOST_NAME2 = 3,
  }
}

export class Result extends jspb.Message {
  getStatus(): number;
  setStatus(value: number): Result;

  getStatusCase(): Result.StatusCase;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): Result.AsObject;
  static toObject(includeInstance: boolean, msg: Result): Result.AsObject;
  static serializeBinaryToWriter(message: Result, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): Result;
  static deserializeBinaryFromReader(message: Result, reader: jspb.BinaryReader): Result;
}

export namespace Result {
  export type AsObject = {
    status: number,
  }

  export enum StatusCase { 
    _STATUS_NOT_SET = 0,
    STATUS = 1,
  }
}

export enum NodeType { 
  HOST = 0,
  SWITCH = 1,
}
