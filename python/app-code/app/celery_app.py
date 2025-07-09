"""
Configuración de Celery para el procesamiento asíncrono de tareas.
Define el broker, backend y configuración de reintentos con persistencia completa.
"""
from celery import Celery
from .config import settings

# Crear instancia de Celery con configuración personalizada
celery_app = Celery(
    "messaging_worker",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=['app.tasks']  # Incluir módulo de tareas
)

# Configuración de Celery con persistencia completa
celery_app.conf.update(
    # Configuración de tareas
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    
    # Configuración de reintentos y timeouts
    task_acks_late=True,  # Confirmar tareas solo después de completarse
    worker_prefetch_multiplier=1,  # Procesar una tarea a la vez
    task_reject_on_worker_lost=True,  # Rechazar tareas si el worker se pierde
    
    # CONFIGURACIÓN DE PERSISTENCIA - ESTO ES LO NUEVO
    task_always_eager=False,  # Asegurar que las tareas se envíen al broker
    task_store_eager_result=True,  # Almacenar resultados incluso en modo eager
    result_expires=3600,  # Resultados expiran en 1 hora
    
    # Configuración de durabilidad de colas
    task_default_queue='default',
    task_default_exchange='default',
    task_default_exchange_type='direct',
    task_default_routing_key='default',
    
    # Configuración de colas duraderas
    task_routes={
        'app.tasks.send_transactional_message': {
            'queue': 'transactional_messages',
            'routing_key': 'transactional_messages',
        },
    },
    
    # Configuración de intercambios y colas duraderas
    task_queues={
        'default': {
            'exchange': 'default',
            'exchange_type': 'direct',
            'routing_key': 'default',
            'durable': True,  # Cola duradera
            'auto_delete': False,  # No eliminar automáticamente
        },
        'transactional_messages': {
            'exchange': 'transactional_messages',
            'exchange_type': 'direct', 
            'routing_key': 'transactional_messages',
            'durable': True,  # Cola duradera
            'auto_delete': False,  # No eliminar automáticamente
        },
    },
    
    # Configuración de monitoreo
    worker_send_task_events=True,
    task_send_sent_event=True,
    
    # Configuración de broker (Redis) para persistencia
    broker_transport_options={
        'visibility_timeout': 3600,  # Tiempo de visibilidad de mensajes
        'fanout_prefix': True,
        'fanout_patterns': True,
        'priority_steps': list(range(10)),  # Soporte para prioridades
    },
    
    # Configuración de resultados
    result_backend_transport_options={
        'retry_on_timeout': True,
        'retry_policy': {
            'timeout': 5.0
        }
    },
)
