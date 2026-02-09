# Backend Dockerfile for the Library Service
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code first
COPY app/ ./app/
COPY server.py rest_server.py ./

# Create logs directory
RUN mkdir -p logs

# Copy proto files and generate code
COPY protos/ ./protos/
COPY generate_proto.sh .
RUN mkdir -p app/generated && touch app/generated/__init__.py

# Generate proto files
RUN python -m grpc_tools.protoc \
    -Iprotos \
    --python_out=app/generated \
    --grpc_python_out=app/generated \
    protos/library.proto && \
    sed -i 's/import library_pb2/from app.generated import library_pb2/g' app/generated/library_pb2_grpc.py

# Expose ports (gRPC: 50051, REST: 8000)
EXPOSE 50051 8000

# Default to REST server (can be overridden)
CMD ["python", "rest_server.py"]
