// package: proto
// file: net.proto

import * as jspb from "google-protobuf";

export class Host extends jspb.Message {
  hasName(): boolean;
  clearName(): void;
  getName(): string;
  setName(value: string): void;

  hasIp(): boolean;
  clearIp(): void;
  getIp(): string;
  setIp(value: string): void;

  hasMac(): boolean;
  clearMac(): void;
  getMac(): string;
  setMac(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): Host.AsObject;
  static toObject(includeInstance: boolean, msg: Host): Host.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: Host, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): Host;
  static deserializeBinaryFromReader(message: Host, reader: jspb.BinaryReader): Host;
}

export namespace Host {
  export type AsObject = {
    name: string,
    ip: string,
    mac: string,
  }
}

export class Switch extends jspb.Message {
  hasName(): boolean;
  clearName(): void;
  getName(): string;
  setName(value: string): void;

  hasDatapathId(): boolean;
  clearDatapathId(): void;
  getDatapathId(): string;
  setDatapathId(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): Switch.AsObject;
  static toObject(includeInstance: boolean, msg: Switch): Switch.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: Switch, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): Switch;
  static deserializeBinaryFromReader(message: Switch, reader: jspb.BinaryReader): Switch;
}

export namespace Switch {
  export type AsObject = {
    name: string,
    datapathId: string,
  }
}

export class Link extends jspb.Message {
  hasName(): boolean;
  clearName(): void;
  getName(): string;
  setName(value: string): void;

  hasHost1(): boolean;
  clearHost1(): void;
  getHost1(): string;
  setHost1(value: string): void;

  hasHost2(): boolean;
  clearHost2(): void;
  getHost2(): string;
  setHost2(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): Link.AsObject;
  static toObject(includeInstance: boolean, msg: Link): Link.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: Link, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): Link;
  static deserializeBinaryFromReader(message: Link, reader: jspb.BinaryReader): Link;
}

export namespace Link {
  export type AsObject = {
    name: string,
    host1: string,
    host2: string,
  }
}

export class RemoteController extends jspb.Message {
  getControllerIp(): string;
  setControllerIp(value: string): void;

  getControllerPort(): number;
  setControllerPort(value: number): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): RemoteController.AsObject;
  static toObject(includeInstance: boolean, msg: RemoteController): RemoteController.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: RemoteController, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): RemoteController;
  static deserializeBinaryFromReader(message: RemoteController, reader: jspb.BinaryReader): RemoteController;
}

export namespace RemoteController {
  export type AsObject = {
    controllerIp: string,
    controllerPort: number,
  }
}

export class Packet extends jspb.Message {
  getTimestamp(): number;
  setTimestamp(value: number): void;

  getInPort(): string;
  setInPort(value: string): void;

  getInPhyPort(): string;
  setInPhyPort(value: string): void;

  getFieldsMap(): jspb.Map<string, string>;
  clearFieldsMap(): void;
  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): Packet.AsObject;
  static toObject(includeInstance: boolean, msg: Packet): Packet.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: Packet, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): Packet;
  static deserializeBinaryFromReader(message: Packet, reader: jspb.BinaryReader): Packet;
}

export namespace Packet {
  export type AsObject = {
    timestamp: number,
    inPort: string,
    inPhyPort: string,
    fieldsMap: Array<[string, string]>,
  }
}

export class Action extends jspb.Message {
  hasStr(): boolean;
  clearStr(): void;
  getStr(): string;
  setStr(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): Action.AsObject;
  static toObject(includeInstance: boolean, msg: Action): Action.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: Action, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): Action;
  static deserializeBinaryFromReader(message: Action, reader: jspb.BinaryReader): Action;
}

export namespace Action {
  export type AsObject = {
    str: string,
  }
}

export class ActionSet extends jspb.Message {
  clearActionsList(): void;
  getActionsList(): Array<Action>;
  setActionsList(value: Array<Action>): void;
  addActions(value?: Action, index?: number): Action;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): ActionSet.AsObject;
  static toObject(includeInstance: boolean, msg: ActionSet): ActionSet.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: ActionSet, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): ActionSet;
  static deserializeBinaryFromReader(message: ActionSet, reader: jspb.BinaryReader): ActionSet;
}

export namespace ActionSet {
  export type AsObject = {
    actionsList: Array<Action.AsObject>,
  }
}

export class Instruction extends jspb.Message {
  hasType(): boolean;
  clearType(): void;
  getType(): InstructionTypeMap[keyof InstructionTypeMap];
  setType(value: InstructionTypeMap[keyof InstructionTypeMap]): void;

  hasGotoTable(): boolean;
  clearGotoTable(): void;
  getGotoTable(): InstructionGotoTable | undefined;
  setGotoTable(value?: InstructionGotoTable): void;

  hasWriteMetadata(): boolean;
  clearWriteMetadata(): void;
  getWriteMetadata(): InstructionWriteMetadata | undefined;
  setWriteMetadata(value?: InstructionWriteMetadata): void;

  hasActions(): boolean;
  clearActions(): void;
  getActions(): InstructionActions | undefined;
  setActions(value?: InstructionActions): void;

  hasMeter(): boolean;
  clearMeter(): void;
  getMeter(): InstructionMeter | undefined;
  setMeter(value?: InstructionMeter): void;

  getDataCase(): Instruction.DataCase;
  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): Instruction.AsObject;
  static toObject(includeInstance: boolean, msg: Instruction): Instruction.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: Instruction, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): Instruction;
  static deserializeBinaryFromReader(message: Instruction, reader: jspb.BinaryReader): Instruction;
}

export namespace Instruction {
  export type AsObject = {
    type: InstructionTypeMap[keyof InstructionTypeMap],
    gotoTable?: InstructionGotoTable.AsObject,
    writeMetadata?: InstructionWriteMetadata.AsObject,
    actions?: InstructionActions.AsObject,
    meter?: InstructionMeter.AsObject,
  }

  export enum DataCase {
    DATA_NOT_SET = 0,
    GOTO_TABLE = 2,
    WRITE_METADATA = 3,
    ACTIONS = 4,
    METER = 5,
  }
}

export class InstructionGotoTable extends jspb.Message {
  getTableId(): number;
  setTableId(value: number): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): InstructionGotoTable.AsObject;
  static toObject(includeInstance: boolean, msg: InstructionGotoTable): InstructionGotoTable.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: InstructionGotoTable, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): InstructionGotoTable;
  static deserializeBinaryFromReader(message: InstructionGotoTable, reader: jspb.BinaryReader): InstructionGotoTable;
}

export namespace InstructionGotoTable {
  export type AsObject = {
    tableId: number,
  }
}

export class InstructionWriteMetadata extends jspb.Message {
  getMetadata(): number;
  setMetadata(value: number): void;

  getMetadataMask(): number;
  setMetadataMask(value: number): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): InstructionWriteMetadata.AsObject;
  static toObject(includeInstance: boolean, msg: InstructionWriteMetadata): InstructionWriteMetadata.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: InstructionWriteMetadata, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): InstructionWriteMetadata;
  static deserializeBinaryFromReader(message: InstructionWriteMetadata, reader: jspb.BinaryReader): InstructionWriteMetadata;
}

export namespace InstructionWriteMetadata {
  export type AsObject = {
    metadata: number,
    metadataMask: number,
  }
}

export class InstructionActions extends jspb.Message {
  clearActionsList(): void;
  getActionsList(): Array<Action>;
  setActionsList(value: Array<Action>): void;
  addActions(value?: Action, index?: number): Action;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): InstructionActions.AsObject;
  static toObject(includeInstance: boolean, msg: InstructionActions): InstructionActions.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: InstructionActions, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): InstructionActions;
  static deserializeBinaryFromReader(message: InstructionActions, reader: jspb.BinaryReader): InstructionActions;
}

export namespace InstructionActions {
  export type AsObject = {
    actionsList: Array<Action.AsObject>,
  }
}

export class InstructionMeter extends jspb.Message {
  getMeterId(): number;
  setMeterId(value: number): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): InstructionMeter.AsObject;
  static toObject(includeInstance: boolean, msg: InstructionMeter): InstructionMeter.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: InstructionMeter, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): InstructionMeter;
  static deserializeBinaryFromReader(message: InstructionMeter, reader: jspb.BinaryReader): InstructionMeter;
}

export namespace InstructionMeter {
  export type AsObject = {
    meterId: number,
  }
}

export class Match extends jspb.Message {
  hasFieldName(): boolean;
  clearFieldName(): void;
  getFieldName(): string;
  setFieldName(value: string): void;

  hasValue(): boolean;
  clearValue(): void;
  getValue(): string;
  setValue(value: string): void;

  hasMask(): boolean;
  clearMask(): void;
  getMask(): string;
  setMask(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): Match.AsObject;
  static toObject(includeInstance: boolean, msg: Match): Match.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: Match, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): Match;
  static deserializeBinaryFromReader(message: Match, reader: jspb.BinaryReader): Match;
}

export namespace Match {
  export type AsObject = {
    fieldName: string,
    value: string,
    mask: string,
  }
}

export class Flow extends jspb.Message {
  hasCookie(): boolean;
  clearCookie(): void;
  getCookie(): string;
  setCookie(value: string): void;

  hasDuration(): boolean;
  clearDuration(): void;
  getDuration(): number;
  setDuration(value: number): void;

  hasTable(): boolean;
  clearTable(): void;
  getTable(): number;
  setTable(value: number): void;

  hasNPackets(): boolean;
  clearNPackets(): void;
  getNPackets(): number;
  setNPackets(value: number): void;

  hasNBytes(): boolean;
  clearNBytes(): void;
  getNBytes(): number;
  setNBytes(value: number): void;

  hasPriority(): boolean;
  clearPriority(): void;
  getPriority(): number;
  setPriority(value: number): void;

  clearMatchList(): void;
  getMatchList(): Array<Match>;
  setMatchList(value: Array<Match>): void;
  addMatch(value?: Match, index?: number): Match;

  clearActionsList(): void;
  getActionsList(): Array<Instruction>;
  setActionsList(value: Array<Instruction>): void;
  addActions(value?: Instruction, index?: number): Instruction;

  hasFlowId(): boolean;
  clearFlowId(): void;
  getFlowId(): number;
  setFlowId(value: number): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): Flow.AsObject;
  static toObject(includeInstance: boolean, msg: Flow): Flow.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: Flow, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): Flow;
  static deserializeBinaryFromReader(message: Flow, reader: jspb.BinaryReader): Flow;
}

export namespace Flow {
  export type AsObject = {
    cookie: string,
    duration: number,
    table: number,
    nPackets: number,
    nBytes: number,
    priority: number,
    matchList: Array<Match.AsObject>,
    actionsList: Array<Instruction.AsObject>,
    flowId: number,
  }
}

export class FlowTable extends jspb.Message {
  clearFlowsList(): void;
  getFlowsList(): Array<Flow>;
  setFlowsList(value: Array<Flow>): void;
  addFlows(value?: Flow, index?: number): Flow;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): FlowTable.AsObject;
  static toObject(includeInstance: boolean, msg: FlowTable): FlowTable.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: FlowTable, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): FlowTable;
  static deserializeBinaryFromReader(message: FlowTable, reader: jspb.BinaryReader): FlowTable;
}

export namespace FlowTable {
  export type AsObject = {
    flowsList: Array<Flow.AsObject>,
  }
}

export class PacketProcessing extends jspb.Message {
  hasSwitch(): boolean;
  clearSwitch(): void;
  getSwitch(): string;
  setSwitch(value: string): void;

  hasFlowTable(): boolean;
  clearFlowTable(): void;
  getFlowTable(): FlowTable | undefined;
  setFlowTable(value?: FlowTable): void;

  hasActionSet(): boolean;
  clearActionSet(): void;
  getActionSet(): ActionSet | undefined;
  setActionSet(value?: ActionSet): void;

  clearPktsList(): void;
  getPktsList(): Array<Packet>;
  setPktsList(value: Array<Packet>): void;
  addPkts(value?: Packet, index?: number): Packet;

  clearMatchedFlowsList(): void;
  getMatchedFlowsList(): Array<number>;
  setMatchedFlowsList(value: Array<number>): void;
  addMatchedFlows(value: number, index?: number): number;

  hasPacketAfterActionSet(): boolean;
  clearPacketAfterActionSet(): void;
  getPacketAfterActionSet(): Packet | undefined;
  setPacketAfterActionSet(value?: Packet): void;

  getOutsMap(): jspb.Map<string, Packet>;
  clearOutsMap(): void;
  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): PacketProcessing.AsObject;
  static toObject(includeInstance: boolean, msg: PacketProcessing): PacketProcessing.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: PacketProcessing, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): PacketProcessing;
  static deserializeBinaryFromReader(message: PacketProcessing, reader: jspb.BinaryReader): PacketProcessing;
}

export namespace PacketProcessing {
  export type AsObject = {
    pb_switch: string,
    flowTable?: FlowTable.AsObject,
    actionSet?: ActionSet.AsObject,
    pktsList: Array<Packet.AsObject>,
    matchedFlowsList: Array<number>,
    packetAfterActionSet?: Packet.AsObject,
    outsMap: Array<[string, Packet.AsObject]>,
  }
}

export class PacketArc extends jspb.Message {
  hasSrc(): boolean;
  clearSrc(): void;
  getSrc(): string;
  setSrc(value: string): void;

  hasPkt(): boolean;
  clearPkt(): void;
  getPkt(): Packet | undefined;
  setPkt(value?: Packet): void;

  hasPacketProcessing(): boolean;
  clearPacketProcessing(): void;
  getPacketProcessing(): PacketProcessing | undefined;
  setPacketProcessing(value?: PacketProcessing): void;

  hasEdge(): boolean;
  clearEdge(): void;
  getEdge(): string;
  setEdge(value: string): void;

  hasDst(): boolean;
  clearDst(): void;
  getDst(): string;
  setDst(value: string): void;

  hasDstInterface(): boolean;
  clearDstInterface(): void;
  getDstInterface(): string;
  setDstInterface(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): PacketArc.AsObject;
  static toObject(includeInstance: boolean, msg: PacketArc): PacketArc.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: PacketArc, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): PacketArc;
  static deserializeBinaryFromReader(message: PacketArc, reader: jspb.BinaryReader): PacketArc;
}

export namespace PacketArc {
  export type AsObject = {
    src: string,
    pkt?: Packet.AsObject,
    packetProcessing?: PacketProcessing.AsObject,
    edge: string,
    dst: string,
    dstInterface: string,
  }
}

export class PacketTrace extends jspb.Message {
  getTimestamp(): number;
  setTimestamp(value: number): void;

  clearArcsList(): void;
  getArcsList(): Array<PacketArc>;
  setArcsList(value: Array<PacketArc>): void;
  addArcs(value?: PacketArc, index?: number): PacketArc;

  hasProtocol(): boolean;
  clearProtocol(): void;
  getProtocol(): string;
  setProtocol(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): PacketTrace.AsObject;
  static toObject(includeInstance: boolean, msg: PacketTrace): PacketTrace.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: PacketTrace, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): PacketTrace;
  static deserializeBinaryFromReader(message: PacketTrace, reader: jspb.BinaryReader): PacketTrace;
}

export namespace PacketTrace {
  export type AsObject = {
    timestamp: number,
    arcsList: Array<PacketArc.AsObject>,
    protocol: string,
  }
}

export class ChangeTopologyRequest extends jspb.Message {
  clearSwitchesList(): void;
  getSwitchesList(): Array<Switch>;
  setSwitchesList(value: Array<Switch>): void;
  addSwitches(value?: Switch, index?: number): Switch;

  clearHostsList(): void;
  getHostsList(): Array<Host>;
  setHostsList(value: Array<Host>): void;
  addHosts(value?: Host, index?: number): Host;

  clearLinksList(): void;
  getLinksList(): Array<Link>;
  setLinksList(value: Array<Link>): void;
  addLinks(value?: Link, index?: number): Link;

  hasController(): boolean;
  clearController(): void;
  getController(): RemoteController | undefined;
  setController(value?: RemoteController): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): ChangeTopologyRequest.AsObject;
  static toObject(includeInstance: boolean, msg: ChangeTopologyRequest): ChangeTopologyRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: ChangeTopologyRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): ChangeTopologyRequest;
  static deserializeBinaryFromReader(message: ChangeTopologyRequest, reader: jspb.BinaryReader): ChangeTopologyRequest;
}

export namespace ChangeTopologyRequest {
  export type AsObject = {
    switchesList: Array<Switch.AsObject>,
    hostsList: Array<Host.AsObject>,
    linksList: Array<Link.AsObject>,
    controller?: RemoteController.AsObject,
  }
}

export class GetFeaturesRequest extends jspb.Message {
  clearSwitchesList(): void;
  getSwitchesList(): Array<Switch>;
  setSwitchesList(value: Array<Switch>): void;
  addSwitches(value?: Switch, index?: number): Switch;

  clearHostsList(): void;
  getHostsList(): Array<Host>;
  setHostsList(value: Array<Host>): void;
  addHosts(value?: Host, index?: number): Host;

  clearLinksList(): void;
  getLinksList(): Array<Link>;
  setLinksList(value: Array<Link>): void;
  addLinks(value?: Link, index?: number): Link;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): GetFeaturesRequest.AsObject;
  static toObject(includeInstance: boolean, msg: GetFeaturesRequest): GetFeaturesRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: GetFeaturesRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): GetFeaturesRequest;
  static deserializeBinaryFromReader(message: GetFeaturesRequest, reader: jspb.BinaryReader): GetFeaturesRequest;
}

export namespace GetFeaturesRequest {
  export type AsObject = {
    switchesList: Array<Switch.AsObject>,
    hostsList: Array<Host.AsObject>,
    linksList: Array<Link.AsObject>,
  }
}

export class StartNetworkRequest extends jspb.Message {
  getOption(): StartNetworkOptionMap[keyof StartNetworkOptionMap];
  setOption(value: StartNetworkOptionMap[keyof StartNetworkOptionMap]): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): StartNetworkRequest.AsObject;
  static toObject(includeInstance: boolean, msg: StartNetworkRequest): StartNetworkRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: StartNetworkRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): StartNetworkRequest;
  static deserializeBinaryFromReader(message: StartNetworkRequest, reader: jspb.BinaryReader): StartNetworkRequest;
}

export namespace StartNetworkRequest {
  export type AsObject = {
    option: StartNetworkOptionMap[keyof StartNetworkOptionMap],
  }
}

export class StartTracingRequest extends jspb.Message {
  hasOption(): boolean;
  clearOption(): void;
  getOption(): number;
  setOption(value: number): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): StartTracingRequest.AsObject;
  static toObject(includeInstance: boolean, msg: StartTracingRequest): StartTracingRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: StartTracingRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): StartTracingRequest;
  static deserializeBinaryFromReader(message: StartTracingRequest, reader: jspb.BinaryReader): StartTracingRequest;
}

export namespace StartTracingRequest {
  export type AsObject = {
    option: number,
  }
}

export class StopTracingRequest extends jspb.Message {
  hasOption(): boolean;
  clearOption(): void;
  getOption(): number;
  setOption(value: number): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): StopTracingRequest.AsObject;
  static toObject(includeInstance: boolean, msg: StopTracingRequest): StopTracingRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: StopTracingRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): StopTracingRequest;
  static deserializeBinaryFromReader(message: StopTracingRequest, reader: jspb.BinaryReader): StopTracingRequest;
}

export namespace StopTracingRequest {
  export type AsObject = {
    option: number,
  }
}

export class GetTraceRequest extends jspb.Message {
  hasOption(): boolean;
  clearOption(): void;
  getOption(): number;
  setOption(value: number): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): GetTraceRequest.AsObject;
  static toObject(includeInstance: boolean, msg: GetTraceRequest): GetTraceRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: GetTraceRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): GetTraceRequest;
  static deserializeBinaryFromReader(message: GetTraceRequest, reader: jspb.BinaryReader): GetTraceRequest;
}

export namespace GetTraceRequest {
  export type AsObject = {
    option: number,
  }
}

export class GetTraceResult extends jspb.Message {
  hasTracesLength(): boolean;
  clearTracesLength(): void;
  getTracesLength(): number;
  setTracesLength(value: number): void;

  clearPacketTracesList(): void;
  getPacketTracesList(): Array<PacketTrace>;
  setPacketTracesList(value: Array<PacketTrace>): void;
  addPacketTraces(value?: PacketTrace, index?: number): PacketTrace;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): GetTraceResult.AsObject;
  static toObject(includeInstance: boolean, msg: GetTraceResult): GetTraceResult.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: GetTraceResult, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): GetTraceResult;
  static deserializeBinaryFromReader(message: GetTraceResult, reader: jspb.BinaryReader): GetTraceResult;
}

export namespace GetTraceResult {
  export type AsObject = {
    tracesLength: number,
    packetTracesList: Array<PacketTrace.AsObject>,
  }
}

export class TopoChangeResult extends jspb.Message {
  hasStatus(): boolean;
  clearStatus(): void;
  getStatus(): number;
  setStatus(value: number): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): TopoChangeResult.AsObject;
  static toObject(includeInstance: boolean, msg: TopoChangeResult): TopoChangeResult.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: TopoChangeResult, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): TopoChangeResult;
  static deserializeBinaryFromReader(message: TopoChangeResult, reader: jspb.BinaryReader): TopoChangeResult;
}

export namespace TopoChangeResult {
  export type AsObject = {
    status: number,
  }
}

export class HostCommand extends jspb.Message {
  hasHost(): boolean;
  clearHost(): void;
  getHost(): string;
  setHost(value: string): void;

  hasCommand(): boolean;
  clearCommand(): void;
  getCommand(): string;
  setCommand(value: string): void;

  hasType(): boolean;
  clearType(): void;
  getType(): CommandResultTypeMap[keyof CommandResultTypeMap];
  setType(value: CommandResultTypeMap[keyof CommandResultTypeMap]): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): HostCommand.AsObject;
  static toObject(includeInstance: boolean, msg: HostCommand): HostCommand.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: HostCommand, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): HostCommand;
  static deserializeBinaryFromReader(message: HostCommand, reader: jspb.BinaryReader): HostCommand;
}

export namespace HostCommand {
  export type AsObject = {
    host: string,
    command: string,
    type: CommandResultTypeMap[keyof CommandResultTypeMap],
  }
}

export class MininetCommand extends jspb.Message {
  hasCommand(): boolean;
  clearCommand(): void;
  getCommand(): string;
  setCommand(value: string): void;

  hasType(): boolean;
  clearType(): void;
  getType(): CommandTypeMap[keyof CommandTypeMap];
  setType(value: CommandTypeMap[keyof CommandTypeMap]): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): MininetCommand.AsObject;
  static toObject(includeInstance: boolean, msg: MininetCommand): MininetCommand.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: MininetCommand, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): MininetCommand;
  static deserializeBinaryFromReader(message: MininetCommand, reader: jspb.BinaryReader): MininetCommand;
}

export namespace MininetCommand {
  export type AsObject = {
    command: string,
    type: CommandTypeMap[keyof CommandTypeMap],
  }
}

export class CommandResult extends jspb.Message {
  hasType(): boolean;
  clearType(): void;
  getType(): CommandResultTypeMap[keyof CommandResultTypeMap];
  setType(value: CommandResultTypeMap[keyof CommandResultTypeMap]): void;

  hasResult(): boolean;
  clearResult(): void;
  getResult(): string;
  setResult(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): CommandResult.AsObject;
  static toObject(includeInstance: boolean, msg: CommandResult): CommandResult.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: CommandResult, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): CommandResult;
  static deserializeBinaryFromReader(message: CommandResult, reader: jspb.BinaryReader): CommandResult;
}

export namespace CommandResult {
  export type AsObject = {
    type: CommandResultTypeMap[keyof CommandResultTypeMap],
    result: string,
  }
}

export interface InstructionTypeMap {
  OFPIT_INVALID: 0;
  OFPIT_GOTO_TABLE: 1;
  OFPIT_WRITE_METADATA: 2;
  OFPIT_WRITE_ACTIONS: 3;
  OFPIT_APPLY_ACTIONS: 4;
  OFPIT_CLEAR_ACTIONS: 5;
  OFPIT_METER: 6;
  OFPIT_EXPERIMENTER: 65535;
}

export const InstructionType: InstructionTypeMap;

export interface StartNetworkOptionMap {
  NO_OPTION: 0;
}

export const StartNetworkOption: StartNetworkOptionMap;

export interface CommandTypeMap {
  NOMAL: 0;
  SIGINT: 1;
}

export const CommandType: CommandTypeMap;

export interface CommandResultTypeMap {
  OUTPUT: 0;
  ERROR: 1;
  END_SIGNAL: 100;
}

export const CommandResultType: CommandResultTypeMap;

