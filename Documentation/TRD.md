# **Technical Requirements Document (TRD)**
# **CLEARLY — Sistema Omnicanal de Accesibilidad Comunitaria Local-First**

| Metadato | Detalle |
| :--- | :--- |
| **Documento** | Technical Requirements & Architecture Document (TRD) |
| **Versión** | 1.0.0 |
| **Estado** | Aprobado para Implementación Técnica (Ready for Engineering) |
| **Lead Architect** | Antigravity AI Systems |
| **Stack Principal** | FastAPI, vLLM, Ollama, PostgreSQL + pgvector, MinIO, Evolution API, Next.js, React Native |
| **Documentos Base** | [PRD.md](file:///d:/IA-PROJECTS/app-clearly/Documentation/PRD.md), [CLEARLY.md](file:///d:/IA-PROJECTS/app-clearly/Documentation/CLEARLY.md) |
| **Fecha de Publicación** | Noviembre 2026 |

---

## **1. Resumen Técnico y Principios Arquitectónicos**

### **1.1 Alcance del Documento**
Este documento define la arquitectura de software, especificaciones de microservicios, contratos de API, modelos de datos relacionales y vectoriales, topología de despliegue en contenedores Docker y protocolos de seguridad para el ecosistema **CLEARLY**.

### **1.2 Principios de Ingeniería (Core Architectural Tenets)**
1. **Local-First & Cero Dependencia Comercial:** Inferencia de modelos fundacionales (LLM, OCR, STT, TTS) ejecutada en servidores locales o nodos dedicados autohospedados, eliminando costos variables por token o petición y asegurando privacidad absoluta de datos médicos y migratorios (conforme a PIPEDA y GDPR).
2. **Desacoplamiento Modular Asíncrono:** Tareas intensivas en cómputo (OCR, transcripción de audio, ingesta y reescritura de eventos) desacopladas mediante colas de mensajes **Redis + Celery/BullMQ**, manteniendo la latencia de la API síncrona < 200ms.
3. **Accesibilidad Nativa (WCAG 2.1 AAA & Atkinson Hyperlegible):** Contratos de datos estructurados para lectura asistida por voz, semántica ARIA estricta y soporte para renderizado adaptativo.
4. **Soberanía y Cifrado en Reposo:** Archivos binarios (documentos escaneados y notas de voz) almacenados en **MinIO** con cifrado del lado del servidor (AES-256) y referencias UUID desvinculadas de metadatos identificables.

---

## **2. Arquitectura Global del Sistema (Diagrama C4 Nivel 2: Contenedores)**

```mermaid
flowchart TD
    subgraph Clientes["Clientes & Canales de Entrada"]
        WA["Usuario WhatsApp (Voz/Texto/Foto)"]
        WEB["App Web Accesible (Next.js 14)"]
        MOB["App Móvil Titular & Tutor (React Native)"]
        EXP["Portal Web de Expertos Premium"]
    end

    subgraph Gateways["Capa de Enrutamiento & Ingesta"]
        EVO["Evolution API (Gateway WhatsApp Autohospedado)"]
        REV["Reverse Proxy & SSL Termination (Traefik / Nginx)"]
    end

    subgraph BackendCore["Plataforma Backend (FastAPI / Python 3.11)"]
        API["FastAPI Core Gateway"]
        AUTH["Auth & Session Service (JWT + RLS)"]
        TUTOR_SVC["Tutor Engine (WebSockets / Handshake)"]
        DOC_SVC["Document Pipeline Orchestrator"]
        EVT_SVC["Community Events Ingestor & API"]
        PREM_SVC["Premium Matching & Booking Engine"]
    end

    subgraph WorkerLayer["Capa de Tareas Asíncronas & IA Local"]
        REDIS["Redis 7 (Broker de Colas & Cache)"]
        CELERY["Workers Asíncronos Celery"]
        
        subgraph AIServer["Servidor de Inferencia Local (GPU / vLLM / Ollama)"]
            VLLM["vLLM / Ollama Server: Llama 3.1 8B / Llama 3.2 3B"]
            OCR_SRV["PaddleOCR + Surya OCR Service (FastAPI Microservice)"]
            STT_SRV["faster-whisper Service (Audio -> Texto)"]
            TTS_SRV["Piper TTS Engine (Texto -> Audio WAV/Opus)"]
            EMBED_SRV["BGE-M3 Embedding Microservice"]
        end
    end

    subgraph DataStorage["Capa de Persistencia & Almacenamiento"]
        PG["PostgreSQL 16 + pgvector (Base Relacional & RAG)"]
        MINIO["MinIO S3-Compatible (Docs cifrados & Audios)"]
    end

    subgraph External["Servicios Externos Restringidos"]
        STRIPE["Stripe Connect API (Pagos & Escrow)"]
        LIVKIT["LiveKit Server (WebRTC Open Source para Video)"]
    end

    WA <--> EVO
    EVO <--> REV
    WEB & MOB & EXP <--> REV
    REV <--> API

    API --> AUTH
    API --> TUTOR_SVC
    API --> DOC_SVC
    API --> EVT_SVC
    API --> PREM_SVC

    DOC_SVC & EVT_SVC --> REDIS
    REDIS --> CELERY
    CELERY --> AIServer

    DOC_SVC <--> MINIO
    API <--> PG
    AIServer <--> PG
    PREM_SVC <--> STRIPE
    PREM_SVC <--> LIVKIT
```

---

## **3. Especificaciones de Microservicios y Componentes**

### **3.1 Servicio 1: Gateway de WhatsApp & Orquestador de Mensajería**
* **Tecnología:** **Evolution API v2** (Node.js/TypeScript) desplegado en contenedor Docker local con conexión vía WebSocket / Puppeteer Engine a WhatsApp Web.
* **Webhook de Entrada (`/api/v1/webhooks/whatsapp`):**
  * Recepción de eventos: `messages.upsert` (texto, audio, imagen, ubicación).
  * Payload de audio recibido como archivo Opus/OGG codificado en Base64 o URL local.
* **Flujo de Ejecución de Notas de Voz:**
  1. El usuario envía nota de voz.
  2. Evolution API descarga el buffer de audio y lo envía al worker de **faster-whisper**.
  3. `faster-whisper` transcribe a texto (`beam_size=5`, lenguaje auto-detectado).
  4. El texto se envía al modelo **Llama 3.2 3B** con prompt de clasificación de intención (Consulta básica, evento, o documento).
  5. Se formula la respuesta y se genera el audio de salida con **Piper TTS** (Voz en español de baja latencia `es_ES-davefx-medium`).
  6. Evolution API envía mensaje de texto y nota de voz de vuelta al chat del usuario.

### **3.2 Servicio 2: Pipeline de OCR y Análisis Documental (Plain Language Engine)**
* **Tecnología:** **PaddleOCR (PP-OCRv4)** para extracción geométrica de texto + **Llama 3.1 8B Instruct** servido en **vLLM** con cuantización AWQ (4-bit) o GGUF.
* **Pipeline de Procesamiento:**
  ```
  [Foto / PDF] 
     ──> Normalización de Imagen (OpenCV: Deskew, Binarización, Contraste)
     ──> PaddleOCR (Detección de polígonos de texto + Reconocimiento OCR)
     ──> Extracción de Bloques Estructurados (Título, Fecha de emisión, Plazo, Requisitos)
     ──> Llama 3.1 8B Prompt (Plain Language Translation + Structured JSON Output)
     ──> Validación Pydantic del JSON
     ──> Almacenamiento en DB + Trigger de Alerta al Tutor (si plazo < 15 días)
  ```
* **Esquema de Salida Pydantic (`DocumentAnalysisResult`):**
  ```python
  from pydantic import BaseModel, Field
  from typing import List, Optional
  from datetime import date

  class ActionItem(BaseModel):
      task: str = Field(description="Acción concreta en lenguaje sencillo")
      required_document: Optional[str] = Field(None, description="Documento necesario")
      deadline: Optional[date] = Field(None, description="Fecha límite inferida")
      is_mandatory: bool = True

  class DocumentAnalysisResult(BaseModel):
      document_type: str = Field(description="Ej: Carta Gubernamental, Notificación Médica")
      plain_summary: str = Field(description="Explicación en Plain Language de 2-3 oraciones")
      detected_language: str
      issuing_entity: str
      critical_deadline: Optional[date] = Field(None, description="Fecha límite más urgente")
      actions_required: List[ActionItem]
      ambiguities_flagged: List[str] = Field(description="Puntos no claros en el documento original")
      recommended_questions: List[str] = Field(description="Preguntas a realizar a la entidad")
      escalate_to_premium: bool = Field(False, description="True si requiere asesoría legal/social humana")
  ```

### **3.3 Servicio 3: Ingestor de Eventos y Motor 'Made Clear'**
* **Scrapers Asíncronos:** Utilizan **Playwright (Python headless)** y conectores de API pública para extraer eventos de Eventbrite y Luma.
* **Filtro de Deduplicación y Hash:** Función SHA-256 calculada sobre `(title_normalized + start_time + venue_coords)` para evitar duplicidad entre plataformas.
* **Transformación Automática:** Inferencia por lotes en **Llama 3.1 8B** para transformar la descripción original en las 4 preguntas canónicas (*¿Qué es?*, *¿Cuándo/Dónde?*, *¿Costo?*, *¿Cómo registrarse?*).
* **Indexación Vectorial:** El resumen transformado se vectoriza con **BGE-M3** (1024 dimensiones) y se indexa en la tabla `events` mediante **HNSW** (`vector_cosine_ops`) en PostgreSQL.

### **3.4 Servicio 4: Módulo de Tutoría y Sincronización en Tiempo Real**
* **Protocolo:** WebSockets seguros (`wss://api.clearly.app/ws/tutor/{tutor_id}`) administrados mediante **Redis Pub/Sub**.
* **Gestión de Alertas:**
  * Alertas Críticas (Vencimiento < 72h o acción urgente): Despachadas simultáneamente por WebSocket, Push Notification (FCM) y mensaje directo al WhatsApp del tutor vía Evolution API.
  * Sincronización de Checklist: Eventos `CHECKLIST_ITEM_TOGGLED` emitidos en tiempo real para reflejarse instantáneamente en la pantalla del adulto mayor y del tutor.

### **3.5 Servicio 5: CLEARLY Premium & Servidor WebRTC Local**
* **Servidor de Videollamadas:** Instancia autohospedada de **LiveKit** (Go/WebRTC). Cero dependencia de Twilio Video o Zoom SDK.
* **Flujo de Pago:** **Stripe Connect Custom/Express**. Al solicitar el servicio, se realiza una retención de fondos (`PaymentIntent` con `capture_method='manual'`). Una vez terminada la sesión y firmada la conformidad del usuario/tutor, se ejecuta la captura y el split de comisiones (85% profesional, 15% CLEARLY).

---

## **4. Diseño de Base de Datos y Esquema DDL (PostgreSQL 16 + pgvector)**

```sql
-- 1. Extensiones necesarias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "vector";

-- 2. Enumeraciones del Sistema
CREATE TYPE user_role AS ENUM ('senior', 'tutor', 'expert', 'admin');
CREATE TYPE doc_urgency AS ENUM ('low', 'medium', 'high', 'critical');
CREATE TYPE event_source AS ENUM ('eventbrite', 'luma', 'civic_library', 'manual');
CREATE TYPE booking_status AS ENUM ('pending', 'confirmed', 'in_progress', 'completed', 'disputed', 'cancelled');
CREATE TYPE service_modality AS ENUM ('virtual', 'in_person');

-- 3. Tabla de Usuarios
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    phone_number VARCHAR(20) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE,
    full_name VARCHAR(150),
    role user_role NOT NULL DEFAULT 'senior',
    preferred_language VARCHAR(10) NOT NULL DEFAULT 'es',
    accessibility_settings JSONB DEFAULT '{
        "font_scale": 1.25,
        "high_contrast": false,
        "audio_speed": 1.0,
        "auto_read_aloud": true
    }'::jsonb,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 4. Tabla de Vínculos de Tutoría (Consentimiento Granular)
CREATE TABLE tutor_relationships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    senior_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    tutor_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    pairing_code_hash VARCHAR(128),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    permissions JSONB NOT NULL DEFAULT '{
        "can_view_critical_alerts": true,
        "can_view_documents": true,
        "can_view_events": true,
        "can_hire_experts": true
    }'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    revoked_at TIMESTAMPTZ,
    CONSTRAINT unique_senior_tutor_pair UNIQUE(senior_id, tutor_id)
);

-- 5. Tabla de Documentos Procesados
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    storage_path VARCHAR(512) NOT NULL, -- Ruta en MinIO S3
    file_sha256 VARCHAR(64) NOT NULL,
    original_extracted_text TEXT,
    plain_summary TEXT NOT NULL,
    issuing_entity VARCHAR(200),
    urgency doc_urgency NOT NULL DEFAULT 'medium',
    critical_deadline DATE,
    ambiguities JSONB DEFAULT '[]'::jsonb,
    recommended_questions JSONB DEFAULT '[]'::jsonb,
    requires_human_expert BOOLEAN NOT NULL DEFAULT FALSE,
    embedding vector(1024), -- Embeddings BGE-M3
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 6. Tabla de Checklists y Acciones Documentales
CREATE TABLE document_actions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    task_description TEXT NOT NULL,
    required_document VARCHAR(255),
    deadline DATE,
    is_completed BOOLEAN NOT NULL DEFAULT FALSE,
    completed_by_user_id UUID REFERENCES users(id),
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 7. Tabla del Marketplace de Eventos Comunitarios
CREATE TABLE community_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    external_id VARCHAR(255),
    source event_source NOT NULL,
    raw_title VARCHAR(300) NOT NULL,
    made_clear_what TEXT NOT NULL,
    made_clear_when_where TEXT NOT NULL,
    made_clear_cost TEXT NOT NULL,
    made_clear_how_to_register TEXT NOT NULL,
    event_url VARCHAR(512),
    start_time TIMESTAMPTZ NOT NULL,
    end_time TIMESTAMPTZ,
    venue_name VARCHAR(255),
    venue_address TEXT,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    is_wheelchair_accessible BOOLEAN NOT NULL DEFAULT TRUE,
    is_senior_friendly BOOLEAN NOT NULL DEFAULT TRUE,
    is_free BOOLEAN NOT NULL DEFAULT TRUE,
    supported_languages VARCHAR(5)[] DEFAULT ARRAY['es', 'en'],
    embedding vector(1024), -- Embeddings BGE-M3 para búsqueda semántica
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 8. Tabla de Profesionales Verificados (CLEARLY Premium)
CREATE TABLE expert_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    specialty VARCHAR(100) NOT NULL, -- ej: 'Immigration Consultant', 'Social Worker', 'Health Navigator'
    license_number VARCHAR(100) NOT NULL,
    id_verification_status VARCHAR(50) NOT NULL DEFAULT 'verified',
    hourly_rate_cents INTEGER NOT NULL DEFAULT 4500, -- ej: $45.00 USD
    bio_plain_text TEXT NOT NULL,
    languages_spoken VARCHAR(5)[] NOT NULL,
    service_modalities service_modality[] NOT NULL DEFAULT ARRAY['virtual'::service_modality],
    average_rating NUMERIC(3, 2) DEFAULT 5.00,
    total_reviews INTEGER NOT NULL DEFAULT 0,
    is_available BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 9. Tabla de Contrataciones Premium (Bookings con Escrow)
CREATE TABLE premium_bookings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_senior_id UUID NOT NULL REFERENCES users(id),
    requested_by_user_id UUID NOT NULL REFERENCES users(id), -- Puede ser el senior o el tutor
    expert_id UUID NOT NULL REFERENCES expert_profiles(id),
    document_id UUID REFERENCES documents(id), -- Expediente previo asociado
    modality service_modality NOT NULL,
    scheduled_start TIMESTAMPTZ NOT NULL,
    scheduled_end TIMESTAMPTZ NOT NULL,
    livekit_room_name VARCHAR(128),
    status booking_status NOT NULL DEFAULT 'pending',
    stripe_payment_intent_id VARCHAR(255),
    amount_cents INTEGER NOT NULL,
    expert_payout_cents INTEGER NOT NULL,
    client_review_rating SMALLINT CHECK (client_review_rating BETWEEN 1 AND 5),
    client_review_text TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 10. Índices de Alto Rendimiento y Búsqueda Vectorial HNSW
CREATE INDEX idx_docs_user ON documents(user_id);
CREATE INDEX idx_docs_deadline ON documents(critical_deadline) WHERE critical_deadline IS NOT NULL;
CREATE INDEX idx_docs_embedding ON documents USING hnsw (embedding vector_cosine_ops);
CREATE INDEX idx_events_start ON community_events(start_time);
CREATE INDEX idx_events_embedding ON community_events USING hnsw (embedding vector_cosine_ops);
CREATE INDEX idx_tutor_active ON tutor_relationships(senior_id, tutor_id) WHERE is_active = TRUE;
```

---

## **5. Especificaciones de APIs RESTful (Contratos OpenAPI)**

### **5.1 Ingesta de Documentos (`POST /api/v1/documents/process`)**
* **Headers:** `Authorization: Bearer <jwt>`, `Content-Type: multipart/form-data`
* **Request Body:**
  * `file`: Archivo binario (PDF, JPEG, PNG, máx. 25MB).
  * `target_language`: Código ISO (ej. `"es"`, `"pa"`).
* **Response (HTTP 202 Accepted — Procesamiento Asíncrono):**
  ```json
  {
    "task_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
    "status": "processing",
    "estimated_seconds": 4.5,
    "websocket_channel": "wss://api.clearly.app/ws/tasks/9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d"
  }
  ```

### **5.2 Consulta Semántica de Eventos (`GET /api/v1/events/search`)**
* **Query Params:**
  * `q`: Texto de búsqueda en lenguaje natural (ej. `"clases de yoga gratis para jubilados"`).
  * `lat`, `lon`: Coordenadas geográficas.
  * `radius_km`: Radio en kilómetros (default `10`).
  * `only_free`: Booleano (default `true`).
* **Response (HTTP 200 OK):**
  ```json
  {
    "total": 3,
    "events": [
      {
        "id": "e4eaaaf2-d142-11e1-b3dd-0001a919326a",
        "title": "Taller de Bienestar y Yoga Suave",
        "what": "Clase grupal de estiramiento y relajación adaptada para personas mayores de 60 años.",
        "when_where": "Sábado 15 de Noviembre, 2:00 PM a 3:30 PM en Centro Comunitario Downtown (Parada de autobús ruta 14 frente a la entrada).",
        "cost": "GRATUITO (No requiere pago).",
        "how_to_register": "Haz clic en 'Reservar Asistido' o muestra este código en la entrada.",
        "is_wheelchair_accessible": true,
        "audio_summary_url": "https://api.clearly.app/v1/audio/events/e4eaaaf2.opus"
      }
    ]
  }
  ```

### **5.3 Asociación de Tutor (`POST /api/v1/tutors/pair`)**
* **Request Body:**
  ```json
  {
    "pairing_code": "849201"
  }
  ```
* **Response (HTTP 200 OK):**
  ```json
  {
    "status": "paired",
    "relationship_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "senior_profile": {
      "full_name": "Rosa Gómez",
      "preferred_language": "es"
    },
    "granted_permissions": {
      "can_view_critical_alerts": true,
      "can_view_documents": true,
      "can_view_events": true
    }
  }
  ```

---

## **6. Topología de Infraestructura y Despliegue (Docker Compose)**

```yaml
version: '3.8'

services:
  # 1. Reverse Proxy & SSL
  traefik:
    image: traefik:v3.0
    restart: always
    command:
      - "--providers.docker=true"
      - "--entrypoints.web.address=:80"
      - "--entrypoints.websecure.address=:443"
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - ./certs:/etc/traefik/certs

  # 2. Base de Datos Soberana (PostgreSQL + pgvector)
  postgres:
    image: pgvector/pgvector:pg16
    restart: always
    environment:
      POSTGRES_DB: clearly_db
      POSTGRES_USER: clearly_admin
      POSTGRES_PASSWORD: ${DB_STRONG_PASSWORD}
    volumes:
      - pgdata:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"

  # 3. Almacenamiento de Objetos Cifrado (MinIO)
  minio:
    image: minio/minio:RELEASE.2024-05-10T01-41-38Z
    restart: always
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: ${MINIO_ROOT_USER}
      MINIO_ROOT_PASSWORD: ${MINIO_ROOT_PASSWORD}
    volumes:
      - miniodata:/data
    ports:
      - "9000:9000"

  # 4. Broker de Mensajes y Caché
  redis:
    image: redis:7-alpine
    restart: always
    volumes:
      - redisdata:/data

  # 5. Gateway de WhatsApp (Evolution API)
  evolution-api:
    image: atendai/evolution-api:v2.0.0
    restart: always
    environment:
      SERVER_URL: "https://wa.clearly.local"
      DATABASE_ENABLED: "true"
      DATABASE_CONNECTION_URI: "postgresql://clearly_admin:${DB_STRONG_PASSWORD}@postgres:5432/clearly_db"
      AUTHENTICATION_API_KEY: ${EVOLUTION_API_KEY}
    depends_on:
      - postgres
      - redis

  # 6. Servidor de Inferencia LLM Local (vLLM en GPU)
  vllm-engine:
    image: vllm/vllm-openai:latest
    restart: always
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    command: >
      --model meta-llama/Meta-Llama-3.1-8B-Instruct
      --quantization awq
      --dtype float16
      --max-model-len 8192
      --gpu-memory-utilization 0.85
      --port 8000
    volumes:
      - ~/.cache/huggingface:/root/.cache/huggingface
    ports:
      - "8000:8000"

  # 7. Microservicio de Visión & OCR Local (PaddleOCR)
  ocr-service:
    build: ./services/ocr_service
    restart: always
    ports:
      - "8001:8001"
    environment:
      USE_GPU: "true"

  # 8. Microservicio de Voz (faster-whisper + Piper TTS)
  audio-service:
    build: ./services/audio_service
    restart: always
    ports:
      - "8002:8002"

  # 9. Backend Core API (FastAPI)
  backend-api:
    build: ./Backend
    restart: always
    environment:
      DATABASE_URL: "postgresql+asyncpg://clearly_admin:${DB_STRONG_PASSWORD}@postgres:5432/clearly_db"
      REDIS_URL: "redis://redis:6379/0"
      MINIO_ENDPOINT: "minio:9000"
      VLLM_ENDPOINT: "http://vllm-engine:8000/v1"
      OCR_ENDPOINT: "http://ocr-service:8001"
      AUDIO_ENDPOINT: "http://audio-service:8002"
    depends_on:
      - postgres
      - redis
      - minio

volumes:
  pgdata:
  miniodata:
  redisdata:
```

---

## **7. Estructura de Directorios del Repositorio**

```
app-clearly/
├── Backend/                       # Core FastAPI & Microservicios
│   ├── app/
│   │   ├── api/                   # Controladores REST & WebSockets
│   │   │   ├── v1/
│   │   │   │   ├── documents.py
│   │   │   │   ├── events.py
│   │   │   │   ├── tutors.py
│   │   │   │   ├── premium.py
│   │   │   │   └── webhooks.py    # Evolution API / WhatsApp Receiver
│   │   ├── core/                  # Seguridad, Configuración y Logger
│   │   ├── db/                    # Modelos SQLAlchemy & Migraciones Alembic
│   │   ├── schemas/               # Modelos Pydantic (Entrada/Salida)
│   │   └── services/              # Lógica de Negocio
│   │       ├── document_pipeline.py
│   │       ├── event_ingestion.py
│   │       ├── tutor_notifier.py
│   │       └── livekit_manager.py
│   ├── Dockerfile
│   └── requirements.txt
├── Database/                      # Esquemas SQL, Migraciones & Seeds
│   ├── init.sql
│   └── migrations/
├── Documentation/                 # Documentación Oficial
│   ├── CLEARLY.md                 # Propuesta y Manifiesto de Marca
│   ├── PRD.md                     # Documento de Requerimientos de Producto
│   ├── TRD.md                     # Este Documento de Requerimientos Técnicos
│   └── clearly_brand_book.pdf     # Guía Oficial de Marca
├── Frontend/                      # Aplicaciones de Usuario
│   ├── web-app/                   # Next.js 14 (Web Accesible WCAG AAA)
│   └── mobile-app/                # React Native / Expo (Senior & Tutor Hub)
├── RAG/                           # Pipelines de IA, Prompts & Scripts Locales
│   ├── models/                    # Configuraciones de vLLM / Ollama
│   ├── prompts/                   # Prompts de Plain Language & Triage
│   ├── ocr_engine/                # Wrappers PaddleOCR & Surya
│   └── audio_engine/              # faster-whisper & Piper TTS scripts
└── docker-compose.yml             # Orquestación del Stack Local-First
```

---

## **8. Criterios de Rendimiento, Seguridad y Aceptación Técnica**

1. **Benchmark de Latencia:**
   * Transcripción de audio de WhatsApp (15 segundos de voz): < 850ms en CPU / < 250ms en GPU.
   * Generación de audio de respuesta con Piper TTS: < 150ms.
   * Extracción OCR y traducción a Plain Language de carta oficial (2 páginas): < 4.2 segundos.
2. **Pruebas de Accesibilidad Automatizadas:**
   * Auditoría de accesibilidad con `@axe-core/playwright` en CI/CD: 0 violaciones en normas WCAG 2.1 Nivel AAA.
3. **Cero Retención de Datos Externos:**
   * Verificación de tráfico saliente en firewall (*Egress Monitor*): Confirmación de que ningún byte de texto de documentos escaneados sale fuera de la subred local de CLEARLY.

---

## **9. Aprobaciones y Control de Cambios**

| Rol Técnico | Nombre | Estado | Fecha |
| :--- | :--- | :--- | :--- |
| **Lead Systems Architect** | Antigravity AI Systems | Aprobado | 12 de Noviembre, 2026 |
| **Principal Software Engineer** | Core Engineering Team | Aprobado | 12 de Noviembre, 2026 |
| **Security & Privacy Officer** | Local-First Compliance Board | Aprobado | 12 de Noviembre, 2026 |

---
