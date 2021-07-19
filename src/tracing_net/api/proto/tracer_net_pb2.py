# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: proto/tracer_net.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='proto/tracer_net.proto',
  package='api.proto',
  syntax='proto3',
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\n\x16proto/tracer_net.proto\x12\tapi.proto\"]\n\x04Node\x12+\n\tnode_type\x18\x01 \x01(\x0e\x32\x13.api.proto.NodeTypeH\x00\x88\x01\x01\x12\x11\n\x04name\x18\x02 \x01(\tH\x01\x88\x01\x01\x42\x0c\n\n_node_typeB\x07\n\x05_name\"r\n\x04Link\x12\x11\n\x04name\x18\x01 \x01(\tH\x00\x88\x01\x01\x12\x17\n\nhost_name1\x18\x02 \x01(\tH\x01\x88\x01\x01\x12\x17\n\nhost_name2\x18\x03 \x01(\tH\x02\x88\x01\x01\x42\x07\n\x05_nameB\r\n\x0b_host_name1B\r\n\x0b_host_name2\"(\n\x06Result\x12\x13\n\x06status\x18\x01 \x01(\x11H\x00\x88\x01\x01\x42\t\n\x07_status* \n\x08NodeType\x12\x08\n\x04HOST\x10\x00\x12\n\n\x06SWITCH\x10\x01\x32\xdc\x01\n\x10TracerNetService\x12/\n\x07\x61\x64\x64Node\x12\x0f.api.proto.Node\x1a\x11.api.proto.Result\"\x00\x12\x32\n\nremoveNode\x12\x0f.api.proto.Node\x1a\x11.api.proto.Result\"\x00\x12/\n\x07\x61\x64\x64Link\x12\x0f.api.proto.Link\x1a\x11.api.proto.Result\"\x00\x12\x32\n\nremoveLink\x12\x0f.api.proto.Link\x1a\x11.api.proto.Result\"\x00\x62\x06proto3'
)

_NODETYPE = _descriptor.EnumDescriptor(
  name='NodeType',
  full_name='api.proto.NodeType',
  filename=None,
  file=DESCRIPTOR,
  create_key=_descriptor._internal_create_key,
  values=[
    _descriptor.EnumValueDescriptor(
      name='HOST', index=0, number=0,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='SWITCH', index=1, number=1,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
  ],
  containing_type=None,
  serialized_options=None,
  serialized_start=290,
  serialized_end=322,
)
_sym_db.RegisterEnumDescriptor(_NODETYPE)

NodeType = enum_type_wrapper.EnumTypeWrapper(_NODETYPE)
HOST = 0
SWITCH = 1



_NODE = _descriptor.Descriptor(
  name='Node',
  full_name='api.proto.Node',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='node_type', full_name='api.proto.Node.node_type', index=0,
      number=1, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='name', full_name='api.proto.Node.name', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
    _descriptor.OneofDescriptor(
      name='_node_type', full_name='api.proto.Node._node_type',
      index=0, containing_type=None,
      create_key=_descriptor._internal_create_key,
    fields=[]),
    _descriptor.OneofDescriptor(
      name='_name', full_name='api.proto.Node._name',
      index=1, containing_type=None,
      create_key=_descriptor._internal_create_key,
    fields=[]),
  ],
  serialized_start=37,
  serialized_end=130,
)


_LINK = _descriptor.Descriptor(
  name='Link',
  full_name='api.proto.Link',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='name', full_name='api.proto.Link.name', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='host_name1', full_name='api.proto.Link.host_name1', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='host_name2', full_name='api.proto.Link.host_name2', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
    _descriptor.OneofDescriptor(
      name='_name', full_name='api.proto.Link._name',
      index=0, containing_type=None,
      create_key=_descriptor._internal_create_key,
    fields=[]),
    _descriptor.OneofDescriptor(
      name='_host_name1', full_name='api.proto.Link._host_name1',
      index=1, containing_type=None,
      create_key=_descriptor._internal_create_key,
    fields=[]),
    _descriptor.OneofDescriptor(
      name='_host_name2', full_name='api.proto.Link._host_name2',
      index=2, containing_type=None,
      create_key=_descriptor._internal_create_key,
    fields=[]),
  ],
  serialized_start=132,
  serialized_end=246,
)


_RESULT = _descriptor.Descriptor(
  name='Result',
  full_name='api.proto.Result',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='status', full_name='api.proto.Result.status', index=0,
      number=1, type=17, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
    _descriptor.OneofDescriptor(
      name='_status', full_name='api.proto.Result._status',
      index=0, containing_type=None,
      create_key=_descriptor._internal_create_key,
    fields=[]),
  ],
  serialized_start=248,
  serialized_end=288,
)

_NODE.fields_by_name['node_type'].enum_type = _NODETYPE
_NODE.oneofs_by_name['_node_type'].fields.append(
  _NODE.fields_by_name['node_type'])
_NODE.fields_by_name['node_type'].containing_oneof = _NODE.oneofs_by_name['_node_type']
_NODE.oneofs_by_name['_name'].fields.append(
  _NODE.fields_by_name['name'])
_NODE.fields_by_name['name'].containing_oneof = _NODE.oneofs_by_name['_name']
_LINK.oneofs_by_name['_name'].fields.append(
  _LINK.fields_by_name['name'])
_LINK.fields_by_name['name'].containing_oneof = _LINK.oneofs_by_name['_name']
_LINK.oneofs_by_name['_host_name1'].fields.append(
  _LINK.fields_by_name['host_name1'])
_LINK.fields_by_name['host_name1'].containing_oneof = _LINK.oneofs_by_name['_host_name1']
_LINK.oneofs_by_name['_host_name2'].fields.append(
  _LINK.fields_by_name['host_name2'])
_LINK.fields_by_name['host_name2'].containing_oneof = _LINK.oneofs_by_name['_host_name2']
_RESULT.oneofs_by_name['_status'].fields.append(
  _RESULT.fields_by_name['status'])
_RESULT.fields_by_name['status'].containing_oneof = _RESULT.oneofs_by_name['_status']
DESCRIPTOR.message_types_by_name['Node'] = _NODE
DESCRIPTOR.message_types_by_name['Link'] = _LINK
DESCRIPTOR.message_types_by_name['Result'] = _RESULT
DESCRIPTOR.enum_types_by_name['NodeType'] = _NODETYPE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

Node = _reflection.GeneratedProtocolMessageType('Node', (_message.Message,), {
  'DESCRIPTOR' : _NODE,
  '__module__' : 'proto.tracer_net_pb2'
  # @@protoc_insertion_point(class_scope:api.proto.Node)
  })
_sym_db.RegisterMessage(Node)

Link = _reflection.GeneratedProtocolMessageType('Link', (_message.Message,), {
  'DESCRIPTOR' : _LINK,
  '__module__' : 'proto.tracer_net_pb2'
  # @@protoc_insertion_point(class_scope:api.proto.Link)
  })
_sym_db.RegisterMessage(Link)

Result = _reflection.GeneratedProtocolMessageType('Result', (_message.Message,), {
  'DESCRIPTOR' : _RESULT,
  '__module__' : 'proto.tracer_net_pb2'
  # @@protoc_insertion_point(class_scope:api.proto.Result)
  })
_sym_db.RegisterMessage(Result)



_TRACERNETSERVICE = _descriptor.ServiceDescriptor(
  name='TracerNetService',
  full_name='api.proto.TracerNetService',
  file=DESCRIPTOR,
  index=0,
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_start=325,
  serialized_end=545,
  methods=[
  _descriptor.MethodDescriptor(
    name='addNode',
    full_name='api.proto.TracerNetService.addNode',
    index=0,
    containing_service=None,
    input_type=_NODE,
    output_type=_RESULT,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
  _descriptor.MethodDescriptor(
    name='removeNode',
    full_name='api.proto.TracerNetService.removeNode',
    index=1,
    containing_service=None,
    input_type=_NODE,
    output_type=_RESULT,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
  _descriptor.MethodDescriptor(
    name='addLink',
    full_name='api.proto.TracerNetService.addLink',
    index=2,
    containing_service=None,
    input_type=_LINK,
    output_type=_RESULT,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
  _descriptor.MethodDescriptor(
    name='removeLink',
    full_name='api.proto.TracerNetService.removeLink',
    index=3,
    containing_service=None,
    input_type=_LINK,
    output_type=_RESULT,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
])
_sym_db.RegisterServiceDescriptor(_TRACERNETSERVICE)

DESCRIPTOR.services_by_name['TracerNetService'] = _TRACERNETSERVICE

# @@protoc_insertion_point(module_scope)
