#!/bin/bash
set -e

echo "======================================================================"
echo "SwiftQueue Container Startup"
echo "======================================================================"
echo "User: $(whoami)"
echo "Working Directory: $(pwd)"
echo "Python Version: $(python --version)"
echo "======================================================================"

echo "Checking directory contents..."
ls -la

echo ""
echo "Checking if run.py exists..."
if [ -f "run.py" ]; then
    echo "✓ run.py found"
else
    echo "✗ run.py NOT FOUND"
    exit 1
fi

echo ""
echo "Checking if app directory exists..."
if [ -d "app" ]; then
    echo "✓ app directory found"
    ls -la app/ | head -10
else
    echo "✗ app directory NOT FOUND"
    exit 1
fi

echo ""
echo "Checking if dist directory exists..."
if [ -d "dist" ]; then
    echo "✓ dist directory found"
    ls -la dist/
else
    echo "⚠ dist directory NOT FOUND (frontend won't be served)"
fi

echo ""
echo "Checking Python imports..."
python -c "import sys; print('Python path:', sys.path)" || exit 1
python -c "import fastapi; print('✓ FastAPI imported')" || exit 1
python -c "import uvicorn; print('✓ Uvicorn imported')" || exit 1
python -c "import sqlalchemy; print('✓ SQLAlchemy imported')" || exit 1

echo ""
echo "======================================================================"
echo "Environment looks good! Starting application..."
echo "======================================================================"
echo ""

# Execute the main command (run.py)
exec python -u run.py
