#!/bin/bash

# SwiftQueue Deployment Script
# Author: SwiftQueue Team
# Description: Automated deployment script for production

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="swiftqueue"
DOCKER_REGISTRY="${DOCKER_REGISTRY:-docker.io}"
IMAGE_TAG="${IMAGE_TAG:-latest}"
ENVIRONMENT="${ENVIRONMENT:-production}"

echo -e "${GREEN}====================================${NC}"
echo -e "${GREEN}SwiftQueue Deployment Script${NC}"
echo -e "${GREEN}Environment: ${ENVIRONMENT}${NC}"
echo -e "${GREEN}====================================${NC}"

# Function to check prerequisites
check_prerequisites() {
    echo -e "${YELLOW}Checking prerequisites...${NC}"
    
    command -v docker >/dev/null 2>&1 || { echo -e "${RED}Docker is not installed${NC}" >&2; exit 1; }
    command -v kubectl >/dev/null 2>&1 || { echo -e "${RED}kubectl is not installed${NC}" >&2; exit 1; }
    
    echo -e "${GREEN}✓ Prerequisites check passed${NC}"
}

# Function to build Docker images
build_images() {
    echo -e "${YELLOW}Building Docker images...${NC}"
    
    # Build backend
    docker build -t ${DOCKER_REGISTRY}/${APP_NAME}/backend:${IMAGE_TAG} \
        --target backend \
        -f Dockerfile .
    
    # Build frontend
    docker build -t ${DOCKER_REGISTRY}/${APP_NAME}/frontend:${IMAGE_TAG} \
        --target frontend-build \
        -f Dockerfile .
    
    echo -e "${GREEN}✓ Docker images built successfully${NC}"
}

# Function to push Docker images
push_images() {
    echo -e "${YELLOW}Pushing Docker images to registry...${NC}"
    
    docker push ${DOCKER_REGISTRY}/${APP_NAME}/backend:${IMAGE_TAG}
    docker push ${DOCKER_REGISTRY}/${APP_NAME}/frontend:${IMAGE_TAG}
    
    echo -e "${GREEN}✓ Images pushed successfully${NC}"
}

# Function to run database migrations
run_migrations() {
    echo -e "${YELLOW}Running database migrations...${NC}"
    
    kubectl exec -it $(kubectl get pod -l app=${APP_NAME},component=backend -o jsonpath='{.items[0].metadata.name}') \
        -- alembic upgrade head
    
    echo -e "${GREEN}✓ Migrations completed${NC}"
}

# Function to deploy to Kubernetes
deploy_k8s() {
    echo -e "${YELLOW}Deploying to Kubernetes...${NC}"
    
    # Apply ConfigMaps and Secrets
    kubectl apply -f k8s/configmap-secrets.yaml
    
    # Apply deployments
    kubectl apply -f k8s/backend-deployment.yaml
    kubectl apply -f k8s/frontend-deployment.yaml
    
    # Apply ingress
    kubectl apply -f k8s/ingress.yaml
    
    # Wait for rollout
    kubectl rollout status deployment/${APP_NAME}-backend
    kubectl rollout status deployment/${APP_NAME}-frontend
    
    echo -e "${GREEN}✓ Deployment completed${NC}"
}

# Function to run health checks
health_check() {
    echo -e "${YELLOW}Running health checks...${NC}"
    
    BACKEND_URL=$(kubectl get ingress ${APP_NAME}-ingress -o jsonpath='{.spec.rules[0].host}')
    
    for i in {1..10}; do
        if curl -f -s "https://${BACKEND_URL}/health" > /dev/null; then
            echo -e "${GREEN}✓ Health check passed${NC}"
            return 0
        fi
        echo "Waiting for service to be ready... ($i/10)"
        sleep 5
    done
    
    echo -e "${RED}✗ Health check failed${NC}"
    return 1
}

# Function to rollback deployment
rollback() {
    echo -e "${RED}Rolling back deployment...${NC}"
    
    kubectl rollout undo deployment/${APP_NAME}-backend
    kubectl rollout undo deployment/${APP_NAME}-frontend
    
    echo -e "${YELLOW}Rollback completed${NC}"
}

# Main deployment flow
main() {
    check_prerequisites
    
    # Build and push images
    if [[ "${SKIP_BUILD}" != "true" ]]; then
        build_images
        push_images
    fi
    
    # Deploy to Kubernetes
    deploy_k8s
    
    # Run migrations
    if [[ "${SKIP_MIGRATIONS}" != "true" ]]; then
        run_migrations
    fi
    
    # Health check
    if ! health_check; then
        echo -e "${RED}Deployment failed health check${NC}"
        
        if [[ "${AUTO_ROLLBACK}" == "true" ]]; then
            rollback
        fi
        exit 1
    fi
    
    echo -e "${GREEN}====================================${NC}"
    echo -e "${GREEN}Deployment completed successfully!${NC}"
    echo -e "${GREEN}====================================${NC}"
}

# Trap errors and rollback
trap 'rollback' ERR

# Run main function
main "$@"
