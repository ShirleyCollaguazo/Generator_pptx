# ==========================================
# DOCKERFILE VERSIÓN CPU (Liviano)
# ==========================================
FROM python:3.9-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Dependencias del sistema (git y curl para descargas)
RUN apt-get update && apt-get install -y git curl && rm -rf /var/lib/apt/lists/*

# 1. Instalamos PyTorch versión CPU (Específico para que no baje CUDA)
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# 2. Instalamos requerimientos y CLI de HuggingFace
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && pip install "huggingface_hub[cli]"

# ============================================================
# ⬇️ DESCARGA DE MODELOS (IGUAL QUE EN GPU)
# ============================================================
ARG HF_TOKEN
ENV HF_TOKEN=${HF_TOKEN}

ARG IDEA_MODEL_REPO
ARG TITLE_BASE_MODEL
ARG TITLE_ADAPTER_REPO

ENV IDEA_MODEL_REPO=${IDEA_MODEL_REPO}
ENV TITLE_BASE_MODEL=${TITLE_BASE_MODEL}
ENV TITLE_ADAPTER_REPO=${TITLE_ADAPTER_REPO}

# --- 1. IDEA MODEL (Modelo completo) ---
RUN mkdir -p /app/models/idea_model
RUN echo "Descargando Idea Model (${IDEA_MODEL_REPO})..." && \
    huggingface-cli download ${IDEA_MODEL_REPO} \
    --token ${HF_TOKEN} \
    --local-dir /app/models/idea_model \
    --local-dir-use-symlinks False

# [DEBUG] Listamos la carpeta para verificar descarga
RUN echo "CONTENIDO DE idea_model:" && ls -la /app/models/idea_model

# --- 2. TITLE ADAPTER (Adaptador LoRA) ---
RUN mkdir -p /app/models/title_adapter
RUN echo "Descargando Title Adapter (${TITLE_ADAPTER_REPO})..." && \
    huggingface-cli download ${TITLE_ADAPTER_REPO} \
    --token ${HF_TOKEN} \
    --local-dir /app/models/title_adapter \
    --local-dir-use-symlinks False

# [DEBUG] Listamos la carpeta para verificar descarga
RUN echo "CONTENIDO DE title_adapter:" && ls -la /app/models/title_adapter

# Nota: El modelo base T5 (TITLE_BASE_MODEL) se descargará automáticamente
# en runtime desde HuggingFace cache si no está disponible localmente

# ============================================================

# Copiamos el código fuente
COPY ./app /app/app
COPY ./pipeline /app/pipeline
COPY ./assets /app/assets

# Creamos los directorios necesarios
RUN mkdir -p /app/tmp /app/outputs /app/data

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
