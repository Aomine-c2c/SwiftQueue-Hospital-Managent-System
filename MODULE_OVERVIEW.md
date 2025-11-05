# Hospital Queue Management System - Module Overview

## System Architecture Diagram

```mermaid
graph TB
    %% Frontend Layer
    subgraph "Frontend Layer (React/TypeScript)"
        UI[User Interface Components]
        AUTH_CTX[Authentication Context]
        API_CLIENT[API Client Service]
        AI_SERVICE[AI Service Client]

        UI --> AUTH_CTX
        UI --> API_CLIENT
        UI --> AI_SERVICE
    end

    %% API Gateway Layer
    subgraph "API Gateway (FastAPI)"
        CORS[CORS Middleware]
        AUTH_MW[Authentication Middleware]
        SEC_MW[Security Middleware]
        RATE_LIMIT[Rate Limiting]

        CORS --> AUTH_MW
        AUTH_MW --> SEC_MW
        SEC_MW --> RATE_LIMIT
    end

    %% Core Services Layer
    subgraph "Core Services"
        AUTH_SVC[Authentication Service]
        QUEUE_SVC[Queue Management Service]
        STAFF_SVC[Staff Management Service]
        PATIENT_SVC[Patient Management Service]
        APPT_SVC[Appointment Service]
        PAYMENT_SVC[Payment Service]
        NOTIF_SVC[Notification Service]
        ANALYTICS_SVC[Analytics Service]
    end

    %% AI & ML Layer
    subgraph "AI & ML Services"
        TRIAGE_AI[Triage AI System]
        PREDICTION_SVC[Prediction Services]
        OPENROUTER_SVC[OpenRouter Integration]
        FALLBACK_AI[Fallback AI Service]
        CACHE_SVC[AI Cache Service]
    end

    %% Specialized Modules
    subgraph "Specialized Modules"
        EMERGENCY[Emergency Management]
        NAVIGATION[Hospital Navigation]
        FILE_UPLOAD[File Upload System]
        REPORTING[Reporting System]
        AUDIT[Audit Logging]
        SESSION_MGMT[Session Management]
    end

    %% Data Layer
    subgraph "Data Layer"
        DB[(SQLite/PostgreSQL)]
        CACHE[(Redis Cache)]
        FILE_STORAGE[(File Storage)]
        ML_MODELS[(ML Models)]
    end

    %% External Integrations
    subgraph "External Integrations"
        SMS_GATEWAY[SMS Gateway]
        EMAIL_SVC[Email Service]
        PAYMENT_GW[Payment Gateway]
        EHR_SYSTEM[EHR Integration]
        HL7_INTEGRATION[HL7 Integration]
    end

    %% Connections
    UI --> API_GATEWAY
    API_CLIENT --> API_GATEWAY
    AI_SERVICE --> API_GATEWAY

    API_GATEWAY --> CORE_SERVICES
    API_GATEWAY --> AI_SERVICES
    API_GATEWAY --> SPECIALIZED_MODULES

    CORE_SERVICES --> DATA_LAYER
    AI_SERVICES --> DATA_LAYER
    SPECIALIZED_MODULES --> DATA_LAYER

    AI_SERVICES --> EXTERNAL_INTEGRATIONS
    SPECIALIZED_MODULES --> EXTERNAL_INTEGRATIONS

    %% Styling
    classDef frontend fill:#e1f5fe
    classDef api fill:#f3e5f5
    classDef services fill:#e8f5e8
    classDef ai fill:#fff3e0
    classDef specialized fill:#fce4ec
    classDef data fill:#f5f5f5
    classDef external fill:#efebe9

    class UI,AUTH_CTX,API_CLIENT,AI_SERVICE frontend
    class CORS,AUTH_MW,SEC_MW,RATE_LIMIT api
    class AUTH_SVC,QUEUE_SVC,STAFF_SVC,PATIENT_SVC,APPT_SVC,PAYMENT_SVC,NOTIF_SVC,ANALYTICS_SVC services
    class TRIAGE_AI,PREDICTION_SVC,OPENROUTER_SVC,FALLBACK_AI,CACHE_SVC ai
    class EMERGENCY,NAVIGATION,FILE_UPLOAD,REPORTING,AUDIT,SESSION_MGMT specialized
    class DB,CACHE,FILE_STORAGE,ML_MODELS data
    class SMS_GATEWAY,EMAIL_SVC,PAYMENT_GW,EHR_SYSTEM,HL7_INTEGRATION external
```

## Module Descriptions

### Frontend Layer
- **User Interface Components**: React components for different user roles (Admin, Staff, Patient)
- **Authentication Context**: Manages user sessions and permissions
- **API Client Service**: Handles HTTP requests to backend APIs
- **AI Service Client**: Specialized client for AI-powered features

### API Gateway Layer
- **CORS Middleware**: Cross-origin resource sharing configuration
- **Authentication Middleware**: JWT token validation and user authentication
- **Security Middleware**: Input sanitization, XSS protection, security headers
- **Rate Limiting**: Prevents abuse and ensures fair resource usage

### Core Services
- **Authentication Service**: User registration, login, role management
- **Queue Management Service**: Patient queue operations, position tracking
- **Staff Management Service**: Staff scheduling, role assignments, performance tracking
- **Patient Management Service**: Patient records, history, demographics
- **Appointment Service**: Scheduling, booking, calendar management
- **Payment Service**: Billing, insurance processing, payment gateway integration
- **Notification Service**: SMS, email, in-app notifications
- **Analytics Service**: Dashboard metrics, reporting, insights

### AI & ML Services
- **Triage AI System**: Symptom analysis, emergency level assessment
- **Prediction Services**: Wait time prediction, peak hour forecasting
- **OpenRouter Integration**: External AI model access (DeepSeek, etc.)
- **Fallback AI Service**: Local AI processing when external services unavailable
- **AI Cache Service**: Response caching for improved performance

### Specialized Modules
- **Emergency Management**: Ambulance dispatch, critical care coordination
- **Hospital Navigation**: Indoor navigation, location services
- **File Upload System**: Document management, medical imaging
- **Reporting System**: Advanced analytics, custom reports
- **Audit Logging**: Security event tracking, compliance logging
- **Session Management**: User session tracking, timeout handling

### Data Layer
- **Database**: SQLite/PostgreSQL for structured data storage
- **Cache**: Redis for session storage and API response caching
- **File Storage**: Document and image storage system
- **ML Models**: Trained machine learning models for predictions

### External Integrations
- **SMS Gateway**: Infobip integration for SMS notifications
- **Email Service**: Email notifications and communications
- **Payment Gateway**: External payment processing
- **EHR Integration**: Electronic Health Record system integration
- **HL7 Integration**: Healthcare data exchange standards

## Key Relationships

1. **Frontend ↔ Backend**: RESTful API communication with WebSocket support
2. **Authentication Flow**: JWT tokens with role-based access control
3. **AI Integration**: Dual-path system (OpenRouter primary, local fallback)
4. **Data Flow**: Service layer → Repository pattern → Database
5. **Security**: Multi-layer security with middleware stack
6. **Caching**: Multi-level caching (API responses, AI results, sessions)

## Technology Stack

- **Frontend**: React, TypeScript, Tailwind CSS, Vite
- **Backend**: FastAPI, Python, SQLAlchemy
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **AI/ML**: OpenRouter API, scikit-learn, joblib
- **External APIs**: OpenRouter, Infobip SMS, Payment gateways
- **Deployment**: Docker, nginx (optional)

## Security Features

- JWT authentication with refresh tokens
- Role-based access control (RBAC)
- Rate limiting and DDoS protection
- Input validation and sanitization
- Audit logging and compliance tracking
- Secure file upload with virus scanning
- HTTPS enforcement in production

## Performance Optimizations

- AI response caching
- Database connection pooling
- API rate limiting
- Lazy loading of components
- Optimized bundle splitting
- CDN integration for static assets