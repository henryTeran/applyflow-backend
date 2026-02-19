#!/bin/bash
# Quick start script for ApplyFlow backend
# Usage: ./start.sh

set -e  # Exit on error

echo "🚀 Starting ApplyFlow Backend..."
echo "================================"

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if PostgreSQL is running
echo -e "${BLUE}📊 Checking PostgreSQL...${NC}"
if ! sudo service postgresql status > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  PostgreSQL not running. Starting...${NC}"
    sudo service postgresql start
    sleep 2
fi
echo -e "${GREEN}✅ PostgreSQL is running${NC}"

# Initialize conda
echo -e "${BLUE}🐍 Initializing Conda...${NC}"
source ~/miniconda3/etc/profile.d/conda.sh || source ~/anaconda3/etc/profile.d/conda.sh

# Activate conda environment
echo -e "${BLUE}🔄 Activating conda environment 'applyflow'...${NC}"
conda activate applyflow

# Check if environment is activated
if [[ "$CONDA_DEFAULT_ENV" != "applyflow" ]]; then
    echo -e "${YELLOW}⚠️  Failed to activate conda environment${NC}"
    echo "Create it with: conda env create -f environment.yml"
    exit 1
fi
echo -e "${GREEN}✅ Conda environment activated${NC}"

# Check database connection
echo -e "${BLUE}🗄️  Checking database connection...${NC}"
if python -c "from app.database import engine; engine.connect()" 2>/dev/null; then
    echo -e "${GREEN}✅ Database connection OK${NC}"
else
    echo -e "${YELLOW}⚠️  Database connection failed. Check your .env file${NC}"
fi

# Start the server
echo ""
echo "================================"
echo -e "${GREEN}🎯 Starting FastAPI server...${NC}"
echo "================================"
echo ""
echo "📍 API: http://localhost:8000"
echo "📚 Docs: http://localhost:8000/docs"
echo "🔍 ReDoc: http://localhost:8000/redoc"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Start uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
