# Prompt conciso: FastAPI + Celery Mensajería

**Stack:** Python 3.11+, FastAPI, Celery, Redis, Docker Compose

---

## Requisitos

> **Nota:** Antes de levantar los servicios, verifica los puertos en uso en Docker, ya que ya hay una instancia de Evolution API corriendo en el servidor. Ajusta los puertos en `docker-compose.yml` si es necesario para evitar conflictos.

1. **API FastAPI**
   - Endpoint `POST /messages` (JSON: `phone`, `message`)
   - Al recibir, encola tarea Celery `send_transactional_message`.

2. **Worker Celery**
   - Escucha cola `transactional_messages`.
   - El envío de mensajes se realiza usando Evolution API, que está en el mismo servidor. Nada de simulaciones: todo debe funcionar correctamente con datos reales.
   - Reintenta hasta 3 veces, delay 5s si falla.

3. **Docker**
   - Dockerfile FastAPI (Python 3.11, uvicorn)
   - Dockerfile Celery worker (Python 3.11)
   - `docker-compose.yml` con servicios: `api`, `worker`, `redis` (puerto 8000 expuesto)

4. **Estructura**
   - `/project/app/{main.py, celery_worker.py, tasks.py}`
   - `requirements.txt`, `Dockerfile`, `docker-compose.yml`

5. **Celery**
   - Redis como broker (`redis` hostname)
   - Retries: máx 3, countdown 5s
   - Logs en: recepción HTTP, encolado, éxito, error

6. **Uso**
   - `docker-compose build && docker-compose up`
   - Test: `curl -X POST http://localhost:8000/messages -H "Content-Type: application/json" -d '{"phone": "+52123456789", "message": "Hola Carlos"}'`

7. **Notas**
   - Usa tipado con Pydantic
   - Flower opcional para monitoreo Celery

8. **Documentación**
   - Crear un README muy práctico y sencillo, que incluya:
     - Un diagrama de funcionamiento del sistema.
     - Instrucciones claras de cómo levantar, detener y volver a correr el sistema.

9. **Calidad de Código**
   - El código debe estar desacoplado y ser modular, agrupado feature by folder para fácil mantenimiento.
   - Todo el código debe estar muy bien explicado con comentarios fáciles de entender, breves y concisos.


✅ Objetivo
Generar un microservicio robusto y dockerizado con FastAPI + Celery para procesar mensajes transaccionales, asegurando:

Persistencia de tareas.

Retries automáticos.

Delay entre reintentos.

Escalabilidad sencilla con Docker.