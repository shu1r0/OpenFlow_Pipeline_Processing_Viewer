# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import src.vnet.api.tracer_net_pb2 as tracer__net__pb2


class TracerNetServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.addNode = channel.unary_unary(
                '/api.TracerNetService/addNode',
                request_serializer=tracer__net__pb2.Node.SerializeToString,
                response_deserializer=tracer__net__pb2.Result.FromString,
                )
        self.removeNode = channel.unary_unary(
                '/api.TracerNetService/removeNode',
                request_serializer=tracer__net__pb2.Node.SerializeToString,
                response_deserializer=tracer__net__pb2.Result.FromString,
                )
        self.addLink = channel.unary_unary(
                '/api.TracerNetService/addLink',
                request_serializer=tracer__net__pb2.Link.SerializeToString,
                response_deserializer=tracer__net__pb2.Result.FromString,
                )
        self.removeLink = channel.unary_unary(
                '/api.TracerNetService/removeLink',
                request_serializer=tracer__net__pb2.Link.SerializeToString,
                response_deserializer=tracer__net__pb2.Result.FromString,
                )


class TracerNetServiceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def addNode(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def removeNode(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def addLink(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def removeLink(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_TracerNetServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'addNode': grpc.unary_unary_rpc_method_handler(
                    servicer.addNode,
                    request_deserializer=tracer__net__pb2.Node.FromString,
                    response_serializer=tracer__net__pb2.Result.SerializeToString,
            ),
            'removeNode': grpc.unary_unary_rpc_method_handler(
                    servicer.removeNode,
                    request_deserializer=tracer__net__pb2.Node.FromString,
                    response_serializer=tracer__net__pb2.Result.SerializeToString,
            ),
            'addLink': grpc.unary_unary_rpc_method_handler(
                    servicer.addLink,
                    request_deserializer=tracer__net__pb2.Link.FromString,
                    response_serializer=tracer__net__pb2.Result.SerializeToString,
            ),
            'removeLink': grpc.unary_unary_rpc_method_handler(
                    servicer.removeLink,
                    request_deserializer=tracer__net__pb2.Link.FromString,
                    response_serializer=tracer__net__pb2.Result.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'api.TracerNetService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class TracerNetService(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def addNode(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/api.TracerNetService/addNode',
            tracer__net__pb2.Node.SerializeToString,
            tracer__net__pb2.Result.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def removeNode(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/api.TracerNetService/removeNode',
            tracer__net__pb2.Node.SerializeToString,
            tracer__net__pb2.Result.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def addLink(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/api.TracerNetService/addLink',
            tracer__net__pb2.Link.SerializeToString,
            tracer__net__pb2.Result.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def removeLink(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/api.TracerNetService/removeLink',
            tracer__net__pb2.Link.SerializeToString,
            tracer__net__pb2.Result.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
