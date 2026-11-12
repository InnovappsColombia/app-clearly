# **CLEARLY — Backend Core API (FastAPI)**

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![Pydantic v2](https://img.shields.io/badge/Pydantic-v2.0%2B-e92063.svg)](https://docs.pydantic.dev/)
[![Readability: FH >= 80](https://img.shields.io/badge/Readability-Fernández--Huerta%20%E2%89%A5%2080-brightgreen.svg)](#)
[![FMEA FM-02: Mitigated](https://img.shields.io/badge/FMEA%20FM--02-Deterministic%200%25%20Discrepancy-blue.svg)](#)

El backend de **CLEARLY** es el núcleo soberano de procesamiento de documentos burocráticos, correspondencia médica y citaciones legales. Opera bajo una arquitectura **local-first**, eliminando costos variables por token y garantizando el cumplimiento de las normativas de privacidad **PIPEDA** y **GDPR**.

---

## **1. Arquitectura de Módulos (Sprint 1: Hero Feature)**

```
Backend/
├── app/
│   ├── main.py                     # Entrypoint de FastAPI, CORS, middlewares y handlers
│   ├── core/
│   │   ├── config.py               # Configuración con Pydantic Settings
│   │   └── security.py             # Helpers de seguridad y hash
│   ├── db/
│   │   ├── repository.py           # Repositorio asíncrono con fallback y seed data
│   │   └── session.py              # Gestión de sesiones
│   ├── models/
│   │   └── entities.py             # Modelos de dominio (User, Document, Action, Notification)
│   ├── schemas/
│   │   └── document.py             # Esquemas de entrada y salida Pydantic v2
│   ├── services/
│   │   ├── spanish_syllabifier.py  # Silabeador fonológico de alta precisión en español
│   │   ├── readability.py          # Auditor Fernández-Huerta (FH >= 80)
│   │   ├── date_extractor.py       # Motor temporal determinista (Mitigación FMEA FM-02)
│   │   ├── legal_guardrail.py      # Guardrail legal anti-asesoría no autorizada (IRPA S.91)
│   │   ├── storage.py              # Almacenamiento MinIO S3 con fallback local y SHA-256
│   │   ├── ocr_service.py          # Extracción y decodificación de texto de cartas
│   │   ├── plain_language.py       # Motor de reescritura en 3 capas
│   │   └── document_pipeline.py    # Orquestador del pipeline documental
│   └── api/
│       ├── deps.py                 # Inyección de dependencias
│       └── v1/
│           ├── router.py           # Enrutador principal de la API v1
│           ├── health.py           # Diagnóstico de salud y almacenamiento
│           └── documents.py        # Endpoints de ingesta y consulta de documentos
├── tests/
│   ├── async_helper.py             # Driver de pruebas síncrono ultra-rápido
│   ├── test_syllabifier.py         # Pruebas de silabeo fonológico
│   ├── test_readability.py         # Pruebas de índice Fernández-Huerta (FH >= 80)
│   ├── test_date_extractor.py      # Pruebas de mitigación FMEA FM-02 (Aritmética temporal)
│   ├── test_legal_guardrail.py     # Pruebas de barrera legal anti-asesoría
│   ├── test_storage.py             # Pruebas de almacenamiento y SHA-256
│   ├── test_document_pipeline.py   # Pruebas de integración del pipeline completo
│   ├── test_api_documents.py       # Pruebas de endpoints RESTful
│   └── run_tests.py                # Runner unificado de la suite de pruebas
├── Dockerfile                      # Contenedor optimizado de producción
├── requirements.txt                # Dependencias fijadas
└── README.md                       # Este documento
```

---

## **2. Especificaciones Técnicas Clave**

### **2.1 Auditor Sintáctico Fernández-Huerta ($FH \ge 80$)**
Calcula el índice de legibilidad para el idioma español:
$$FH = 206.84 - (0.60 \times P) - (1.02 \times F)$$
* **$P$**: Densidad silábica (número de sílabas por cada 100 palabras).
* **$F$**: Longitud media de las oraciones (palabras por frase).
* **Criterio de Aceptación:** Todo documento generado por el pipeline debe certificar $FH \ge 80$ (*"Lectura Fácil / Muy Fácil"*, accesible para personas con nivel escolar primario o deterioro cognitivo leve).

### **2.2 Motor de Extracción Temporal Determinista (Mitigación FMEA FM-02)**
* **Problema:** Los LLMs frecuentemente alucinan cálculos de fechas al sumar días a un punto de referencia (ej. *"14 días tras la fecha del matasellos (30 de octubre)"* $\rightarrow$ el LLM erróneamente calcula 15 de noviembre).
* **Solución CLEARLY:** El LLM o los extractores solo identifican la fecha base y el operador ($+14\text{d}$, $+10\text{ días hábiles}$); una biblioteca determinista calcula la fecha exacta en el calendario, con tolerancia de error del 0%.
* **Escala de Urgencia y Alertas:**
  * `critical` ($\le 3$ días / 72h): Alerta inmediata al titular y tutor.
  * `high` ($\le 14$ días / $< 15$ días): Genera notificación preventiva prioritaria en el *Tutor Hub*.
  * `medium` ($\le 30$ días): Seguimiento regular en el checklist.
  * `low` ($> 30$ días): Informativo.

### **2.3 Guardrail Legal y Frontera Ontológica (IRPA Sección 91)**
El sistema analiza cualquier texto generado frente a patrones prohibidos de consejo prescriptivo (ej. *"debe demandar"*, *"le recomiendo apelar"*, *"no pague"*). Si se detecta un caso de alto riesgo legal (orden de expulsión, lanzamiento judicial), el sistema marca `requires_human_expert = True` y ofrece derivar el caso a un profesional verificado en **CLEARLY Premium**.

---

## **3. Endpoints de la API REST (`/api/v1`)**

| Método | Endpoint | Descripción |
| :--- | :--- | :--- |
| `GET` | `/api/v1/health` | Estado del servicio y disponibilidad de MinIO |
| `POST` | `/api/v1/documents/process` | **Hero Feature**: Ingesta multipart, OCR, cálculo temporal, FH y persistencia |
| `GET` | `/api/v1/documents/{id}` | Consulta de expediente estructurado con acciones y texto original |
| `GET` | `/api/v1/documents/user/{user_id}` | Lista de documentos analizados de un usuario titular |
| `PATCH`| `/api/v1/documents/actions/{action_id}/toggle` | Marca/desmarca una tarea del checklist interactivo |
| `POST` | `/api/v1/documents/audit-readability` | Audita un texto y calcula el índice Fernández-Huerta |
| `POST` | `/api/v1/documents/extract-dates` | Ejecuta extracción de plazos deterministas sobre texto libre |

---

## **4. Ejecución de la Suite de Pruebas**

Para ejecutar las 29 pruebas unitarias y de integración de Sprint 1:

```bash
python Backend/tests/run_tests.py
```

Salida esperada:
```
CLEARLY Sprint 1 Test Results: Ran 29 tests.
✅ ALL TESTS PASSED SUCCESSFULLY!
```

