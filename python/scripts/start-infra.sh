#\!/bin/bash

echo "🚀 Iniciando infraestructura (Redis + Flower)..."

cd /home/python/infrastructure
docker-compose -f docker-compose.infra.yml up -d

echo "✅ Infraestructura iniciada"
echo "📊 Flower (monitoring): http://localhost:5556"
echo "🗄️ Redis: localhost:6380"
