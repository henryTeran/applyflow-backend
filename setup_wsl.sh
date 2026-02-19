#!/bin/bash
# Setup script for ApplyFlow backend with WSL + Conda
# This script automates the initial setup process

set -e  # Exit on error

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "======================================"
echo "🚀 ApplyFlow Backend Setup (WSL+Conda)"
echo "======================================"
echo ""

# Check if running in WSL
if ! grep -qi microsoft /proc/version; then
    echo -e "${RED}❌ This script must be run in WSL (Windows Subsystem for Linux)${NC}"
    exit 1
fi

# Check if conda is installed
if ! command -v conda &> /dev/null; then
    echo -e "${RED}❌ Conda is not installed${NC}"
    echo "Install Miniconda with:"
    echo "  wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh"
    echo "  bash Miniconda3-latest-Linux-x86_64.sh"
    exit 1
fi

echo -e "${GREEN}✅ WSL detected${NC}"
echo -e "${GREEN}✅ Conda found: $(conda --version)${NC}"
echo ""

# Step 1: Create conda environment
echo -e "${BLUE}📦 Step 1: Creating conda environment...${NC}"
if conda env list | grep -q "applyflow"; then
    echo -e "${YELLOW}⚠️  Environment 'applyflow' already exists${NC}"
    read -p "Do you want to recreate it? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        conda env remove -n applyflow -y
        conda env create -f environment.yml
    fi
else
    conda env create -f environment.yml
fi
echo -e "${GREEN}✅ Conda environment ready${NC}"
echo ""

# Step 2: Check PostgreSQL
echo -e "${BLUE}📊 Step 2: Checking PostgreSQL...${NC}"
if ! command -v psql &> /dev/null; then
    echo -e "${YELLOW}⚠️  PostgreSQL not found. Installing...${NC}"
    sudo apt update
    sudo apt install -y postgresql postgresql-contrib
fi

# Start PostgreSQL
if ! sudo service postgresql status > /dev/null 2>&1; then
    echo "Starting PostgreSQL..."
    sudo service postgresql start
fi
echo -e "${GREEN}✅ PostgreSQL is running${NC}"
echo ""

# Step 3: Setup database
echo -e "${BLUE}🗄️  Step 3: Database setup${NC}"
read -p "Do you want to create the database? (Y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    read -p "Database name [applyflow_db]: " DB_NAME
    DB_NAME=${DB_NAME:-applyflow_db}
    
    read -p "Database user [applyflow_user]: " DB_USER
    DB_USER=${DB_USER:-applyflow_user}
    
    read -s -p "Database password: " DB_PASS
    echo
    
    sudo -u postgres psql << EOF
-- Create user if not exists
DO \$\$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_user WHERE usename = '${DB_USER}') THEN
        CREATE USER ${DB_USER} WITH PASSWORD '${DB_PASS}';
    END IF;
END
\$\$;

-- Create database if not exists
SELECT 'CREATE DATABASE ${DB_NAME} OWNER ${DB_USER}'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '${DB_NAME}')\gexec

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE ${DB_NAME} TO ${DB_USER};
EOF
    
    echo -e "${GREEN}✅ Database created${NC}"
fi
echo ""

# Step 4: Configure environment
echo -e "${BLUE}⚙️  Step 4: Environment configuration${NC}"
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env
    
    # Update DATABASE_URL if database was created
    if [ ! -z "$DB_NAME" ]; then
        sed -i "s|DATABASE_URL=.*|DATABASE_URL=postgresql://${DB_USER}:${DB_PASS}@localhost:5432/${DB_NAME}|" .env
    fi
    
    echo -e "${YELLOW}⚠️  Please edit .env file with your SMTP and other settings${NC}"
    echo "Important: Update SMTP_* variables for email functionality"
else
    echo -e "${GREEN}✅ .env file already exists${NC}"
fi
echo ""

# Step 5: Create generated_docs directory
echo -e "${BLUE}📁 Step 5: Creating directories...${NC}"
mkdir -p generated_docs
echo -e "${GREEN}✅ Directories created${NC}"
echo ""

# Step 6: Run migrations
echo -e "${BLUE}🔄 Step 6: Database migrations${NC}"
read -p "Do you want to run migrations now? (Y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    # Activate conda environment
    source ~/miniconda3/etc/profile.d/conda.sh || source ~/anaconda3/etc/profile.d/conda.sh
    conda activate applyflow
    
    # Run migration script
    python migrate.py
fi
echo ""

# Step 7: Seed data
echo -e "${BLUE}🌱 Step 7: Sample data${NC}"
read -p "Do you want to load sample data? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    source ~/miniconda3/etc/profile.d/conda.sh || source ~/anaconda3/etc/profile.d/conda.sh
    conda activate applyflow
    python seed_data.py
fi
echo ""

# Make scripts executable
chmod +x start.sh

# Final summary
echo "======================================"
echo -e "${GREEN}✅ Setup Complete!${NC}"
echo "======================================"
echo ""
echo "📝 Next steps:"
echo "1. Edit .env file with your settings (especially SMTP)"
echo "2. Start the server:"
echo "   ./start.sh"
echo ""
echo "   Or manually:"
echo "   conda activate applyflow"
echo "   uvicorn app.main:app --reload"
echo ""
echo "3. Visit http://localhost:8000/docs"
echo ""
echo "📚 Documentation:"
echo "   - SETUP_WSL_CONDA.md - Detailed setup guide"
echo "   - README.md - Full documentation"
echo "   - QUICKSTART.md - Quick start guide"
echo ""
echo "🎉 Happy coding!"
