Se hacen los cambios en el code y posteriormente se ejecutan estos comandos

cd python

# 1. Detener servicios
docker-compose down

# 2. Reconstruir imágenes sin caché
docker-compose build --no-cache

# 3. Levantar servicios
docker-compose up -d