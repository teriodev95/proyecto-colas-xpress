# Estructura Modular del Proyecto Python

## Organizacion del Proyecto

/home/python/
- infrastructure/                    # Infraestructura (NO CAMBIAR)
  - docker-compose.infra.yml        # Redis + Flower
  - redis/
    - redis.conf                    # Configuracion Redis
- app-code/                         # Codigo Python (CAMBIAR AQUI)
  - app/
    - main.py                       # FastAPI app
    - tasks.py                      # Tareas Celery
    - celery_app.py                 # Configuracion Celery
- docker-compose.app.yml            # Servicios de aplicacion
- Dockerfile                        # Imagen de la API
- Dockerfile.worker                 # Imagen del worker
- scripts/                          # Scripts de manejo
  - start-infra.sh                 # Iniciar infraestructura
  - start-app.sh                   # Iniciar aplicacion
  - restart-app.sh                 # Reiniciar solo app

## Comandos de Uso

### 1. Iniciar Infraestructura (solo una vez)
./scripts/start-infra.sh

### 2. Iniciar Aplicacion
./scripts/start-app.sh

### 3. Reiniciar Solo la Aplicacion (despues de cambios en codigo)
./scripts/restart-app.sh

## Ventajas de esta estructura:

- Infraestructura estable: Redis y Flower no se reinician al cambiar codigo
- Desarrollo agil: Solo rebuilds la app cuando cambias Python
- Persistencia garantizada: Las colas se mantienen al reiniciar app
- Facil mantenimiento: Codigo separado de infraestructura
- Escalable: Facil agregar mas servicios de infra

## URLs de Acceso:
- API: http://localhost:8001
- Flower (monitoring): http://localhost:5556
- Redis: localhost:6380
