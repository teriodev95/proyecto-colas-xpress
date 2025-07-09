# Evolution API v2.1.1 - Docker Setup

## 🚀 Servicios Incluidos

- **Evolution API v2.1.1**: API principal de WhatsApp
- **PostgreSQL 15**: Base de datos principal
- **Redis 7**: Sistema de cache

## 📋 Inicio Rápido

```bash
# Iniciar todos los servicios
docker-compose up -d

# Ver estado de contenedores
docker-compose ps

# Ver logs
docker-compose logs evolution-api

# Detener servicios
docker-compose down
```

## 🔑 Acceso

- **Evolution API**: http://localhost:8080
- **Manager Web**: http://localhost:8080/manager/
- **API Key**: f60859261b61e89087078576c020c9c1d0d2f8b87fa09c5cba009b8ca69a98e0
- **Swagger Docs**: http://localhost:8080/docs

## 📱 Configuración QR

La configuración incluye `CONFIG_SESSION_PHONE_VERSION=2.3000.1023204200` para la correcta generación de códigos QR.
