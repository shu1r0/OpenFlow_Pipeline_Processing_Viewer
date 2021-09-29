#! /bin/bash

PLUGIN_TS=../../node_modules/.bin/protoc-gen-ts

PLUGIN_GRPC=../../node_modules/.bin/grpc_tools_node_protoc_plugin

DIST_DIR=.
DIST_DIR_TS=.

protoc \
--js_out=import_style=commonjs,binary:"${DIST_DIR}"/ \
--ts_out=import_style=commonjs,binary:"${DIST_DIR_TS}"/ \
--grpc_out="${DIST_DIR}"/ \
--plugin=protoc-gen-grpc="${PLUGIN_GRPC}" \
--plugin=protoc-gen-ts="${PLUGIN_TS}" \
-I /Users/shu_ruhe/lesson/Network/tracing_of_pipeline/src/api/proto/ \
/Users/shu_ruhe/lesson/Network/tracing_of_pipeline/src/api/proto/net.proto