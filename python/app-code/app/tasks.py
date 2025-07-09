"""
Tareas de Celery para procesamiento asíncrono de mensajes.
Incluye envío de mensajes usando Evolution API con reintentos automáticos.
"""
import logging
import httpx
from celery import Task
from celery.exceptions import Retry
from .celery_app import celery_app
from .config import settings

# Configurar logging
logger = logging.getLogger(__name__)

class CallbackTask(Task):
    """
    Tarea base personalizada para manejo de callbacks y logging.
    """
    def on_success(self, retval, task_id, args, kwargs):
        """Callback ejecutado cuando la tarea se completa exitosamente."""
        logger.info(f"✅ Tarea {task_id} completada exitosamente: {retval}")
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Callback ejecutado cuando la tarea falla después de todos los reintentos."""
        logger.error(f"❌ Tarea {task_id} falló definitivamente: {exc}")
    
    def on_retry(self, exc, task_id, args, kwargs, einfo):
        """Callback ejecutado cuando la tarea se reintenta."""
        logger.warning(f"🔄 Reintentando tarea {task_id}: {exc}")

@celery_app.task(
    bind=True, 
    base=CallbackTask, 
    max_retries=3, 
    default_retry_delay=5,
    rate_limit='1/s'  # Límite de 1 mensaje por segundo
)
def send_transactional_message(self, phone: str, message: str, instance_name: str = "default") -> dict:
    """
    Envía un mensaje transaccional usando Evolution API.
    
    Args:
        phone: Número de teléfono en formato internacional
        message: Mensaje a enviar
        instance_name: Nombre de la instancia de Evolution API
        
    Returns:
        dict: Resultado del envío con status y detalles
        
    Raises:
        Retry: Si el envío falla y quedan reintentos disponibles
    """
    task_id = self.request.id
    logger.info(f"📤 Procesando mensaje para {phone} via instancia {instance_name} - Tarea ID: {task_id}")
    
    try:
        # Preparar datos para Evolution API (coincide con el formato del curl)
        payload = {
            "number": phone,
            "text": message
        }
        
        # Headers según el ejemplo curl proporcionado
        headers = {
            "Content-Type": "application/json",
            "apikey": settings.evolution_api_key
        }
        
        # URL del endpoint de Evolution API (coincide con el formato del curl)
        url = f"{settings.evolution_api_url}/message/sendText/{instance_name}"
        
        logger.info(f"🔗 Enviando request a: {url}")
        logger.debug(f"📋 Payload: {payload}")
        
        # Realizar solicitud HTTP
        with httpx.Client(timeout=30.0) as client:
            response = client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
        result_data = response.json()
        logger.info(f"📨 Respuesta de Evolution API: {result_data}")
        
        # Verificar si Evolution API reportó éxito
        # Evolution API típicamente retorna un objeto con key o message_id
        if result_data.get("key") or result_data.get("message") or result_data.get("status") == "success":
            message_key = result_data.get("key") or result_data.get("message_id") or "success"
            logger.info(f"✅ Mensaje enviado exitosamente a {phone} - Key: {message_key}")
            return {
                "success": True,
                "phone": phone,
                "message": message,
                "instance_name": instance_name,
                "evolution_key": message_key,
                "evolution_response": result_data,
                "task_id": task_id
            }
        else:
            raise Exception(f"Evolution API no retornó respuesta válida: {result_data}")
            
    except httpx.HTTPStatusError as exc:
        error_msg = f"Error HTTP {exc.response.status_code}: {exc.response.text}"
        logger.error(f"❌ Error HTTP enviando a {phone}: {error_msg}")
        
        # Reintentar solo para errores 5xx (errores del servidor)
        if exc.response.status_code >= 500:
            logger.warning(f"🔄 Reintentando por error del servidor {exc.response.status_code}")
            raise self.retry(exc=exc, countdown=5)
        else:
            # Para errores 4xx (cliente), no reintentar
            logger.error(f"❌ Error del cliente {exc.response.status_code}, no se reintentará")
            return {
                "success": False,
                "phone": phone,
                "instance_name": instance_name,
                "error": error_msg,
                "error_type": "client_error",
                "status_code": exc.response.status_code,
                "task_id": task_id
            }
            
    except httpx.RequestError as exc:
        error_msg = f"Error de conexión: {str(exc)}"
        logger.error(f"❌ Error de conexión enviando a {phone}: {error_msg}")
        logger.warning(f"🔄 Reintentando por error de conexión")
        raise self.retry(exc=exc, countdown=5)
        
    except Exception as exc:
        error_msg = f"Error inesperado: {str(exc)}"
        logger.error(f"❌ Error inesperado enviando a {phone}: {error_msg}")
        logger.warning(f"🔄 Reintentando por error inesperado")
        raise self.retry(exc=exc, countdown=5)

@celery_app.task(bind=True)
def get_task_status(self, task_id: str) -> dict:
    """
    Obtiene el estado de una tarea específica.
    
    Args:
        task_id: ID de la tarea a consultar
        
    Returns:
        dict: Estado y resultado de la tarea
    """
    result = celery_app.AsyncResult(task_id)
    return {
        "task_id": task_id,
        "status": result.status,
        "result": result.result if result.ready() else None,
        "info": result.info
    } 