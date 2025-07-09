#!/bin/bash

# Script de gestión para el microservicio de mensajería
# Facilita las operaciones comunes del sistema

# Colores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para mostrar ayuda
show_help() {
    echo -e "${BLUE}🛠️  Microservicio de Mensajería - Gestor${NC}"
    echo ""
    echo "Uso: ./manage.sh [comando]"
    echo ""
    echo "Comandos disponibles:"
    echo "  start      - Iniciar el sistema completo"
    echo "  stop       - Detener el sistema"
    echo "  restart    - Reiniciar el sistema"
    echo "  build      - Reconstruir los contenedores"
    echo "  status     - Ver estado de los servicios"
    echo "  logs       - Ver logs en tiempo real"
    echo "  test       - Ejecutar pruebas del sistema"
    echo "  scale      - Escalar workers (ej: ./manage.sh scale 3)"
    echo "  clean      - Limpiar sistema completo"
    echo "  health     - Verificar salud del sistema"
    echo "  monitor    - Abrir herramientas de monitoreo"
    echo "  help       - Mostrar esta ayuda"
    echo ""
}

# Verificar si Docker Compose está disponible
check_docker() {
    if ! command -v docker-compose &> /dev/null; then
        echo -e "${RED}Error: docker-compose no está instalado${NC}"
        exit 1
    fi
}

# Función para iniciar el sistema
start_system() {
    echo -e "${YELLOW}🚀 Iniciando microservicio de mensajería...${NC}"
    docker-compose up -d
    echo -e "${GREEN}✅ Sistema iniciado correctamente${NC}"
    echo ""
    echo "URLs disponibles:"
    echo "  API: http://localhost:8001"
    echo "  Docs: http://localhost:8001/docs"
    echo "  Flower: http://localhost:5556"
}

# Función para detener el sistema
stop_system() {
    echo -e "${YELLOW}🛑 Deteniendo microservicio de mensajería...${NC}"
    docker-compose down
    echo -e "${GREEN}✅ Sistema detenido correctamente${NC}"
}

# Función para reiniciar el sistema
restart_system() {
    echo -e "${YELLOW}🔄 Reiniciando microservicio de mensajería...${NC}"
    docker-compose restart
    echo -e "${GREEN}✅ Sistema reiniciado correctamente${NC}"
}

# Función para construir el sistema
build_system() {
    echo -e "${YELLOW}🔨 Reconstruyendo contenedores...${NC}"
    docker-compose build --no-cache
    docker-compose up -d
    echo -e "${GREEN}✅ Sistema reconstruido e iniciado${NC}"
}

# Función para ver estado
check_status() {
    echo -e "${BLUE}📊 Estado de los servicios:${NC}"
    docker-compose ps
}

# Función para ver logs
show_logs() {
    echo -e "${BLUE}📝 Logs del sistema (Ctrl+C para salir):${NC}"
    docker-compose logs -f
}

# Función para ejecutar pruebas
run_tests() {
    echo -e "${YELLOW}🧪 Ejecutando pruebas del sistema...${NC}"
    if [ -f "scripts/test-system.sh" ]; then
        chmod +x scripts/test-system.sh
        ./scripts/test-system.sh
    else
        echo -e "${RED}Error: archivo de pruebas no encontrado${NC}"
    fi
}

# Función para escalar workers
scale_workers() {
    if [ -z "$2" ]; then
        echo -e "${RED}Error: especifica el número de workers${NC}"
        echo "Uso: ./manage.sh scale [número]"
        exit 1
    fi
    
    echo -e "${YELLOW}⚖️ Escalando workers a $2 instancias...${NC}"
    docker-compose up --scale worker=$2 -d
    echo -e "${GREEN}✅ Workers escalados correctamente${NC}"
}

# Función para limpiar sistema
clean_system() {
    echo -e "${YELLOW}🧹 Limpiando sistema completo...${NC}"
    echo "Esto eliminará todos los contenedores, volúmenes e imágenes"
    read -p "¿Estás seguro? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker-compose down -v --rmi all --remove-orphans
        echo -e "${GREEN}✅ Sistema limpiado completamente${NC}"
    else
        echo -e "${YELLOW}Operación cancelada${NC}"
    fi
}

# Función para verificar salud
check_health() {
    echo -e "${BLUE}🏥 Verificando salud del sistema...${NC}"
    echo ""
    
    # Verificar API
    if curl -s http://localhost:8001/health > /dev/null; then
        echo -e "${GREEN}✅ API: Funcionando${NC}"
    else
        echo -e "${RED}❌ API: No disponible${NC}"
    fi
    
    # Verificar Redis
    if docker-compose exec -T redis redis-cli ping | grep -q "PONG"; then
        echo -e "${GREEN}✅ Redis: Funcionando${NC}"
    else
        echo -e "${RED}❌ Redis: No disponible${NC}"
    fi
    
    # Verificar Worker
    if docker-compose ps worker | grep -q "Up"; then
        echo -e "${GREEN}✅ Worker: Funcionando${NC}"
    else
        echo -e "${RED}❌ Worker: No disponible${NC}"
    fi
    
    # Verificar Flower
    if curl -s http://localhost:5556 > /dev/null; then
        echo -e "${GREEN}✅ Flower: Funcionando${NC}"
    else
        echo -e "${RED}❌ Flower: No disponible${NC}"
    fi
}

# Función para abrir herramientas de monitoreo
open_monitoring() {
    echo -e "${BLUE}📊 Abriendo herramientas de monitoreo...${NC}"
    
    if command -v xdg-open &> /dev/null; then
        xdg-open http://localhost:8001/docs
        xdg-open http://localhost:5556
    elif command -v open &> /dev/null; then
        open http://localhost:8001/docs
        open http://localhost:5556
    else
        echo "URLs de monitoreo:"
        echo "  API Docs: http://localhost:8001/docs"
        echo "  Flower: http://localhost:5556"
    fi
}

# Verificar Docker
check_docker

# Procesar comandos
case "$1" in
    "start")
        start_system
        ;;
    "stop")
        stop_system
        ;;
    "restart")
        restart_system
        ;;
    "build")
        build_system
        ;;
    "status")
        check_status
        ;;
    "logs")
        show_logs
        ;;
    "test")
        run_tests
        ;;
    "scale")
        scale_workers "$@"
        ;;
    "clean")
        clean_system
        ;;
    "health")
        check_health
        ;;
    "monitor")
        open_monitoring
        ;;
    "help"|"--help"|"-h")
        show_help
        ;;
    "")
        show_help
        ;;
    *)
        echo -e "${RED}Error: Comando desconocido '$1'${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac 