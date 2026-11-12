import { DocumentAnalysisResult, CommunityEvent } from "../types/document";

export const SAMPLE_DOCUMENTS: Record<string, DocumentAnalysisResult> = {
  n4_eviction: {
    id: "doc-sample-n4-ltb-2026",
    user_id: "senior-elena-brampton-uuid",
    document_type: "Aviso de Desalojo por Renta Atrasada (Formulario N4)",
    issuing_entity: "Tribunal de Arrendamiento de Ontario (LTB)",
    plain_summary:
      "Esta carta es un aviso de tu arrendador porque hay un pago de renta pendiente. Tienes 14 días para pagar la cantidad indicada o para hablar con ellos y llegar a un acuerdo. No tienes que salir de tu casa hoy mismo.",
    detected_language: "es",
    fernandez_huerta_score: 88.5,
    readability_category: "Muy fácil (Nivel 4to-6to de primaria)",
    urgency: "critical",
    critical_deadline: "2026-11-26",
    days_remaining: 14,
    tutor_alert_triggered: true,
    requires_human_expert: true,
    actions_required: [
      {
        id: "act-1",
        document_id: "doc-sample-n4-ltb-2026",
        task_description:
          "Revisar tus recibos bancarios para confirmar si el mes reclamado realmente está sin pagar.",
        required_document: "Recibos de banco o comprobantes de transferencia Interac",
        deadline: "2026-11-16",
        is_completed: true,
        completed_at: "2026-11-12T17:00:00Z",
        created_at: "2026-11-12T16:00:00Z",
      },
      {
        id: "act-2",
        document_id: "doc-sample-n4-ltb-2026",
        task_description:
          "Pagar el monto adeudado ($1,250.00 CAD) antes de la fecha límite o pedir un plan de pagos por escrito.",
        required_document: "Comprobante oficial de pago firmado por el dueño",
        deadline: "2026-11-26",
        is_completed: false,
        completed_at: null,
        created_at: "2026-11-12T16:00:00Z",
      },
      {
        id: "act-3",
        document_id: "doc-sample-n4-ltb-2026",
        task_description:
          "Si no tienes el dinero completo, contactar a un trabajador social de Brampton Housing Help para pedir ayuda de emergencia de renta.",
        required_document: "Identificación oficial y carta N4 escaneada",
        deadline: "2026-11-18",
        is_completed: false,
        completed_at: null,
        created_at: "2026-11-12T16:00:00Z",
      },
    ],
    ambiguities_flagged: [
      "El aviso menciona cargos de mora por $50, pero la ley de Ontario generalmente no permite multas por retraso a menos que estén aprobadas por el tribunal.",
      "No se especifica si el pago puede ser entregado en cheque o solo por transferencia bancaria.",
    ],
    recommended_questions: [
      "¿Puedo pagar en dos partes durante este mes sin que presenten la solicitud formal al tribunal?",
      "¿Me pueden entregar un recibo firmado inmediatamente después de que haga el pago?",
    ],
    created_at: "2026-11-12T15:30:00Z",
    original_extracted_text: `LANDLORD AND TENANT BOARD - FORM N4
Notice to End your Tenancy Early for Non-payment of Rent
To: Elena Ramos (Tenant)
From: Peel Living Properties (Landlord)
Rental Unit: 45 Railroad St, Apt 304, Brampton, ON L6X 1G4

The landlord claims that you owe $1,250.00 in rent for November 2026.
You must pay this amount by the termination date: November 26, 2026 (14 calendar days from notice date November 12, 2026).
If you do not pay or move out by this date, the landlord may apply to the Board for an order evicting you.
Warning: Late fee charges of $50 have been appended.`,
  },

  ircc_letter: {
    id: "doc-sample-ircc-2026",
    user_id: "senior-elena-brampton-uuid",
    document_type: "Solicitud de Evidencia Adicional (Carta de Equidad Procesal)",
    issuing_entity: "Inmigración, Refugiados y Ciudadanía de Canadá (IRCC)",
    plain_summary:
      "El gobierno de Canadá está revisando tu trámite de residencia y necesita un documento adicional antes de tomar una decisión. No han rechazado tu caso, solo piden aclarar una información en un plazo de 30 días.",
    detected_language: "es",
    fernandez_huerta_score: 86.2,
    readability_category: "Muy fácil (Nivel 4to-6to de primaria)",
    urgency: "high",
    critical_deadline: "2026-12-12",
    days_remaining: 30,
    tutor_alert_triggered: true,
    requires_human_expert: true,
    actions_required: [
      {
        id: "act-ircc-1",
        document_id: "doc-sample-ircc-2026",
        task_description:
          "Pedir tu certificado de antecedentes penales actualizado del país de origen.",
        required_document: "Certificado con apostilla o legalización oficial",
        deadline: "2026-11-25",
        is_completed: false,
        completed_at: null,
        created_at: "2026-11-12T16:00:00Z",
      },
      {
        id: "act-ircc-2",
        document_id: "doc-sample-ircc-2026",
        task_description:
          "Hacer la traducción certificada al inglés de los documentos si vienen en español.",
        required_document: "Traducción con sello de traductor acreditado ATIO",
        deadline: "2026-12-05",
        is_completed: false,
        completed_at: null,
        created_at: "2026-11-12T16:00:00Z",
      },
      {
        id: "act-ircc-3",
        document_id: "doc-sample-ircc-2026",
        task_description:
          "Subir los documentos en el portal web de IRCC antes del 12 de Diciembre a las 11:59 PM.",
        required_document: "Archivos digitales en formato PDF legible",
        deadline: "2026-12-12",
        is_completed: false,
        completed_at: null,
        created_at: "2026-11-12T16:00:00Z",
      },
    ],
    ambiguities_flagged: [
      "La carta solicita antecedentes policiales de todos los lugares donde vivió más de 6 meses, pero no indica si aceptan versión electrónica.",
    ],
    recommended_questions: [
      "¿Puedo solicitar una extensión de 30 días si el consulado tarda en emitir el certificado?",
      "¿La traducción certificada debe incluir la declaración jurada física del traductor?",
    ],
    created_at: "2026-11-12T14:15:00Z",
    original_extracted_text: `IMMIGRATION, REFUGEES AND CITIZENSHIP CANADA (IRCC)
Case Processing Centre - Mississauga
Client ID: 8934-2901
Application: F000492812

Dear Elena Ramos,
This letter concerns your application for Permanent Residence under the Family Class.
In order to continue processing, you must provide an original Police Certificate from your country of origin covering the period from 2018 to present.
You must submit this evidence within 30 days of the date of this letter (Deadline: December 12, 2026).
Failure to provide the requested document may result in the refusal of your application.`,
  },

  cra_gis_pension: {
    id: "doc-sample-gis-cra-2026",
    user_id: "senior-elena-brampton-uuid",
    document_type: "Renovación de Suplemento de Renta Garantizada (GIS)",
    issuing_entity: "Service Canada / Agencia de Ingresos de Canadá (CRA)",
    plain_summary:
      "Service Canada necesita confirmar tus ingresos del año pasado para continuar enviándote el suplemento mensual de dinero de tu pensión. Todo está bien, solo debes presentar tu declaración de impuestos antes de fin de mes.",
    detected_language: "es",
    fernandez_huerta_score: 91.0,
    readability_category: "Muy fácil (Nivel 4to de primaria)",
    urgency: "medium",
    critical_deadline: "2026-12-01",
    days_remaining: 19,
    tutor_alert_triggered: false,
    requires_human_expert: false,
    actions_required: [
      {
        id: "act-gis-1",
        document_id: "doc-sample-gis-cra-2026",
        task_description:
          "Reunir tus comprobantes de pensión OAS del año anterior (formulario T4A-OAS).",
        required_document: "Hojas de impuestos T4A de Service Canada",
        deadline: "2026-11-20",
        is_completed: true,
        completed_at: "2026-11-12T12:00:00Z",
        created_at: "2026-11-12T10:00:00Z",
      },
      {
        id: "act-gis-2",
        document_id: "doc-sample-gis-cra-2026",
        task_description:
          "Llevar los papeles a la clínica gratuita de impuestos para personas mayores en la biblioteca municipal de Brampton.",
        required_document: "Identificación con foto y cartas de ingresos",
        deadline: "2026-11-28",
        is_completed: false,
        completed_at: null,
        created_at: "2026-11-12T10:00:00Z",
      },
    ],
    ambiguities_flagged: [],
    recommended_questions: [
      "¿La clínica gratuita de impuestos en la biblioteca puede enviar mi declaración por internet el mismo día?",
    ],
    created_at: "2026-11-12T09:00:00Z",
    original_extracted_text: `SERVICE CANADA - OLD AGE SECURITY & GUARANTEED INCOME SUPPLEMENT (GIS)
Notification of Annual Entitlement Review
Recipient: Elena Ramos
OAS Account Number: ***-**-4912

To ensure your monthly GIS payment is not interrupted starting next quarter, your 2025 net income must be assessed.
Please file your income tax return or submit form ISP-3026 by December 1, 2026.
If you require assistance, community volunteer tax clinics are available across Brampton.`,
  },
};

export const SAMPLE_EVENTS: CommunityEvent[] = [
  {
    id: "evt-brampton-yoga-1",
    title: "Taller de Bienestar y Yoga Suave en Silla",
    what: "Clase grupal muy suave de estiramiento y relajación diseñada especialmente para personas mayores de 60 años. Se practica sentado en una silla cómoda sin esfuerzo físico pesado.",
    when_where:
      "Sábado 15 de Noviembre, 2:00 PM a 3:30 PM en Centro Comunitario Downtown Brampton (8 Central Park Dr).",
    cost: "GRATUITO (Cero costo, no requiere membresía).",
    how_to_register:
      "Puedes llegar directamente y registrarte en la entrada, o pedir a tu familia que te anote por teléfono llamando al 311.",
    is_free: true,
    is_wheelchair_accessible: true,
    is_senior_friendly: true,
    transport_tip:
      "Autobús Brampton Transit Ruta 1 o 501 Züm se detiene justo frente a la puerta principal con rampa accesible.",
    organizer: "Biblioteca Pública de Brampton & Parks & Rec",
    date_label: "Sáb 15 Nov",
  },
  {
    id: "evt-brampton-tax-2",
    title: "Clínica Gratuita de Impuestos y Trámites para Pensionados",
    what: "Voluntarios acreditados te ayudan a llenar y enviar tu declaración de impuestos para que no se detengan tus pagos del gobierno (OAS y GIS). Atención disponible en español e inglés.",
    when_where:
      "Miércoles 19 de Noviembre, 10:00 AM a 2:00 PM en Biblioteca Four Corners (65 Queen St E, Brampton).",
    cost: "GRATUITO (Servicio cívico oficial sin cobro).",
    how_to_register:
      "Trae tus papeles en mano. Las fichas de turno se entregan por orden de llegada a partir de las 9:30 AM.",
    is_free: true,
    is_wheelchair_accessible: true,
    is_senior_friendly: true,
    transport_tip:
      "A 3 minutos a pie de la estación de tren Brampton GO. Cuenta con ascensor en el vestíbulo.",
    organizer: "Community Volunteer Income Tax Program (CVITP)",
    date_label: "Mié 19 Nov",
  },
  {
    id: "evt-brampton-caminar-3",
    title: "Club de Caminata Amigable y Café Comunitario",
    what: "Caminata corta y tranquila de 20 minutos por los senderos planos del parque Gage, seguida de café caliente, té y charla entre vecinos.",
    when_where:
      "Viernes 21 de Noviembre, 10:30 AM en Kiosco central de Gage Park (Main St S & Wellington St W).",
    cost: "GRATUITO (El café y galletas son cortesía del club).",
    how_to_register: "No requiere inscripción previa. Solo acude con calzado cómodo y abrigo.",
    is_free: true,
    is_wheelchair_accessible: true,
    is_senior_friendly: true,
    transport_tip: "Estacionamiento municipal gratuito con lugares para discapacidad.",
    organizer: "Club de Adultos Mayores de Brampton",
    date_label: "Vie 21 Nov",
  },
];

