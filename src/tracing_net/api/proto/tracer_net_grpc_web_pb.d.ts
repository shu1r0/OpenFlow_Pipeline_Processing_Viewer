import * as grpcWeb from 'grpc-web';

import * as tracer_net_pb from './tracer_net_pb';


export class TracerNetServiceClient {
  constructor (hostname: string,
               credentials?: null | { [index: string]: string; },
               options?: null | { [index: string]: any; });

  addNode(
    request: tracer_net_pb.Node,
    metadata: grpcWeb.Metadata | undefined,
    callback: (err: grpcWeb.Error,
               response: tracer_net_pb.Result) => void
  ): grpcWeb.ClientReadableStream<tracer_net_pb.Result>;

  removeNode(
    request: tracer_net_pb.Node,
    metadata: grpcWeb.Metadata | undefined,
    callback: (err: grpcWeb.Error,
               response: tracer_net_pb.Result) => void
  ): grpcWeb.ClientReadableStream<tracer_net_pb.Result>;

  addLink(
    request: tracer_net_pb.Link,
    metadata: grpcWeb.Metadata | undefined,
    callback: (err: grpcWeb.Error,
               response: tracer_net_pb.Result) => void
  ): grpcWeb.ClientReadableStream<tracer_net_pb.Result>;

  removeLink(
    request: tracer_net_pb.Link,
    metadata: grpcWeb.Metadata | undefined,
    callback: (err: grpcWeb.Error,
               response: tracer_net_pb.Result) => void
  ): grpcWeb.ClientReadableStream<tracer_net_pb.Result>;

}

export class TracerNetServicePromiseClient {
  constructor (hostname: string,
               credentials?: null | { [index: string]: string; },
               options?: null | { [index: string]: any; });

  addNode(
    request: tracer_net_pb.Node,
    metadata?: grpcWeb.Metadata
  ): Promise<tracer_net_pb.Result>;

  removeNode(
    request: tracer_net_pb.Node,
    metadata?: grpcWeb.Metadata
  ): Promise<tracer_net_pb.Result>;

  addLink(
    request: tracer_net_pb.Link,
    metadata?: grpcWeb.Metadata
  ): Promise<tracer_net_pb.Result>;

  removeLink(
    request: tracer_net_pb.Link,
    metadata?: grpcWeb.Metadata
  ): Promise<tracer_net_pb.Result>;

}

