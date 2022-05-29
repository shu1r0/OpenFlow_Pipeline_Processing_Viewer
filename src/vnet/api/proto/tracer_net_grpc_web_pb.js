/**
 * @fileoverview gRPC-Web generated client stub for api.proto
 * @enhanceable
 * @public
 */

// GENERATED CODE -- DO NOT EDIT!


/* eslint-disable */
// @ts-nocheck



const grpc = {};
grpc.web = require('grpc-web');

const proto = {};
proto.api = {};
proto.api.proto = require('./tracer_net_pb.js');

/**
 * @param {string} hostname
 * @param {?Object} credentials
 * @param {?Object} options
 * @constructor
 * @struct
 * @final
 */
proto.api.proto.TracerNetServiceClient =
    function(hostname, credentials, options) {
  if (!options) options = {};
  options['format'] = 'text';

  /**
   * @private @const {!grpc.web.GrpcWebClientBase} The client
   */
  this.client_ = new grpc.web.GrpcWebClientBase(options);

  /**
   * @private @const {string} The hostname
   */
  this.hostname_ = hostname;

};


/**
 * @param {string} hostname
 * @param {?Object} credentials
 * @param {?Object} options
 * @constructor
 * @struct
 * @final
 */
proto.api.proto.TracerNetServicePromiseClient =
    function(hostname, credentials, options) {
  if (!options) options = {};
  options['format'] = 'text';

  /**
   * @private @const {!grpc.web.GrpcWebClientBase} The client
   */
  this.client_ = new grpc.web.GrpcWebClientBase(options);

  /**
   * @private @const {string} The hostname
   */
  this.hostname_ = hostname;

};


/**
 * @const
 * @type {!grpc.web.MethodDescriptor<
 *   !proto.api.proto.Node,
 *   !proto.api.proto.Result>}
 */
const methodDescriptor_TracerNetService_addNode = new grpc.web.MethodDescriptor(
  '/api.proto.TracerNetService/addNode',
  grpc.web.MethodType.UNARY,
  proto.api.proto.Node,
  proto.api.proto.Result,
  /**
   * @param {!proto.api.proto.Node} request
   * @return {!Uint8Array}
   */
  function(request) {
    return request.serializeBinary();
  },
  proto.api.proto.Result.deserializeBinary
);


/**
 * @const
 * @type {!grpc.web.AbstractClientBase.MethodInfo<
 *   !proto.api.proto.Node,
 *   !proto.api.proto.Result>}
 */
const methodInfo_TracerNetService_addNode = new grpc.web.AbstractClientBase.MethodInfo(
  proto.api.proto.Result,
  /**
   * @param {!proto.api.proto.Node} request
   * @return {!Uint8Array}
   */
  function(request) {
    return request.serializeBinary();
  },
  proto.api.proto.Result.deserializeBinary
);


/**
 * @param {!proto.api.proto.Node} request The
 *     request proto
 * @param {?Object<string, string>} metadata User defined
 *     call metadata
 * @param {function(?grpc.web.Error, ?proto.api.proto.Result)}
 *     callback The callback function(error, response)
 * @return {!grpc.web.ClientReadableStream<!proto.api.proto.Result>|undefined}
 *     The XHR Node Readable Stream
 */
proto.api.proto.TracerNetServiceClient.prototype.addNode =
    function(request, metadata, callback) {
  return this.client_.rpcCall(this.hostname_ +
      '/api.proto.TracerNetService/addNode',
      request,
      metadata || {},
      methodDescriptor_TracerNetService_addNode,
      callback);
};


/**
 * @param {!proto.api.proto.Node} request The
 *     request proto
 * @param {?Object<string, string>} metadata User defined
 *     call metadata
 * @return {!Promise<!proto.api.proto.Result>}
 *     Promise that resolves to the response
 */
proto.api.proto.TracerNetServicePromiseClient.prototype.addNode =
    function(request, metadata) {
  return this.client_.unaryCall(this.hostname_ +
      '/api.proto.TracerNetService/addNode',
      request,
      metadata || {},
      methodDescriptor_TracerNetService_addNode);
};


/**
 * @const
 * @type {!grpc.web.MethodDescriptor<
 *   !proto.api.proto.Node,
 *   !proto.api.proto.Result>}
 */
const methodDescriptor_TracerNetService_removeNode = new grpc.web.MethodDescriptor(
  '/api.proto.TracerNetService/removeNode',
  grpc.web.MethodType.UNARY,
  proto.api.proto.Node,
  proto.api.proto.Result,
  /**
   * @param {!proto.api.proto.Node} request
   * @return {!Uint8Array}
   */
  function(request) {
    return request.serializeBinary();
  },
  proto.api.proto.Result.deserializeBinary
);


/**
 * @const
 * @type {!grpc.web.AbstractClientBase.MethodInfo<
 *   !proto.api.proto.Node,
 *   !proto.api.proto.Result>}
 */
const methodInfo_TracerNetService_removeNode = new grpc.web.AbstractClientBase.MethodInfo(
  proto.api.proto.Result,
  /**
   * @param {!proto.api.proto.Node} request
   * @return {!Uint8Array}
   */
  function(request) {
    return request.serializeBinary();
  },
  proto.api.proto.Result.deserializeBinary
);


/**
 * @param {!proto.api.proto.Node} request The
 *     request proto
 * @param {?Object<string, string>} metadata User defined
 *     call metadata
 * @param {function(?grpc.web.Error, ?proto.api.proto.Result)}
 *     callback The callback function(error, response)
 * @return {!grpc.web.ClientReadableStream<!proto.api.proto.Result>|undefined}
 *     The XHR Node Readable Stream
 */
proto.api.proto.TracerNetServiceClient.prototype.removeNode =
    function(request, metadata, callback) {
  return this.client_.rpcCall(this.hostname_ +
      '/api.proto.TracerNetService/removeNode',
      request,
      metadata || {},
      methodDescriptor_TracerNetService_removeNode,
      callback);
};


/**
 * @param {!proto.api.proto.Node} request The
 *     request proto
 * @param {?Object<string, string>} metadata User defined
 *     call metadata
 * @return {!Promise<!proto.api.proto.Result>}
 *     Promise that resolves to the response
 */
proto.api.proto.TracerNetServicePromiseClient.prototype.removeNode =
    function(request, metadata) {
  return this.client_.unaryCall(this.hostname_ +
      '/api.proto.TracerNetService/removeNode',
      request,
      metadata || {},
      methodDescriptor_TracerNetService_removeNode);
};


/**
 * @const
 * @type {!grpc.web.MethodDescriptor<
 *   !proto.api.proto.Link,
 *   !proto.api.proto.Result>}
 */
const methodDescriptor_TracerNetService_addLink = new grpc.web.MethodDescriptor(
  '/api.proto.TracerNetService/addLink',
  grpc.web.MethodType.UNARY,
  proto.api.proto.Link,
  proto.api.proto.Result,
  /**
   * @param {!proto.api.proto.Link} request
   * @return {!Uint8Array}
   */
  function(request) {
    return request.serializeBinary();
  },
  proto.api.proto.Result.deserializeBinary
);


/**
 * @const
 * @type {!grpc.web.AbstractClientBase.MethodInfo<
 *   !proto.api.proto.Link,
 *   !proto.api.proto.Result>}
 */
const methodInfo_TracerNetService_addLink = new grpc.web.AbstractClientBase.MethodInfo(
  proto.api.proto.Result,
  /**
   * @param {!proto.api.proto.Link} request
   * @return {!Uint8Array}
   */
  function(request) {
    return request.serializeBinary();
  },
  proto.api.proto.Result.deserializeBinary
);


/**
 * @param {!proto.api.proto.Link} request The
 *     request proto
 * @param {?Object<string, string>} metadata User defined
 *     call metadata
 * @param {function(?grpc.web.Error, ?proto.api.proto.Result)}
 *     callback The callback function(error, response)
 * @return {!grpc.web.ClientReadableStream<!proto.api.proto.Result>|undefined}
 *     The XHR Node Readable Stream
 */
proto.api.proto.TracerNetServiceClient.prototype.addLink =
    function(request, metadata, callback) {
  return this.client_.rpcCall(this.hostname_ +
      '/api.proto.TracerNetService/addLink',
      request,
      metadata || {},
      methodDescriptor_TracerNetService_addLink,
      callback);
};


/**
 * @param {!proto.api.proto.Link} request The
 *     request proto
 * @param {?Object<string, string>} metadata User defined
 *     call metadata
 * @return {!Promise<!proto.api.proto.Result>}
 *     Promise that resolves to the response
 */
proto.api.proto.TracerNetServicePromiseClient.prototype.addLink =
    function(request, metadata) {
  return this.client_.unaryCall(this.hostname_ +
      '/api.proto.TracerNetService/addLink',
      request,
      metadata || {},
      methodDescriptor_TracerNetService_addLink);
};


/**
 * @const
 * @type {!grpc.web.MethodDescriptor<
 *   !proto.api.proto.Link,
 *   !proto.api.proto.Result>}
 */
const methodDescriptor_TracerNetService_removeLink = new grpc.web.MethodDescriptor(
  '/api.proto.TracerNetService/removeLink',
  grpc.web.MethodType.UNARY,
  proto.api.proto.Link,
  proto.api.proto.Result,
  /**
   * @param {!proto.api.proto.Link} request
   * @return {!Uint8Array}
   */
  function(request) {
    return request.serializeBinary();
  },
  proto.api.proto.Result.deserializeBinary
);


/**
 * @const
 * @type {!grpc.web.AbstractClientBase.MethodInfo<
 *   !proto.api.proto.Link,
 *   !proto.api.proto.Result>}
 */
const methodInfo_TracerNetService_removeLink = new grpc.web.AbstractClientBase.MethodInfo(
  proto.api.proto.Result,
  /**
   * @param {!proto.api.proto.Link} request
   * @return {!Uint8Array}
   */
  function(request) {
    return request.serializeBinary();
  },
  proto.api.proto.Result.deserializeBinary
);


/**
 * @param {!proto.api.proto.Link} request The
 *     request proto
 * @param {?Object<string, string>} metadata User defined
 *     call metadata
 * @param {function(?grpc.web.Error, ?proto.api.proto.Result)}
 *     callback The callback function(error, response)
 * @return {!grpc.web.ClientReadableStream<!proto.api.proto.Result>|undefined}
 *     The XHR Node Readable Stream
 */
proto.api.proto.TracerNetServiceClient.prototype.removeLink =
    function(request, metadata, callback) {
  return this.client_.rpcCall(this.hostname_ +
      '/api.proto.TracerNetService/removeLink',
      request,
      metadata || {},
      methodDescriptor_TracerNetService_removeLink,
      callback);
};


/**
 * @param {!proto.api.proto.Link} request The
 *     request proto
 * @param {?Object<string, string>} metadata User defined
 *     call metadata
 * @return {!Promise<!proto.api.proto.Result>}
 *     Promise that resolves to the response
 */
proto.api.proto.TracerNetServicePromiseClient.prototype.removeLink =
    function(request, metadata) {
  return this.client_.unaryCall(this.hostname_ +
      '/api.proto.TracerNetService/removeLink',
      request,
      metadata || {},
      methodDescriptor_TracerNetService_removeLink);
};


module.exports = proto.api.proto;

