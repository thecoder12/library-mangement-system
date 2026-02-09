"""Application configuration settings."""

import os
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database settings
    database_url: str = "postgresql://library_user:library_pass@localhost:5432/library_db"
    
    # gRPC server settings
    grpc_host: str = "0.0.0.0"
    grpc_port: int = 50051
    
    # REST API server settings
    rest_host: str = "0.0.0.0"
    rest_port: int = 8000
    
    # Application settings
    default_borrow_days: int = 14  # Default loan period
    max_books_per_member: int = 5  # Maximum books a member can borrow
    
    # Logging settings
    log_level: str = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    log_format: str = "json"  # "json" for structured logging, "text" for human-readable
    log_file: str = "logs/app.log"  # Log file path (relative to backend dir)
    log_max_bytes: int = 10485760  # 10 MB
    log_backup_count: int = 5  # Number of backup files to keep
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
