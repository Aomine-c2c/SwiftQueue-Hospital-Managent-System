# 🚀 SwiftQueue Hospital Management System

A comprehensive, modern hospital management system built with cutting-edge technologies for efficient healthcare delivery.

## ✨ Features

### 🏥 Core Healthcare Features
- **Patient Management**: Complete patient lifecycle management
- **Appointment Scheduling**: Intelligent scheduling with conflict resolution
- **Queue Management**: Real-time queue monitoring with AI-powered predictions
- **Telemedicine**: Video consultations with integrated chat and file sharing
- **Prescription Management**: Digital prescriptions with drug interaction checking
- **Inventory Management**: Complete pharmacy and equipment tracking
- **Patient Portal**: Self-service portal for patients
- **Emergency Response**: First aid guidance and dispatch coordination

### 🤖 AI-Powered Features
- **Triage Intelligence**: AI-powered patient prioritization
- **Wait Time Prediction**: Machine learning-based queue predictions
- **Symptom Analysis**: Intelligent symptom classification
- **Resource Optimization**: AI-driven staff and resource allocation
- **Anomaly Detection**: Automated issue identification

### 📊 Analytics & Reporting
- **Real-time Dashboards**: Live system monitoring
- **Performance Analytics**: Comprehensive reporting
- **Patient Flow Analysis**: Optimize hospital operations
- **Financial Reporting**: Revenue and cost analysis

## 🛠️ Technology Stack

### Frontend
- **React 18** - Modern React with hooks
- **TypeScript** - Type-safe development
- **Zustand** - Lightweight state management
- **React Query** - Powerful data fetching and caching
- **Tailwind CSS** - Utility-first CSS framework
- **Storybook** - Component development and documentation

### Backend
- **FastAPI** - High-performance async web framework
- **Python 3.11** - Modern Python with async support
- **SQLAlchemy** - Powerful ORM with async support
- **PostgreSQL** - Robust relational database
- **Redis** - High-performance caching and session storage
- **JWT** - Secure authentication with refresh tokens

### DevOps & Infrastructure
- **Docker** - Containerized deployment
- **Kubernetes** - Container orchestration
- **Nginx** - Reverse proxy and load balancing
- **Prometheus** - Metrics collection and monitoring
- **Grafana** - Visualization and dashboards
- **Prisma** - Type-safe database operations

### Quality Assurance
- **Playwright** - End-to-end testing
- **Lighthouse** - Performance monitoring
- **Sentry** - Error tracking and monitoring
- **Prettier/ESLint** - Code formatting and linting

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ and npm
- Python 3.11+

### Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/swiftqueue.git
   cd swiftqueue
   ```

2. **Environment Setup**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start Development Environment**
   ```bash
   # Start all services
   docker-compose up -d

   # Or for development
   npm run dev
   ```

4. **Run Tests**
   ```bash
   # Frontend tests
   npm test

   # E2E tests
   npx playwright test

   # Backend tests
   cd backend && python -m pytest
   ```

## 📁 Project Structure

```
swiftqueue/
├── frontend/                 # React frontend
│   ├── src/
│   │   ├── components/       # Reusable UI components
│   │   ├── stores/          # Zustand state stores
│   │   ├── hooks/           # Custom React hooks
│   │   ├── lib/             # Utilities and configurations
│   │   └── pages/           # Page components
│   ├── e2e/                 # Playwright tests
│   └── .storybook/          # Storybook configuration
├── backend/                  # FastAPI backend
│   ├── app/
│   │   ├── models/          # SQLAlchemy models
│   │   ├── routes/          # API endpoints
│   │   ├── services/        # Business logic
│   │   └── core/            # Core functionality
│   └── tests/               # Backend tests
├── docker/                   # Docker configurations
├── k8s/                     # Kubernetes manifests
├── monitoring/              # Prometheus & Grafana configs
├── scripts/                 # Automation scripts
└── docs/                    # Documentation
```

## 🔧 Configuration

### Environment Variables

```bash
# Application
ENVIRONMENT=development
SECRET_KEY=your-secret-key
DEBUG=True

# Database
DATABASE_URL=postgresql://user:password@localhost/swiftqueue

# Redis
REDIS_URL=redis://localhost:6379

# Authentication
JWT_SECRET_KEY=your-jwt-secret
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# External Services
SENTRY_DSN=your-sentry-dsn
STRIPE_PUBLIC_KEY=your-stripe-key

# Email
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

## 🧪 Testing

### Unit Tests
```bash
# Frontend
npm test

# Backend
cd backend && python -m pytest tests/
```

### E2E Tests
```bash
# Run all E2E tests
npx playwright test

# Run specific test
npx playwright test auth.spec.ts

# Debug mode
npx playwright test --debug
```

### Performance Testing
```bash
# Lighthouse audit
npm run lighthouse

# Load testing
npm run load-test
```

## 🚀 Deployment

### Docker Deployment
```bash
# Build and deploy
./scripts/deploy.sh full

# Or step by step
./scripts/deploy.sh build
./scripts/deploy.sh deploy
```

### Kubernetes Deployment
```bash
# Deploy to Kubernetes
kubectl apply -f k8s/
kubectl rollout status deployment/swiftqueue-app
```

## 📊 Monitoring

### Access Monitoring Dashboards
- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090
- **Application Metrics**: http://localhost:8001/metrics

### Health Checks
```bash
# Application health
curl http://localhost/health

# Database connectivity
curl http://localhost/health/db

# Redis connectivity
curl http://localhost/health/redis
```

## 🔒 Security

- JWT-based authentication with refresh tokens
- Role-based access control (RBAC)
- Rate limiting and DDoS protection
- Input validation and sanitization
- SQL injection prevention
- XSS protection
- CSRF protection
- Secure headers (HSTS, CSP, etc.)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow TypeScript/React best practices
- Write comprehensive tests
- Update documentation
- Ensure code passes linting
- Follow conventional commit messages

## 📝 API Documentation

API documentation is automatically generated and available at:
- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc

## 🐛 Error Monitoring

Errors are automatically tracked using Sentry. Check the Sentry dashboard for:
- Frontend JavaScript errors
- Backend Python exceptions
- Performance issues
- User feedback

## 📈 Performance

The application is optimized for performance with:
- Code splitting and lazy loading
- Image optimization
- Caching strategies
- Database query optimization
- CDN integration

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- React, FastAPI, and PostgreSQL communities
- Open source contributors
- Healthcare professionals for domain expertise

## 📞 Support

For support, email support@swiftqueue.com or join our Slack community.

---

**Built with ❤️ for better healthcare delivery**
