#\!/bin/bash

echo "🔄 Reiniciando solo la aplicación (manteniendo infraestructura)..."

cd /home/python
docker-compose -f docker-compose.app.yml down
docker-compose -f docker-compose.app.yml up -d --build

echo "✅ Aplicación reiniciada"
echo "🌐 API: http://localhost:8001"
