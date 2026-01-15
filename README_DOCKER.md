# 🐳 Guía de Dockerización - Generator_PPTX

Este microservicio ha sido dockerizado siguiendo el patrón de **TICRENGIFO** para la gestión de modelos y contenedores Docker.

## 📋 Características

- ✅ **Descarga automática de modelos** durante el build de Docker
- ✅ **Soporte para CPU y GPU** con Dockerfiles separados
- ✅ **Modelos pre-descargados** en la imagen (no requiere internet en runtime)
- ✅ **Docker Compose** para fácil despliegue
- ✅ **Volúmenes mapeados** para outputs y datos

## 🚀 Inicio Rápido

### 1. Configurar Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto:

```env
# Token de Hugging Face (OBLIGATORIO para build)
HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxx

# Repositorios de modelos
IDEA_MODEL_REPO=tu_organizacion/modelo-ideas
TITLE_BASE_MODEL=google-t5/t5-large
TITLE_ADAPTER_REPO=tu_organizacion/adaptador-titulos

# API Key de DeepL (para traducción)
DEEPL_API_KEY=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

### 2. Construir y Levantar (CPU)

```bash
docker-compose build
docker-compose up -d
```

### 3. Construir y Levantar (GPU)

```bash
docker-compose -f docker-compose.gpu.yml build
docker-compose -f docker-compose.gpu.yml up -d
```

### 4. Verificar el Servicio

```bash
curl http://localhost:8002/health
```

## 📁 Estructura de Archivos Docker

```
Generator_pptx/
├── Dockerfile              # Build para CPU
├── Dockerfile.gpu          # Build para GPU
├── docker-compose.yml      # Orquestación CPU
├── docker-compose.gpu.yml  # Orquestación GPU
└── .env                    # Variables de entorno (crear manualmente)
```

## 🔧 Configuración Detallada

### Modelos Descargados en Build

Los siguientes modelos se descargan automáticamente durante el build:

1. **IDEA_MODEL_REPO**: Modelo completo para generación de ideas
   - Se guarda en: `/app/models/idea_model`
   
2. **TITLE_ADAPTER_REPO**: Adaptador LoRA para generación de títulos
   - Se guarda en: `/app/models/title_adapter`
   
3. **TITLE_BASE_MODEL**: Modelo base T5 (se descarga en runtime desde cache de HuggingFace)

### Volúmenes Mapeados

- `./app:/app/app` - Código fuente (desarrollo)
- `./pipeline:/app/pipeline` - Pipeline de procesamiento
- `./tmp:/app/tmp` - Archivos temporales
- `./outputs:/app/outputs` - Presentaciones generadas
- `./data:/app/data` - Datos adicionales
- `./data/hf_cache:/root/.cache/huggingface` - Cache de HuggingFace (solo GPU)

## 🏗️ Arquitectura

### Dockerfile CPU

- Base: `python:3.9-slim`
- PyTorch: Versión CPU (sin CUDA)
- Modelos: Descargados durante build
- Uso: Desarrollo y producción sin GPU

### Dockerfile GPU

- Base: `pytorch/pytorch:2.2.2-cuda12.1-cudnn8-runtime`
- PyTorch: Con soporte CUDA
- Modelos: Descargados durante build
- Uso: Producción con GPU para mejor rendimiento

## 📊 Comparación CPU vs GPU

| Aspecto | CPU | GPU |
|---------|-----|-----|
| **Tiempo de inferencia** | 30-60s por slide | 5-10s por slide |
| **Memoria RAM** | ~4GB | ~6GB |
| **Memoria GPU** | N/A | ~4GB |
| **Uso recomendado** | Desarrollo, pruebas | Producción |

## 🐛 Solución de Problemas

### Error: "HF_TOKEN is not set"

Asegúrate de tener el archivo `.env` con el token:

```bash
echo "HF_TOKEN=tu_token_aqui" > .env
```

### Error: "modelo no encontrado"

Los modelos no se descargaron durante el build:

```bash
# Reconstruir sin cache
docker-compose build --no-cache
```

### Error: "CUDA out of memory" (GPU)

Reduce el batch size o usa CPU:

```bash
docker-compose down
docker-compose up -d  # Usa CPU
```

### Servicio lento en primera request

Los modelos se cargan bajo demanda. La primera request puede tardar 30-60 segundos mientras se cargan los modelos en memoria.

## 📝 Comandos Útiles

### Ver logs

```bash
# CPU
docker-compose logs -f generator-pptx-cpu

# GPU
docker-compose -f docker-compose.gpu.yml logs -f generator-pptx-gpu
```

### Reconstruir imagen

```bash
# CPU
docker-compose build --no-cache

# GPU
docker-compose -f docker-compose.gpu.yml build --no-cache
```

### Detener servicios

```bash
# CPU
docker-compose down

# GPU
docker-compose -f docker-compose.gpu.yml down
```

### Acceder al contenedor

```bash
# CPU
docker exec -it generator-pptx-cpu bash

# GPU
docker exec -it generator-pptx-gpu bash
```

## 🔄 Actualizar Modelos

Si necesitas actualizar los modelos:

1. Actualiza las variables en `.env`
2. Reconstruye la imagen:
   ```bash
   docker-compose build --no-cache
   ```
3. Reinicia el servicio:
   ```bash
   docker-compose up -d
   ```

## 📚 Referencias

- Patrón de referencia: `TICRENGIFO/`
- Documentación Docker: https://docs.docker.com/
- HuggingFace CLI: https://huggingface.co/docs/huggingface_hub/guides/cli

---

**Última actualización**: 2026-01-14  
**Versión**: 1.0.0
