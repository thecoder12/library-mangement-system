"""gRPC Server for the Neighborhood Library Service."""

import logging
from concurrent import futures
import grpc
from grpc_reflection.v1alpha import reflection

from app.config import get_settings
from app.generated import library_pb2, library_pb2_grpc
from app.services.library_service import LibraryServiceServicer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def serve():
    """Start the gRPC server."""
    settings = get_settings()
    
    # Create gRPC server with thread pool
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10),
        options=[
            ('grpc.max_send_message_length', 50 * 1024 * 1024),
            ('grpc.max_receive_message_length', 50 * 1024 * 1024),
        ]
    )
    
    # Register service
    library_pb2_grpc.add_LibraryServiceServicer_to_server(
        LibraryServiceServicer(), server
    )
    
    # Enable server reflection for debugging with tools like grpcurl
    SERVICE_NAMES = (
        library_pb2.DESCRIPTOR.services_by_name['LibraryService'].full_name,
        reflection.SERVICE_NAME,
    )
    reflection.enable_server_reflection(SERVICE_NAMES, server)
    
    # Bind to address
    address = f"{settings.grpc_host}:{settings.grpc_port}"
    server.add_insecure_port(address)
    
    # Start server
    server.start()
    logger.info(f"🚀 gRPC server started on {address}")
    logger.info(f"📚 Neighborhood Library Service is ready to accept requests")
    
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("Shutting down server...")
        server.stop(grace=5)


if __name__ == "__main__":
    serve()
