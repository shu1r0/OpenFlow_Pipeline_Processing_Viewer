#! /bin/bash

PLUGIN_TS=../../../view/node_modules/.bin/protoc-gen-ts

DIST_DIR_TS=../../../view/src/scripts/remote
DIST_DIR_PY=.

PROTO_DIR=.
PROTO=*.proto

protoc \
--ts_out=import_style=commonjs,binary:"${DIST_DIR_TS}"/ \
--js_out=import_style=commonjs,binary:"${DIST_DIR_TS}"/ \
--python_out="${DIST_DIR_PY}"/ \
--plugin=protoc-gen-ts="${PLUGIN_TS}" \
-I ${PROTO_DIR} \
${PROTO}