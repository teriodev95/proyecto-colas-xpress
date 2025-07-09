#!/bin/bash

# Script de prueba para el microservicio de mensajería
# Verifica que todos los componentes estén funcionando correctamente

echo -e "\033[0;34m🧪 Iniciando pruebas del sistema...\033[0m"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Variables
API_URL="http://localhost:8001"
FLOWER_URL="http://localhost:5556"

# Test 1: Health Check de la API
echo -e "${YELLOW}[TEST]${NC} Verificando que la API esté disponible..."
if curl -s "$API_URL/health" > /dev/null; then
    echo -e "${GREEN}[✓]${NC} API está respondiendo correctamente"
else
    echo -e "${RED}[✗]${NC} API no está disponible"
    exit 1
fi

# Test 2: Endpoint root
echo -e "${YELLOW}[TEST]${NC} Probando endpoint root..."
ROOT_RESPONSE=$(curl -s "$API_URL/")
if echo "$ROOT_RESPONSE" | grep -q "Microservicio de Mensajería"; then
    echo -e "${GREEN}[✓]${NC} Endpoint root funciona correctamente"
else
    echo -e "${RED}[✗]${NC} Endpoint root no responde correctamente"
fi

# Test 3: Envío de mensaje de prueba
echo -e "${YELLOW}[TEST]${NC} Enviando mensaje de prueba..."
MESSAGE_RESPONSE=$(curl -s -X POST "$API_URL/messages" \
    -H "Content-Type: application/json" \
    -d '{
        "phone": "+521234567890",
        "message": "Mensaje de prueba desde el sistema automático",
        "instance_name": "default"
    }')

if echo "$MESSAGE_RESPONSE" | grep -q "task_id"; then
    TASK_ID=$(echo "$MESSAGE_RESPONSE" | grep -o '"task_id":"[^"]*"' | cut -d'"' -f4)
    echo -e "${GREEN}[✓]${NC} Mensaje encolado exitosamente. Task ID: $TASK_ID"
    
    # Test 4: Consulta de estado de tarea
    echo -e "${YELLOW}[TEST]${NC} Esperando procesamiento de la tarea..."
    sleep 5
    
    echo -e "${YELLOW}[TEST]${NC} Consultando estado de la tarea..."
    TASK_STATUS=$(curl -s "$API_URL/tasks/$TASK_ID")
    echo "Estado de la tarea: $TASK_STATUS"
else
    echo -e "${RED}[✗]${NC} Error al enviar mensaje de prueba"
    echo "Respuesta: $MESSAGE_RESPONSE"
fi

# Test 5: Documentación de la API
echo -e "${YELLOW}[TEST]${NC} Verificando documentación de la API..."
if curl -s "$API_URL/docs" | grep -q "swagger"; then
    echo -e "${GREEN}[✓]${NC} Documentación de la API disponible"
else
    echo -e "${RED}[✗]${NC} Documentación de la API no está disponible"
fi

# Test 6: Flower (opcional)
echo -e "${YELLOW}[TEST]${NC} Verificando Flower..."
if curl -s "$FLOWER_URL" > /dev/null; then
    echo -e "${GREEN}[✓]${NC} Flower está funcionando"
else
    echo -e "${YELLOW}[!]${NC} Flower no está disponible (opcional)"
fi

echo ""
echo -e "${GREEN}🎉 Pruebas completadas!${NC}"
echo ""
echo -e "${BLUE}📋 URLs importantes:${NC}"
echo -e "   API: $API_URL"
echo -e "   Docs: $API_URL/docs"
echo -e "   Health: $API_URL/health"
echo -e "   Flower: $FLOWER_URL"
echo ""
echo -e "${BLUE}💡 Para ver logs en tiempo real:${NC}"
echo -e "   docker-compose logs -f" 