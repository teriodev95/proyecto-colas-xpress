"""
Configuración centralizada del sistema.
Maneja variables de entorno y configuración global.
"""
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Configuración de la aplicación usando Pydantic para validación de tipos."""
    
    # Configuración Redis
    redis_host: str = os.getenv("REDIS_HOST", "redis")
    redis_port: int = int(os.getenv("REDIS_PORT", "6379"))
    redis_db: int = int(os.getenv("REDIS_DB", "0"))
    
    # Configuración Evolution API
    evolution_api_url: str = os.getenv("EVOLUTION_API_URL", "http://localhost:8080")
    evolution_api_key: str = os.getenv("EVOLUTION_API_KEY", "")
    evolution_instance_name: str = os.getenv("EVOLUTION_INSTANCE_NAME", "default")
    
    # Configuración de la aplicación
    app_host: str = os.getenv("APP_HOST", "0.0.0.0")
    app_port: int = int(os.getenv("APP_PORT", "8000"))
    
    # Configuración Celery
    celery_broker_url: str = f"redis://{redis_host}:{redis_port}/{redis_db}"
    celery_result_backend: str = f"redis://{redis_host}:{redis_port}/{redis_db}"
    
    class Config:
        env_file = ".env"

# Instancia global de configuración
settings = Settings() 