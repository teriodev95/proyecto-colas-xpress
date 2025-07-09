# ⚡ Inicio Rápido - Microservicio de Mensajería

## 🏃‍♂️ Solo 3 pasos para funcionar

### 1. Configurar Evolution API
```bash
cp .env.example .env
nano .env  # Editar con tus credenciales reales de Evolution API
```

### 2. Levantar el sistema
```bash
docker-compose up --build -d
```

### 3. Probar que funciona
```bash
./scripts/test-system.sh
```

## 🎯 URLs importantes después de levantar:
- **API**: http://localhost:8001
- **Documentación**: http://localhost:8001/docs  
- **Monitoreo**: http://localhost:5556

## 🚀 Envío de mensaje de prueba:
```bash
curl -X POST http://localhost:8001/messages \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+52123456789",
    "message": "Hola! Sistema funcionando ✅"
  }'
```

## 🛠️ Gestión rápida:
```bash
./scripts/manage.sh start    # Iniciar
./scripts/manage.sh stop     # Detener  
./scripts/manage.sh logs     # Ver logs
./scripts/manage.sh health   # Verificar salud
```

**¡Listo! Tu microservicio está funcionando! 🎉**

> 📖 Para documentación completa ver [README.md](README.md) 