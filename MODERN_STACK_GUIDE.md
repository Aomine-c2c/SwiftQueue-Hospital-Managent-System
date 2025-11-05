# SwiftQueue - Modern Tech Stack Implementation

This document provides comprehensive documentation for all the modern tools and technologies implemented in SwiftQueue Hospital Management System.

## 📋 Table of Contents

- [Zustand State Management](#zustand-state-management)
- [React Query](#react-query)
- [Lighthouse CI](#lighthouse-ci)
- [Storybook](#storybook)
- [Playwright E2E Testing](#playwright-e2e-testing)
- [Sentry Error Tracking](#sentry-error-tracking)
- [Bash Scripts](#bash-scripts)
- [Docker & Docker Compose](#docker--docker-compose)
- [Kubernetes](#kubernetes)
- [Redis Caching](#redis-caching)
- [Nginx](#nginx)
- [JWT Authentication](#jwt-authentication)
- [Prometheus](#prometheus)
- [Grafana](#grafana)

---

## 🏪 Zustand State Management

### Overview
Zustand is used for lightweight, scalable state management replacing Redux.

### Stores Created

#### 1. **Auth Store** (`src/stores/authStore.ts`)
- User authentication state
- Token management with refresh tokens
- Persistent storage with localStorage

```typescript
import { useAuthStore } from './stores/authStore';

// Usage
const { user, login, logout } = useAuthStore();
```

#### 2. **Queue Store** (`src/stores/queueStore.ts`)
- Queue management state
- Filtering and sorting
- Real-time updates with DevTools

```typescript
import { useQueueStore } from './stores/queueStore';

const { queues, addQueue, updateQueue } = useQueueStore();
```

#### 3. **Notification Store** (`src/stores/notificationStore.ts`)
- Toast notifications
- Auto-dismiss with configurable duration
- Action buttons support

#### 4. **UI Store** (`src/stores/uiStore.ts`)
- Theme management
- Sidebar state
- Online/offline detection

---

## 🔄 React Query (TanStack Query)

### Setup
Configured in `src/lib/react-query.ts` with optimized defaults:
- 5-minute stale time
- 10-minute garbage collection time
- Automatic refetch on reconnect

### API Hooks (`src/hooks/useApi.ts`)

```typescript
// Fetch queues
const { data, isLoading, error } = useQueues({ status: 'waiting' });

// Create queue entry
const { mutate: createQueue } = useCreateQueue();
createQueue(queueData);

// Update queue
const { mutate: updateQueue } = useUpdateQueue();
updateQueue({ id, updates });
```

### Features
- Automatic caching and invalidation
- Optimistic updates
- Request deduplication
- Token refresh interceptor

---

## 🔍 Lighthouse CI

### Configuration
File: `lighthouserc.js`

### Performance Budgets
- Performance: ≥80%
- Accessibility: ≥90%
- Best Practices: ≥85%
- SEO: ≥85%

### Run Lighthouse
```bash
npm run lighthouse
```

---

## 📖 Storybook

### Setup
```bash
npx storybook@latest init
npm run storybook
```

### Addons Included
- Accessibility testing (@storybook/addon-a11y)
- Interactions testing
- Essential controls

### Create Stories
```typescript
// Button.stories.tsx
import type { Meta, StoryObj } from '@storybook/react';
import { Button } from './Button';

const meta: Meta<typeof Button> = {
  title: 'Components/Button',
  component: Button,
};

export default meta;
```

---

## 🎭 Playwright E2E Testing

### Configuration
File: `playwright.config.ts`

### Test Files
- `e2e/auth.spec.ts` - Authentication flows
- `e2e/queue.spec.ts` - Queue management

### Run Tests
```bash
# Run all tests
npm run test:e2e

# Run with UI
npm run test:e2e:ui

# Debug mode
npm run test:e2e:debug
```

### Features
- Multi-browser testing (Chrome, Firefox, Safari)
- Mobile device emulation
- Accessibility testing with @axe-core
- Auto-wait and retry logic

---

## 🐛 Sentry Error Tracking

### Setup
File: `src/lib/sentry.ts`

### Initialize
```typescript
import { initSentry } from './lib/sentry';

initSentry();
```

### Features
- Error tracking
- Performance monitoring (10% sample rate)
- Session replay on errors
- User identification
- Custom breadcrumbs

### Usage
```typescript
import { captureException, addBreadcrumb, setUser } from './lib/sentry';

// Track error
captureException(error, { customContext: data });

// Add breadcrumb
addBreadcrumb('User action', 'user', 'info');

// Set user
setUser({ id, email, username });
```

### Environment Variables
```bash
VITE_SENTRY_DSN=your_sentry_dsn
VITE_APP_VERSION=1.0.0
```

---

## 📜 Bash Scripts

### 1. Deployment Script (`scripts/deploy.sh`)
```bash
# Deploy to production
./scripts/deploy.sh

# Skip build
SKIP_BUILD=true ./scripts/deploy.sh

# With auto-rollback
AUTO_ROLLBACK=true ./scripts/deploy.sh
```

### 2. Health Check Script (`scripts/health-check.sh`)
```bash
./scripts/health-check.sh
```

Checks:
- Backend API health
- Frontend availability
- Redis connection
- PostgreSQL connection
- API response time

---

## 🐳 Docker & Docker Compose

### Development Environment
File: `docker-compose.dev.yml`

### Services
- PostgreSQL database
- Redis cache
- Backend API
- Frontend
- Nginx reverse proxy
- Prometheus monitoring
- Grafana dashboards

### Commands
```bash
# Start all services
npm run docker:dev

# Build and start
npm run docker:dev:build

# Stop all services
npm run docker:down
```

### Environment Variables
```bash
DB_PASSWORD=changeme123
REDIS_PASSWORD=redis123
SECRET_KEY=your-secret-key
GRAFANA_USER=admin
GRAFANA_PASSWORD=admin123
```

---

## ☸️ Kubernetes

### Manifests
- `k8s/backend-deployment.yaml` - Backend deployment with HPA
- `k8s/frontend-deployment.yaml` - Frontend deployment
- `k8s/ingress.yaml` - Ingress configuration
- `k8s/configmap-secrets.yaml` - ConfigMaps and Secrets

### Deploy
```bash
npm run k8s:deploy
```

### Features
- Horizontal Pod Autoscaling (2-10 replicas)
- Rolling updates
- Health checks (liveness & readiness)
- Resource limits
- SSL/TLS termination

---

## 🔴 Redis Caching

### Implementation
File: `backend/app/utils/redis_cache.py`

### Features
- Query result caching
- Session storage
- Rate limiting data
- Pub/Sub for real-time updates

### Usage
```python
from app.utils.redis_cache import cache, cache_response

# Direct cache operations
cache.set('key', value, ttl=300)
result = cache.get('key')
cache.delete('key')

# Decorator for caching
@cache_response('queue_list', ttl=60)
async def get_queues():
    return await db.query(Queue).all()
```

---

## 🌐 Nginx

### Configuration
File: `nginx/nginx.conf`

### Features
- Load balancing (least connections)
- SSL/TLS termination
- Gzip compression
- Rate limiting (API: 10 req/s, Auth: 5 req/min)
- WebSocket support
- Security headers
- Static file caching (1 year)

### Endpoints
- `/api/*` → Backend API
- `/ws/*` → WebSocket connections
- `/health` → Health check
- `/*` → Frontend SPA

---

## 🔐 JWT Authentication

### Implementation
File: `backend/app/utils/jwt_auth.py`

### Features
- Access tokens (30 min expiry)
- Refresh tokens (7 days expiry)
- Token rotation on refresh
- Token blacklisting with Redis
- Secure password hashing (bcrypt)

### API Endpoints
```python
# Login
POST /api/auth/login
{
  "email": "user@example.com",
  "password": "password"
}

# Refresh token
POST /api/auth/refresh
{
  "refresh_token": "..."
}

# Logout (revoke token)
POST /api/auth/logout
```

---

## 📊 Prometheus

### Configuration
File: `monitoring/prometheus.yml`

### Metrics Collected
- HTTP request count
- Request duration
- Queue length by status
- Wait time by priority
- Database query duration
- Error rates
- Authentication attempts
- WebSocket connections
- Cache hit/miss rates

### Implementation
File: `backend/app/utils/prometheus_metrics.py`

### Usage
```python
from app.utils.prometheus_metrics import (
    track_request_metrics,
    track_queue_metrics,
    track_wait_time,
    monitor_performance
)

# Track metrics
track_request_metrics('GET', '/api/queue', 200, duration)
track_queue_metrics(queues)

# Performance decorator
@monitor_performance('get_patients')
async def get_patients():
    return await db.query(Patient).all()
```

### Metrics Endpoint
```
GET http://localhost:8000/metrics
```

---

## 📈 Grafana

### Configuration
- Dashboards: `monitoring/grafana/dashboards/`
- Data sources: `monitoring/grafana/datasources/`

### Access
```
http://localhost:3000
Default: admin/admin123
```

### Dashboards
1. **System Overview**
   - CPU, Memory, Disk usage
   - Network traffic

2. **Application Metrics**
   - Request rate and latency
   - Error rate
   - Queue statistics

3. **Database Metrics**
   - Connection pool
   - Query performance
   - Slow queries

4. **Business KPIs**
   - Average wait time
   - Patient throughput
   - Service utilization

### Alerts
File: `monitoring/alerts.yml`

Configured alerts for:
- High API response time (>2s)
- High error rate (>10%)
- Long queue (>50 patients)
- Low database connections
- High memory/CPU usage
- Service downtime

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
npm install
pip install -r backend/requirements.txt
```

### 2. Environment Variables
```bash
# Frontend (.env)
VITE_API_URL=http://localhost:8000/api
VITE_SENTRY_DSN=your_sentry_dsn

# Backend (.env)
DATABASE_URL=postgresql://user:pass@localhost:5432/swiftqueue
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key
SENTRY_DSN=your_sentry_dsn
```

### 3. Start Development
```bash
# With Docker (recommended)
npm run docker:dev

# Or manually
npm run dev
```

### 4. Run Tests
```bash
npm run test:e2e
npm run lighthouse
```

### 5. Deploy to Production
```bash
npm run k8s:deploy
```

---

## 📚 Additional Resources

- [Zustand Documentation](https://docs.pmnd.rs/zustand)
- [TanStack Query](https://tanstack.com/query)
- [Playwright](https://playwright.dev)
- [Sentry](https://docs.sentry.io)
- [Prometheus](https://prometheus.io/docs)
- [Grafana](https://grafana.com/docs)

---

## 🤝 Contributing

1. Create feature branch
2. Write tests
3. Update documentation
4. Submit pull request

---

## 📄 License

MIT License - see LICENSE file for details
