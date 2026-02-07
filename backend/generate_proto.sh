#!/bin/bash
# Script to generate Python code from Protocol Buffer definitions

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROTO_DIR="$SCRIPT_DIR/protos"
OUTPUT_DIR="$SCRIPT_DIR/app/generated"

echo "📦 Generating Python code from Protocol Buffers..."

# Create output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# Generate Python code
python3 -m grpc_tools.protoc \
    -I"$PROTO_DIR" \
    --python_out="$OUTPUT_DIR" \
    --grpc_python_out="$OUTPUT_DIR" \
    --pyi_out="$OUTPUT_DIR" \
    "$PROTO_DIR/library.proto"

# Fix imports in generated files (grpc_tools generates relative imports incorrectly)
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    sed -i '' 's/import library_pb2/from app.generated import library_pb2/g' "$OUTPUT_DIR/library_pb2_grpc.py"
else
    # Linux
    sed -i 's/import library_pb2/from app.generated import library_pb2/g' "$OUTPUT_DIR/library_pb2_grpc.py"
fi

echo "✅ Generated Python code in $OUTPUT_DIR"
echo "   - library_pb2.py"
echo "   - library_pb2_grpc.py"
echo "   - library_pb2.pyi"
