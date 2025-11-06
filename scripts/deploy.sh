#!/bin/bash

# SwiftQueue Hospital Management System - Deployment Script
# This script handles deployment to different environments

set -e  # Exit on any error

# Configuration
PROJECT_NAME="swiftqueue"
DOCKER_REGISTRY="${DOCKER_REGISTRY:-localhost:5000}"
ENVIRONMENT="${ENVIRONMENT:-development}"
VERSION="${VERSION:-latest}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."

    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi

    # Check if Docker Compose is installed
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi

    # Check if kubectl is installed for Kubernetes deployments
    if [ "$DEPLOYMENT_TYPE" = "kubernetes" ]; then
        if ! command -v kubectl &> /dev/null; then
            log_error "kubectl is not installed. Please install kubectl for Kubernetes deployments."
            exit 1
        fi
    fi

    log_success "Prerequisites check passed"
}

# Build Docker images
build_images() {
    log_info "Building Docker images..."

    # Build main application image
    docker build -t ${DOCKER_REGISTRY}/${PROJECT_NAME}-app:${VERSION} .

    # Tag as latest if this is the latest version
    if [ "$VERSION" = "latest" ]; then
        docker tag ${DOCKER_REGISTRY}/${PROJECT_NAME}-app:${VERSION} ${DOCKER_REGISTRY}/${PROJECT_NAME}-app:latest
    fi

    log_success "Docker images built successfully"
}

# Push images to registry
push_images() {
    log_info "Pushing images to registry..."

    docker push ${DOCKER_REGISTRY}/${PROJECT_NAME}-app:${VERSION}

    if [ "$VERSION" = "latest" ]; then
        docker push ${DOCKER_REGISTRY}/${PROJECT_NAME}-app:latest
    fi

    log_success "Images pushed to registry"
}

# Deploy using Docker Compose
deploy_docker_compose() {
    log_info "Deploying with Docker Compose..."

    # Create environment file
    cat > .env << EOF
ENVIRONMENT=${ENVIRONMENT}
SECRET_KEY=${SECRET_KEY}
DATABASE_URL=${DATABASE_URL}
REDIS_URL=redis://redis:6379
SENTRY_DSN=${SENTRY_DSN}
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
GRAFANA_PASSWORD=${GRAFANA_PASSWORD}
EOF

    # Start services
    docker-compose up -d

    log_success "Deployment completed with Docker Compose"
}

# Deploy to Kubernetes
deploy_kubernetes() {
    log_info "Deploying to Kubernetes..."

    # Apply Kubernetes manifests
    kubectl apply -f k8s/

    # Wait for rollout to complete
    kubectl rollout status deployment/${PROJECT_NAME}-app

    log_success "Deployment completed on Kubernetes"
}

# Run database migrations
run_migrations() {
    log_info "Running database migrations..."

    if [ "$DEPLOYMENT_TYPE" = "docker-compose" ]; then
        docker-compose exec app python -m alembic upgrade head
    elif [ "$DEPLOYMENT_TYPE" = "kubernetes" ]; then
        kubectl exec -it deployment/${PROJECT_NAME}-app -- python -m alembic upgrade head
    fi

    log_success "Database migrations completed"
}

# Run tests
run_tests() {
    log_info "Running tests..."

    if [ "$DEPLOYMENT_TYPE" = "docker-compose" ]; then
        docker-compose exec app python -m pytest tests/ -v
    elif [ "$DEPLOYMENT_TYPE" = "kubernetes" ]; then
        kubectl exec -it deployment/${PROJECT_NAME}-app -- python -m pytest tests/ -v
    fi

    log_success "Tests completed"
}

# Health check
health_check() {
    log_info "Performing health checks..."

    # Wait for services to be ready
    sleep 30

    # Check main application
    if curl -f http://localhost/health; then
        log_success "Application health check passed"
    else
        log_error "Application health check failed"
        exit 1
    fi

    # Check database connectivity
    if [ "$DEPLOYMENT_TYPE" = "docker-compose" ]; then
        if docker-compose exec -T postgres pg_isready -U swiftqueue; then
            log_success "Database health check passed"
        else
            log_error "Database health check failed"
            exit 1
        fi
    fi
}

# Rollback deployment
rollback() {
    log_warning "Rolling back deployment..."

    if [ "$DEPLOYMENT_TYPE" = "docker-compose" ]; then
        docker-compose down
        # Start previous version if available
        PREVIOUS_VERSION=$(docker images ${DOCKER_REGISTRY}/${PROJECT_NAME}-app --format "{{.Repository}}:{{.Tag}}" | head -2 | tail -1)
        if [ -n "$PREVIOUS_VERSION" ]; then
            sed -i "s|image: ${DOCKER_REGISTRY}/${PROJECT_NAME}-app:.*|image: ${PREVIOUS_VERSION}|" docker-compose.yml
            docker-compose up -d
        fi
    elif [ "$DEPLOYMENT_TYPE" = "kubernetes" ]; then
        kubectl rollout undo deployment/${PROJECT_NAME}-app
    fi

    log_info "Rollback completed"
}

# Main deployment function
main() {
    log_info "Starting deployment of ${PROJECT_NAME} v${VERSION} to ${ENVIRONMENT} environment"

    # Set deployment type based on environment or flag
    DEPLOYMENT_TYPE="${DEPLOYMENT_TYPE:-docker-compose}"

    case $1 in
        "build")
            check_prerequisites
            build_images
            ;;
        "push")
            push_images
            ;;
        "deploy")
            check_prerequisites
            case $DEPLOYMENT_TYPE in
                "docker-compose")
                    deploy_docker_compose
                    ;;
                "kubernetes")
                    deploy_kubernetes
                    ;;
                *)
                    log_error "Unknown deployment type: $DEPLOYMENT_TYPE"
                    exit 1
                    ;;
            esac
            run_migrations
            health_check
            ;;
        "test")
            run_tests
            ;;
        "rollback")
            rollback
            ;;
        "full")
            check_prerequisites
            build_images
            if [ "$ENVIRONMENT" = "production" ]; then
                push_images
            fi
            case $DEPLOYMENT_TYPE in
                "docker-compose")
                    deploy_docker_compose
                    ;;
                "kubernetes")
                    deploy_kubernetes
                    ;;
            esac
            run_migrations
            run_tests
            health_check
            ;;
        *)
            echo "Usage: $0 {build|push|deploy|test|rollback|full}"
            echo ""
            echo "Commands:"
            echo "  build    - Build Docker images"
            echo "  push     - Push images to registry"
            echo "  deploy   - Deploy application"
            echo "  test     - Run tests"
            echo "  rollback - Rollback deployment"
            echo "  full     - Full deployment pipeline"
            echo ""
            echo "Environment variables:"
            echo "  ENVIRONMENT        - Target environment (development/staging/production)"
            echo "  VERSION           - Docker image version tag"
            echo "  DEPLOYMENT_TYPE   - Deployment type (docker-compose/kubernetes)"
            echo "  DOCKER_REGISTRY   - Docker registry URL"
            echo "  SECRET_KEY        - Application secret key"
            echo "  DATABASE_URL      - Database connection URL"
            echo "  REDIS_URL         - Redis connection URL"
            echo "  SENTRY_DSN        - Sentry DSN for error monitoring"
            exit 1
            ;;
    esac

    log_success "Deployment operation completed successfully"
}

# Run main function with all arguments
main "$@"
