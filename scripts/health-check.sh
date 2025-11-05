#!/bin/bash

# SwiftQueue Health Check Script
# Monitors the health of all services

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuration
BACKEND_URL="${BACKEND_URL:-http://localhost:8000}"
FRONTEND_URL="${FRONTEND_URL:-http://localhost:5173}"
REDIS_HOST="${REDIS_HOST:-localhost}"
REDIS_PORT="${REDIS_PORT:-6379}"
POSTGRES_HOST="${POSTGRES_HOST:-localhost}"
POSTGRES_PORT="${POSTGRES_PORT:-5432}"

echo -e "${YELLOW}Running SwiftQueue Health Checks...${NC}\n"

# Check Backend API
check_backend() {
    echo -n "Backend API... "
    if curl -f -s "${BACKEND_URL}/health" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Healthy${NC}"
        return 0
    else
        echo -e "${RED}✗ Unhealthy${NC}"
        return 1
    fi
}

# Check Frontend
check_frontend() {
    echo -n "Frontend... "
    if curl -f -s "${FRONTEND_URL}" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Healthy${NC}"
        return 0
    else
        echo -e "${RED}✗ Unhealthy${NC}"
        return 1
    fi
}

# Check Redis
check_redis() {
    echo -n "Redis... "
    if redis-cli -h "${REDIS_HOST}" -p "${REDIS_PORT}" ping > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Healthy${NC}"
        return 0
    else
        echo -e "${RED}✗ Unhealthy${NC}"
        return 1
    fi
}

# Check PostgreSQL
check_postgres() {
    echo -n "PostgreSQL... "
    if pg_isready -h "${POSTGRES_HOST}" -p "${POSTGRES_PORT}" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Healthy${NC}"
        return 0
    else
        echo -e "${RED}✗ Unhealthy${NC}"
        return 1
    fi
}

# Check API response time
check_response_time() {
    echo -n "API Response Time... "
    RESPONSE_TIME=$(curl -o /dev/null -s -w '%{time_total}' "${BACKEND_URL}/health")
    
    if (( $(echo "$RESPONSE_TIME < 1" | bc -l) )); then
        echo -e "${GREEN}✓ ${RESPONSE_TIME}s${NC}"
        return 0
    elif (( $(echo "$RESPONSE_TIME < 2" | bc -l) )); then
        echo -e "${YELLOW}⚠ ${RESPONSE_TIME}s (Slow)${NC}"
        return 0
    else
        echo -e "${RED}✗ ${RESPONSE_TIME}s (Too Slow)${NC}"
        return 1
    fi
}

# Run all checks
FAILED=0

check_backend || FAILED=$((FAILED + 1))
check_frontend || FAILED=$((FAILED + 1))
check_redis || FAILED=$((FAILED + 1))
check_postgres || FAILED=$((FAILED + 1))
check_response_time || FAILED=$((FAILED + 1))

echo ""
if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}All health checks passed!${NC}"
    exit 0
else
    echo -e "${RED}${FAILED} health check(s) failed!${NC}"
    exit 1
fi
