"""
Aplicación FastAPI para el microservicio de mensajería.
Proporciona endpoints REST para envío de mensajes y consulta de estado.
"""
import logging
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from .models import MessageRequest, MessageResponse, TaskStatus
from .tasks import send_transactional_message, get_task_status
from .config import settings
from .celery_app import celery_app
import redis
from datetime import datetime
import os

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Crear aplicación FastAPI
app = FastAPI(
    title="Microservicio de Mensajería",
    description="API para envío de mensajes transaccionales usando Evolution API y Celery by calaverita*",
    version="1.0.1",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS para permitir requests desde cualquier origen
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Evento ejecutado al iniciar la aplicación."""
    logger.info("🚀 Iniciando microservicio de mensajería")
    logger.info(f"📡 Conectado a Redis en: {settings.redis_host}:{settings.redis_port}")
    logger.info(f"🔗 Evolution API URL: {settings.evolution_api_url}")

@app.get("/", status_code=status.HTTP_200_OK)
async def root():
    """
    Endpoint de health check.
    Verifica que la API esté funcionando correctamente.
    """
    return {
        "message": "Microservicio de Mensajería activo 1.0.1",
        "status": "healthy",
        "docs": "/docs",
        "monitoring": "/monitoring"
    }

@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """
    Endpoint de monitoreo de salud del servicio.
    """
    return {
        "status": "healthy",
        "service": "messaging-api",
        "redis_host": settings.redis_host
    }

@app.get("/monitoring", status_code=status.HTTP_200_OK)
async def get_monitoring_info():
    """
    Endpoint completo de monitoreo del sistema de mensajería.
    Incluye información de Celery, Redis, workers y enlaces de monitoreo.
    """
    try:
        # Obtener información de Celery
        inspect = celery_app.control.inspect()
        
        # Información de workers activos
        active_workers = inspect.active() or {}
        registered_tasks = inspect.registered() or {}
        
        # Conexión a Redis para estadísticas
        redis_client = redis.Redis(
            host=settings.redis_host, 
            port=settings.redis_port, 
            db=settings.redis_db
        )
        
        # Información de la cola de mensajes
        queue_length = redis_client.llen('transactional_messages')
        redis_info = redis_client.info()
        
        # URLs del sistema
        base_url = os.getenv('BASE_URL', 'http://65.109.10.85')
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "service_info": {
                "name": "Microservicio de Mensajería",
                "version": "1.0.0",
                "status": "running",
                "uptime": redis_info.get('uptime_in_seconds', 0)
            },
            "monitoring_urls": {
                "flower_dashboard": f"{base_url}:5556",
                "flower_tasks": f"{base_url}:5556/tasks",
                "flower_workers": f"{base_url}:5556/workers",
                "flower_broker": f"{base_url}:5556/broker",
                "api_docs": f"{base_url}:8001/docs",
                "api_health": f"{base_url}:8001/health"
            },
            "celery_info": {
                "workers": {
                    "active_workers": len(active_workers),
                    "worker_details": active_workers,
                    "registered_tasks": list(registered_tasks.keys()) if registered_tasks else []
                },
                "queue_info": {
                    "transactional_messages_queue": queue_length,
                    "rate_limit": "1 mensaje por segundo",
                    "max_retries": 3,
                    "retry_delay": "5 segundos"
                }
            },
            "redis_info": {
                "host": settings.redis_host,
                "port": settings.redis_port,
                "database": settings.redis_db,
                "connected_clients": redis_info.get('connected_clients', 0),
                "total_commands_processed": redis_info.get('total_commands_processed', 0),
                "memory_usage": f"{redis_info.get('used_memory_human', 'N/A')}",
                "uptime": f"{redis_info.get('uptime_in_seconds', 0)} segundos"
            },
            "evolution_api": {
                "url": settings.evolution_api_url,
                "configured": bool(settings.evolution_api_key),
                "endpoints": {
                    "send_text": f"{settings.evolution_api_url}/message/sendText/{{instance_name}}"
                }
            },
            "system_stats": {
                "total_messages_in_queue": queue_length,
                "estimated_processing_time": f"{queue_length} segundos" if queue_length > 0 else "0 segundos",
                "rate_limit_info": {
                    "current": "1 mensaje/segundo",
                    "description": "Los mensajes se procesan secuencialmente respetando este límite"
                }
            },
            "useful_commands": {
                "check_queue": "docker exec -it messaging_redis redis-cli LLEN transactional_messages",
                "view_logs": "docker-compose logs --tail=50 worker",
                "restart_worker": "docker-compose restart worker",
                "scale_workers": "docker-compose up --scale worker=2 -d"
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo información de monitoreo: {str(e)}")
        return {
            "error": "No se pudo obtener información completa de monitoreo",
            "basic_info": {
                "timestamp": datetime.utcnow().isoformat(),
                "flower_url": "http://65.109.10.85:5556",
                "api_status": "running",
                "error_details": str(e)
            }
        }

@app.post("/messages", response_model=MessageResponse, status_code=status.HTTP_202_ACCEPTED)
async def send_message(message_data: MessageRequest):
    """
    Envía un mensaje transaccional de forma asíncrona.
    
    Args:
        message_data: Datos del mensaje (teléfono y texto)
        
    Returns:
        MessageResponse: Confirmación de encolado con ID de tarea
        
    Raises:
        HTTPException: Si hay error al encolar la tarea
    """
    try:
        logger.info(f"📨 Recibida solicitud de mensaje para: {message_data.phone}")
        
        # Encolar tarea en Celery
        task = send_transactional_message.delay(
            phone=message_data.phone,
            message=message_data.message,
            instance_name=message_data.instance_name
        )
        
        logger.info(f"✅ Mensaje encolado exitosamente - Tarea ID: {task.id}")
        
        return MessageResponse(
            success=True,
            message="Mensaje encolado correctamente para procesamiento",
            task_id=task.id
        )
        
    except Exception as e:
        logger.error(f"❌ Error al encolar mensaje: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )

@app.get("/tasks/{task_id}", response_model=TaskStatus, status_code=status.HTTP_200_OK)
async def get_task_info(task_id: str):
    """
    Consulta el estado de una tarea específica.
    
    Args:
        task_id: ID de la tarea a consultar
        
    Returns:
        TaskStatus: Estado actual de la tarea
        
    Raises:
        HTTPException: Si la tarea no existe
    """
    try:
        logger.info(f"🔍 Consultando estado de tarea: {task_id}")
        
        # Obtener estado de la tarea
        task_info = get_task_status.delay(task_id)
        result = task_info.get(timeout=5)
        
        return TaskStatus(
            task_id=task_id,
            status=result["status"],
            result=result["result"]
        )
        
    except Exception as e:
        logger.error(f"❌ Error consultando tarea {task_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tarea no encontrada: {task_id}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=True,
        log_level="info"
    ) 