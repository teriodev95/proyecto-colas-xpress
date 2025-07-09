#\!/bin/bash

echo "🚀 Iniciando aplicación (API + Worker)..."

# Verificar que la red existe
docker network ls | grep messaging_network || docker network create messaging_network

cd /home/python
docker-compose -f docker-compose.app.yml up -d

echo "✅ Aplicación iniciada"
echo "🌐 API: http://localhost:8001"
echo "👷 Worker: Procesando en background"
