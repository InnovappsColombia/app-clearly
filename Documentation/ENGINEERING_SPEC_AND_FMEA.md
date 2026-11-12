# **CLEARLY — Especificación Técnica de Ingeniería de Misión Crítica y FMEA**
## **Arquitectura Local-First, Accesibilidad Gerontológica (A11y) y Mitigación de Fallos**

| Metadato | Detalle Técnico |
| :--- | :--- |
| **Documento** | Deep Engineering Specification & FMEA (Failure Mode and Effects Analysis) |
| **Versión** | 1.0.0-PROD-SPEC |
| **Rol Responsable** | Principal AI Systems Architect & Staff Geriatric Accessibility Designer |
| **Clasificación de Seguridad** | Alta Disponibilidad, Privacidad Soberana (PIPEDA / GDPR / AODA) |
| **Target Hardware** | 1x NVIDIA RTX 3090 / 4090 (24,576 MiB VRAM) Dedicated Node |
| **Documentos Base** | [PRD.md](file:///d:/IA-PROJECTS/app-clearly/Documentation/PRD.md), [TRD.md](file:///d:/IA-PROJECTS/app-clearly/Documentation/TRD.md) |
| **Fecha de Publicación** | Noviembre 2026 |

---

# **1. MATRIZ DE ANÁLISIS DE MODOS DE FALLO Y EFECTOS (FMEA)**

La metodología FMEA cuantifica el riesgo mediante el Índice de Prioridad de Riesgo (*Risk Priority Number*):
$$\text{RPN} = \text{Severidad (S)} \times \text{Ocurrencia (O)} \times \text{Detección (D)}$$
Donde cada variable se evalúa en una escala de 1 a 10. Las acciones correctivas son obligatorias para cualquier RPN > 100 o cuando la Severidad sea $\ge 9$ (riesgo legal, migratorio o de salud).

### **1.1 Matriz Cuantitativa FMEA para los 5 Servicios Core**

| ID | Modo de Fallo | Causa Raíz | Efecto en el Usuario | S | O | D | RPN Inicial | Mitigación de Ingeniería Implementada | S_rev | O_rev | D_rev | RPN Final |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **FM-01** | OCR omite o invierte negación (*"no renovable"* $\rightarrow$ *"renovable"*). | Doblez en papel, tinta tenue, artefacto de compresión JPEG. | El usuario asume que su estatus migratorio o subsidio continúa; cae en ilegalidad o deuda. | **10** | 4 | 5 | **200** | **Dual-Engine Agreement Pass** (PaddleOCR + Surya OCR) con verificación cruzada obligatoria en frases negativas y anclaje morfológico de términos críticos. | 10 | 1 | 2 | **20** |
| **FM-02** | Alucinación de fecha límite por aritmética temporal del LLM. | El documento dice *"14 días tras la fecha del matasellos (30 Oct)"*; el LLM infiere 15 Nov por error de cálculo. | Plazo legal vencido; pérdida irrevocable de derecho a apelar ante tribunales (ej. LTB, IRCC). | **10** | 5 | 4 | **200** | **Motor de Inferencia Temporal Determinista:** El LLM tiene prohibido calcular fechas. Solo extrae la fecha base y el operador ($+14\text{d}$); una librería AST determinista (`python-dateutil`) calcula la fecha final. | 10 | 1 | 1 | **10** |
| **FM-03** | Silero VAD corta prematuramente nota de voz de anciano. | Pausa respiratoria o dubitativa de 4 a 6 segundos; disartria o temblor vocal senil. | El bot transcribe una frase incompleta (ej. *"Quiero saber si..."*) y emite una respuesta inútil o errada. | **7** | 8 | 3 | **168** | **VAD Gerontológico Calibrado:** `min_silence_duration_ms=4500`, `threshold=0.30`, búfer de pre-roll de 600ms y detector de entonación inconclusa. | 7 | 2 | 2 | **28** |
| **FM-04** | Coerción o abuso patrimonial del Tutor sobre el Adulto Mayor. | El hijo tutor obtiene control del checklist y usa la información para presionar financieramente al padre. | Pérdida de autonomía del adulto mayor, despojo de pensiones o subsidios sin su consentimiento. | **9** | 3 | 7 | **189** | **Asimetría Criptográfica de Capacidades:** El tutor tiene acceso de solo lectura (*read-only*). Mecanismo de **Duress PIN** (Código de coacción silenciosa) que desvincula alertas sin notificar al tutor. | 9 | 1 | 2 | **18** |
| **FM-05** | Baneo masivo de IP/Número en Gateway WhatsApp (Evolution API). | Detección de patrones de bot por Meta ante ráfagas de mensajes salientes sin consentimiento explícito. | Pérdida total del canal de comunicación para todos los usuarios que no tienen la App instalada. | **9** | 6 | 4 | **216** | **Pool Rotativo de Instancias + Rate Limiting Token-Bucket:** Intervalos de envío con jitter estocástico (2.5s a 5.0s), balanceo de números y fallback a PWA Push Notifications. | 9 | 1 | 2 | **18** |

---

### **1.2 Delimitación Ontológica y Legal: Frontera contra el Ejercicio No Autorizado de la Abogacía / Medicina**

Bajo la sección 91 de la *Immigration and Refugee Protection Act (IRPA)* de Canadá y los estatutos de los colegios de abogados y médicos, proporcionar consejo o asesoría estratégica sin licencia constituye un delito.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       FRONTERA ONTOLÓGICA DE CLEARLY                        │
│                                                                             │
│   PERMITIDO (Conversión de Accesibilidad)    ESTRICTAMENTE PROHIBIDO (Consejo Legal) │
│  ┌──────────────────────────────────────┐   ┌─────────────────────────────┐ │
│  │ • Reorganizar el texto original.     │   │ • Recomendar estrategias.   │ │
│  │ • Traducir terminología al español.  │   │ • Estimar probabilidades.   │ │
│  │ • Extraer listas de requisitos.      │   │ • Redactar respuestas a     │ │
│  │ • Convertir plazos a fechas fijas.   │   │   entidades judiciales.     │ │
│  │ • Redactar preguntas para el emisor. │   │ • Interpretar intenciones   │ │
│  │ • Citar textualmente el párrafo base.│   │   no explícitas en el texto.│ │
│  └──────────────────────────────────────┘   └─────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### **Implementación del Guardrail de NeMo / Regex Validator en FastAPI:**
```python
import re
from fastapi import HTTPException

PROHIBITED_LEGAL_ADVICE_PATTERNS = [
    r"\b(debe(?:s)?|tiene(?:s)? que) (demandar|apelar|denunciar|declarar)\b",
    r"\b(le conviene|le recomiendo|mi consejo legal es)\b",
    r"\b(este documento significa que ganar[aá]|perder[aá] su caso)\b",
    r"\b(no pague|ignore esta carta)\b",
    r"\b(su diagn[oó]stico m[eé]dico indica)\b"
]

def assert_no_unauthorized_advice(llm_output_text: str) -> None:
    for pattern in PROHIBITED_LEGAL_ADVICE_PATTERNS:
        match = re.search(pattern, llm_output_text, re.IGNORECASE)
        if match:
            raise ValueError(
                f"Violación de Guardrail Legal: Detección de consejo prescriptivo no autorizado ('{match.group(0)}'). "
                f"El motor debe limitarse a la simplificación lingüística objetiva."
            )
```

---

# **2. PROTOCOLO DE VALIDACIÓN Y DATASET DE PRUEBA (EVAL-DRIVEN)**

### **2.1 Métricas Matemáticas de Legibilidad en Español**

Para certificar que una simplificación de carta gubernamental sea comprensible por un adulto mayor con educación básica, el texto procesado por CLEARLY debe someterse a auditoría sintáctica obligatoria previa entrega.

#### **1. Índice Fernández-Huerta (Adaptación oficial de Flesch para el español):**
$$FH = 206.84 - (0.60 \times P) - (1.02 \times F)$$
Donde:
* $P$: Número total de sílabas por cada 100 palabras (densidad silábica).
* $F$: Número de frases/oraciones por cada 100 palabras.

**Criterio de Aceptación:** $FH \ge 80$ (*"Lectura Muy Fácil"*, nivel de 4to a 6to grado escolar). Todo output con $FH < 75$ es rechazado y reescrito por el pipeline de IA.

#### **2. Algoritmo de Auditoría Sintáctica Automatizada en Python:**
```python
import pyphen

dic = pyphen.Pyphen(lang='es')

def calculate_fernandez_huerta(text: str) -> float:
    words = [w.strip(".,;:!?()[]") for w in text.split() if w.strip(".,;:!?()[]")]
    num_words = len(words)
    if num_words == 0:
        return 0.0

    sentences = [s for s in re.split(r'[.!?]+', text) if s.strip()]
    num_sentences = max(1, len(sentences))

    total_syllables = sum(len(dic.inserted(word).split('-')) for word in words)

    p = (total_syllables / num_words) * 100.0
    f = (num_sentences / num_words) * 100.0

    score = 206.84 - (0.60 * p) - (1.02 * f)
    return round(score, 2)
```

---

### **2.2 Framework de Evaluación de RAG & Alucinación (DeepEval / Ragas Pipeline)**

Cada inferencia sobre documentos de usuarios se evalúa con tres métricas automatizadas:

1. **Fidelidad Fáctica (*Faithfulness*):**
   $$S_{\text{faith}} = \frac{|\text{Afirmaciones en Respuesta verificables en el Contexto}|}{|\text{Total de Afirmaciones extraídas de la Respuesta}|}$$
   * **Umbral Crítico:** $S_{\text{faith}} \ge 0.98$. Si es menor, la respuesta se bloquea y se emite la advertencia de documento ambiguo.
2. **Precisión de Extracción de Fechas Críticas (*Deterministic Anchor Matching*):**
   * Comparación de tokens de fecha extraídos contra el Ground Truth mediante expresiones regulares ISO 8601. Tolerancia de error: **0% (cero discrepancias permitidas)**.

---

### **2.3 Especificación del Dataset de Prueba (Gold Standard: 50 Documentos Reales)**

El dataset de validación interna se divide en 4 clústeres de alta vulnerabilidad administrativa:

```
[50 DOCUMENTOS DEL GROUND TRUTH BENCHMARK]
├── CLÚSTER 1: Cartas de Inmigración y Refugio (IRCC / CBSA) [15 Documentos]
│   ├── 5x Solicitudes de Evidencia Adicional (Procedural Fairness Letters - Plazo 30 días).
│   ├── 5x Órdenes de Toma de Biométricos (Plazo 14 días con cita médica).
│   └── 5x Notificaciones de Denegación de Permiso de Trabajo con derecho a revisión judicial (Plazo 15 días).
├── CLÚSTER 2: Vivienda y Desalojo de Adultos Mayores (LTB / Rent Tribunal) [15 Documentos]
│   ├── 7x Formularios N4 (Aviso de Desalojo por Falta de Pago - Plazo de subsanación 14 días).
│   ├── 5x Formularios N12 (Aviso de Desalojo por Uso del Propietario).
│   └── 3x Órdenes de Audiencia en línea con enlaces a Teams / Zoom.
├── CLÚSTER 3: Notificaciones Clínicas y Medicamentos Complejos [10 Documentos]
│   ├── 5x Instrucciones preoperatorias de endoscopía/cirugía (ayuno 12h, suspensión de anticoagulantes).
│   └── 5x Planes de egreso hospitalario con recetas múltiples y citas escalonadas.
└── CLÚSTER 4: Subsidios y Pensiones Públicas (OAS / CPP / CRA) [10 Documentos]
    ├── 5x Auditorías de declaración de ingresos para Suplemento de Renta Baja (GIS).
    └── 5x Notificaciones de pago en exceso con plazo de apelación de 30 días.
```

---

### **2.4 Protocolo de Prueba de Campo Ciega con Adultos Mayores (Human Usability Gate)**

* **Muestra:** $N = 10$ adultos mayores de 68 a 82 años.
* **Criterios de Selección:** Habla nativa española o punjabi, competencia tecnológica baja (solo usan WhatsApp para llamadas y fotos familiares), sin formación legal.
* **Metodología Ciega:** Se entrega un formulario real N4 (desalojo) o carta de IRCC. Al grupo A se le entrega el documento físico original; al grupo B se le procesa mediante CLEARLY vía WhatsApp.
* **Medición de Tareas Críticas:**
  1. *¿Debo pagar o entregar algo?* (Sí/No).
  2. *¿Cuál es el último día exacto para responder?* (Día/Mes/Año).
  3. *¿Qué consecuencia explícita advierte la carta si no contesto?*
* **Criterio de Aceptación para Pase a Producción:**
  * **Tasa de Éxito en Fechas y Tareas:** 100% en el Grupo B en $< 60$ segundos.
  * **Carga Cognitiva (Escala NASA-TLX):** Reducción de frustración $> 70\%$ comparado con el Grupo A.

---

# **3. ARQUITECTURA DE INFERENCIA LOCAL Y PRESUPUESTO DE VRAM (24 GB GPU)**

### **3.1 Presupuesto de Memoria Gráfica (NVIDIA RTX 3090 / 4090 — 24,576 MiB)**

Para eliminar la dependencia de OpenAI o Google y garantizar cero costo por token, todo el cómputo de inferencia corre localmente sobre un solo nodo GPU de 24 GB optimizado para alta concurrencia.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│             ASIGNACIÓN DE VRAM EN NODO DEDICADO DE 24,576 MiB               │
│                                                                             │
│  [vLLM: Llama 3.1 8B AWQ]        [PaddleOCR PP-OCRv4]  [faster-whisper]     │
│  █████████████████████████████   ████████              ███████              │
│  15,360 MiB (62.5%)              2,800 MiB (11.4%)     2,550 MiB (10.4%)    │
│                                                                             │
│  [BGE-M3 Embeddings]  [Margen de Seguridad / Overhead PyTorch]              │
│  ████                 ██████                                                │
│  1,400 MiB (5.7%)     2,466 MiB (10.0%)                                     │
└─────────────────────────────────────────────────────────────────────────────┘
```

| Componente | Modelo / Tecnología | Precisión / Cuantización | Memoria de Pesos (Weights) | KV Cache / Búfer de Inferencia | Memoria Total Asignada | Justificación Técnica de Concurrencia |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **LLM Motor Core** | Meta Llama 3.1 8B Instruct | **AWQ 4-bit** (W4A16) | 4,800 MiB | 10,560 MiB (PagedAttention) | **15,360 MiB** | Soporta hasta $b = 8$ peticiones simultáneas con contexto completo de 8,192 tokens sin fragmentación. |
| **Motor OCR** | PaddleOCR (PP-OCRv4 Server) | **FP16** (TensorRT Engine) | 850 MiB | 1,950 MiB (Inference Buffer) | **2,800 MiB** | Procesa simultáneamente hasta 4 imágenes a resolución 1080p con detección y reconocimiento en $< 600\text{ms}$. |
| **Motor STT** | faster-whisper | **CTranslate2 int8_float16** | 1,550 MiB | 1,000 MiB (Beam Search Buffer) | **2,550 MiB** | Transcribe hasta 6 notas de voz simultáneas en $< 1.0\times$ Real Time Factor (RTF: 0.08). |
| **Embeddings** | BGE-M3 (BAAI) | **FP16** | 1,150 MiB | 250 MiB (Batch size 16) | **1,400 MiB** | Genera vectores de 1024 dimensiones para indexación RAG instantánea en PostgreSQL. |
| **Motor TTS** | Piper TTS | **ONNX / CPU Offload** | **0 MiB (GPU)** | 60 MiB en **RAM de Sistema** | **0 MiB (GPU)** | **Decisión Arquitectónica:** Piper TTS corre al 100% en CPU (consume $< 5\%$ de 4 núcleos x86). Cero impacto en VRAM. |
| **Margen de Seguridad** | CUDA Context & Overheads | N/A | 1,200 MiB | 1,266 MiB | **2,466 MiB** | Colchón estricto para evitar *CUDA Out-of-Memory (OOM)* durante picos de carga. |
| **TOTAL** | — | — | — | — | **22,110 MiB / 24,576 MiB (90.0% Utilización)** |

---

### **3.2 Pipeline de Preprocesamiento de Visión en OpenCV (Anti-Desenfoque y Sombras)**

Los adultos mayores frecuentemente capturan documentos con iluminación dispareja, perspectiva deformada o temblor leve. El siguiente pipeline ejecuta normalización morfológica antes de ingresar la imagen a PaddleOCR:

```python
import cv2
import numpy as np

def preprocess_document_for_ocr(image_bytes: bytes) -> np.ndarray:
    # 1. Decodificación a matriz BGR
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # 2. Corrección de iluminación no uniforme mediante canal L en LAB y CLAHE
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    cl = clahe.apply(l)
    limg = cv2.merge((cl, a, b))
    enhanced = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)

    # 3. Denoising preservando bordes tipográficos
    denoised = cv2.fastNlMeansDenoisingColored(enhanced, None, h=10, hColor=10, templateWindowSize=7, searchWindowSize=21)

    # 4. Estimación de orientación y des-rotación (Deskew)
    gray = cv2.cvtColor(denoised, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    coords = np.column_stack(np.where(thresh > 0))
    angle = cv2.minAreaRect(coords)[-1]

    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle

    (h, w) = img.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(denoised, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

    return rotated
```

---

### **3.3 Calibración de Silero VAD para Patrones de Habla Geriátrica**

Los algoritmos de detección de actividad por voz (*VAD*) comerciales cortan la grabación tras 1.5 a 2.0 segundos de silencio. En personas mayores, una pausa para recordar un dato o respirar dura típicamente entre 3.0 y 4.5 segundos.

```python
import torch

# Carga de Silero VAD local
vad_model, utils = torch.hub.load(
    repo_or_dir='snakers4/silero-vad',
    model='silero_vad',
    onnx=True,
    trust_repo=True
)
(get_speech_timestamps, save_audio, read_audio, VADIterator, collect_chunks) = utils

GERIATRIC_VAD_CONFIG = {
    "threshold": 0.30,                     # Umbral más bajo para captar voces tenues seniles
    "min_speech_duration_ms": 250,         # Captura palabras cortas como "Sí", "No"
    "max_speech_duration_s": 180,          # Límite máximo de nota de voz (3 minutos)
    "min_silence_duration_ms": 4500,       # TOLERANCIA EXTENDIDA: 4.5 segundos de silencio antes de cortar
    "speech_pad_ms": 600                   # Búfer previo y posterior para no podar la primera y última sílaba
}

def extract_valid_geriatric_speech(audio_tensor: torch.Tensor, sample_rate: int = 16000):
    speech_timestamps = get_speech_timestamps(
        audio_tensor,
        vad_model,
        sampling_rate=sample_rate,
        threshold=GERIATRIC_VAD_CONFIG["threshold"],
        min_speech_duration_ms=GERIATRIC_VAD_CONFIG["min_speech_duration_ms"],
        min_silence_duration_ms=GERIATRIC_VAD_CONFIG["min_silence_duration_ms"],
        speech_pad_ms=GERIATRIC_VAD_CONFIG["speech_pad_ms"]
    )
    return collect_chunks(audio_tensor, speech_timestamps)
```

---

# **4. ESQUEMA DE SEGURIDAD, AUTONOMÍA Y CONSENTIMIENTO FAMILIAR**

### **4.1 Protocolo Criptográfico de Asociación (Handshake Efímero con Zero-Knowledge)**

Para vincular la cuenta del adulto mayor con su hijo/cuidador sin exponer números telefónicos ni claves compartidas en texto plano:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│              PROTOCOLO DE HANDSHAKE EFÍMERO TITULAR-TUTOR                   │
│                                                                             │
│  [ADULTO MAYOR (App CLEARLY)]                           [TUTOR / HIJO]      │
│  1. Genera par de claves efímeras:                                          │
│     (PrivKey_A, PubKey_A) [Curve25519]                                      │
│  2. Muestra QR dinámico conteniendo:                                        │
│     { pairing_id, PubKey_A, expires_at: NOW + 180s }                        │
│                                              3. Escanea QR y firma con:     │
│                                                 (PrivKey_B, PubKey_B)       │
│                                              4. Envía a Backend:            │
│                                                 Handshake Payload cifrado   │
│  5. Backend calcula Secreto Compartido (ECDH):                              │
│     Secret = X25519(PrivKey_A, PubKey_B)                                    │
│  6. Genera Token de Capacidad Macaroons con permisos granulares.            │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### **4.2 Estructura del Token de Capacidad con Atenuación Macaroon / PASETO v4**

El token entregado al tutor no es un JWT con permisos estáticos, sino un token atenuado criptográficamente que restringe estrictamente su capacidad operativa:

```json
{
  "iss": "clearly-auth-core",
  "sub": "tutor_user_uuid_98a7b6c5",
  "senior_target": "senior_user_uuid_1234abcd",
  "caveats": [
    "action = read_only",
    "scope = critical_deadlines_and_checklists",
    "prohibit_actions = [financial_transfer, document_deletion, identity_alteration]",
    "valid_until = 2027-11-12T00:00:00Z"
  ],
  "signature": "ed25519_signature_bytes..."
}
```

---

### **4.3 Mecanismo de Coacción Silenciosa (*Duress Mode* contra Abuso Patrimonial)**

Si un adulto mayor es forzado físicamente o psicológicamente por un familiar a mostrar su aplicación o transferir poderes:

1. **Activación de Código de Emergencia (*Duress PIN*):**
   * El usuario cuenta con un PIN normal (ej. `1234`) y un PIN de Coacción configurado previamente con su navegador comunitario (ej. `9876`).
2. **Respuesta del Sistema ante Duress PIN:**
   * **Interfaz Idéntica:** La app no muestra ninguna señal de alerta en pantalla, ni mensajes de error, ni cambios visuales que delaten al usuario frente al coaccionador.
   * **Desconexión Silenciosa de Canales:** El backend suspende de forma inmediata y silenciosa todos los webhooks y eventos hacia el dispositivo del tutor registrado.
   * **Cifrado de Cuarentena:** Se congelan las vistas de documentos patrimoniales, mostrando únicamente registros ficticios o desactualizados.
   * **Despacho de Alerta Cívica:** Se genera un ticket encriptado con nivel de prioridad crítico hacia la red de trabajadores sociales certificados de CLEARLY Premium para seguimiento y visita de bienestar.

---

### **4.4 Trazabilidad Inmutable (Tamper-Evident Audit Trail)**

Cada acceso a un documento de un adulto mayor genera una entrada encadenada criptográficamente en la tabla `audit_ledger`:

$$\text{Hash}_n = \text{SHA-256}(\text{Hash}_{n-1} \parallel \text{Timestamp} \parallel \text{ActorID} \parallel \text{DocID} \parallel \text{Action})$$

Cualquier intento de un tutor o administrador de alterar el historial para ocultar accesos indebidos rompe la cadena criptográfica y bloquea el expediente automáticamente.

---
