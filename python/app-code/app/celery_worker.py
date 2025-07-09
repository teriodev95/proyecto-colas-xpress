"""
Worker de Celery para procesamiento de tareas de mensajería.
Este script se ejecuta como un proceso separado para procesar las tareas encoladas.
"""
import logging
from .celery_app import celery_app

# Configurar logging para el worker
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    logger.info("🔧 Iniciando worker de Celery para mensajería")
    
    # Ejecutar worker con configuración específica
    celery_app.worker_main([
        'worker',
        '--loglevel=info',
        '--queues=transactional_messages',
        '--concurrency=2',  # Número de procesos worker concurrentes
        '--max-tasks-per-child=100'  # Reiniciar worker después de 100 tareas
    ]) 