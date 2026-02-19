# ApplyFlow Backend - Environment Setup with WSL + Conda

## ✅ Prerequisites

- Windows with WSL2 installed
- Conda (Miniconda or Anaconda) in WSL
- PostgreSQL in WSL

## 🐧 WSL Setup

### 1. Install/Enable WSL2

```powershell
# In Windows PowerShell (as Administrator)
wsl --install
# Or update to WSL2
wsl --set-default-version 2
```

### 2. Install Ubuntu (or your preferred distro)

```powershell
wsl --install -d Ubuntu-22.04
```

### 3. Access WSL

```powershell
wsl
```

## 🐍 Conda Setup in WSL

### Install Miniconda (if not already installed)

```bash
# In WSL terminal
cd ~
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh

# Follow prompts, then restart shell or:
source ~/.bashrc
```

### Verify Conda Installation

```bash
conda --version
# Should show: conda 23.x.x or similar
```

## 🚀 Project Setup

### 1. Navigate to Project (in WSL)

```bash
# Your Windows C:\ drive is mounted at /mnt/c/ in WSL
cd /mnt/c/projets/ApplyFlow/backend
```

### 2. Create Conda Environment

```bash
# Create environment with Python 3.11
conda create -n applyflow python=3.11 -y

# Activate environment
conda activate applyflow
```

### 3. Install Dependencies

```bash
# Install pip packages
pip install -r requirements.txt

# Or install with conda when possible
conda install -c conda-forge fastapi uvicorn sqlalchemy psycopg2 alembic pydantic -y
pip install -r requirements.txt  # For remaining packages
```

## 🗄️ PostgreSQL Setup in WSL

### Install PostgreSQL

```bash
# Update package list
sudo apt update

# Install PostgreSQL
sudo apt install postgresql postgresql-contrib -y

# Start PostgreSQL service
sudo service postgresql start
```

### Configure PostgreSQL

```bash
# Switch to postgres user
sudo -u postgres psql

# In PostgreSQL prompt:
# Create user
CREATE USER applyflow_user WITH PASSWORD 'your_secure_password';

# Create database
CREATE DATABASE applyflow_db OWNER applyflow_user;

# Grant privileges
GRANT ALL PRIVILEGES ON DATABASE applyflow_db TO applyflow_user;

# Exit
\q
```

### Auto-start PostgreSQL (optional)

```bash
# Add to ~/.bashrc
echo 'sudo service postgresql start' >> ~/.bashrc
```

## ⚙️ Environment Configuration

### 1. Copy environment template

```bash
cp .env.example .env
```

### 2. Edit .env file

```bash
# Use nano or vim
nano .env
```

Update with your settings:

```env
# Database - Use localhost since PostgreSQL is in WSL
DATABASE_URL=postgresql://applyflow_user:your_secure_password@localhost:5432/applyflow_db

# SMTP Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM=your-email@gmail.com

# OpenAI API (optional)
OPENAI_API_KEY=sk-your-key-here

# Application
DEBUG=True
GENERATED_DOCS_PATH=./generated_docs
```

Save: `Ctrl+O`, `Enter`, `Ctrl+X`

## 🏃 Running the Application

### Start the Server

```bash
# Make sure conda environment is activated
conda activate applyflow

# Navigate to backend directory
cd /mnt/c/projets/ApplyFlow/backend

# Start with uvicorn
uvicorn app.main:app --reload --host 0.0.0.0
```

### Access from Windows

- API: http://localhost:8000
- Docs: http://localhost:8000/docs

## 🗃️ Database Migrations

```bash
# Ensure conda environment is activated
conda activate applyflow

# Generate initial migration
python migrate.py

# Or manually:
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

## 🌱 Seed Sample Data

```bash
conda activate applyflow
python seed_data.py
```

## 📝 Daily Workflow

### Start Development Session

```bash
# 1. Open WSL terminal (Windows Terminal or wsl command)
wsl

# 2. Start PostgreSQL (if not auto-started)
sudo service postgresql start

# 3. Navigate to project
cd /mnt/c/projets/ApplyFlow/backend

# 4. Activate conda environment
conda activate applyflow

# 5. Start server
uvicorn app.main:app --reload --host 0.0.0.0
```

### Quick Start Script

Create `start.sh` in the backend folder:

```bash
#!/bin/bash
# start.sh - Quick start script

# Start PostgreSQL
sudo service postgresql start

# Activate conda environment
source ~/miniconda3/etc/profile.d/conda.sh
conda activate applyflow

# Start server
uvicorn app.main:app --reload --host 0.0.0.0
```

Make it executable:

```bash
chmod +x start.sh
```

Then just run:

```bash
./start.sh
```

## 🛠️ Useful Commands

### Conda Environment Management

```bash
# List all environments
conda env list

# Activate environment
conda activate applyflow

# Deactivate environment
conda deactivate

# Update packages
conda update --all

# Export environment
conda env export > environment.yml

# Create from environment file
conda env create -f environment.yml
```

### PostgreSQL Management

```bash
# Start PostgreSQL
sudo service postgresql start

# Stop PostgreSQL
sudo service postgresql stop

# Check status
sudo service postgresql status

# Connect to database
psql -U applyflow_user -d applyflow_db

# Backup database
pg_dump -U applyflow_user applyflow_db > backup.sql

# Restore database
psql -U applyflow_user applyflow_db < backup.sql
```

### WSL Commands (from Windows PowerShell)

```powershell
# Start WSL
wsl

# Run command in WSL
wsl -e bash -c "cd /mnt/c/projets/ApplyFlow/backend && conda activate applyflow && uvicorn app.main:app"

# Shutdown WSL
wsl --shutdown

# List running distributions
wsl -l -v
```

## 🐛 Troubleshooting

### PostgreSQL Connection Issues

```bash
# Check if PostgreSQL is running
sudo service postgresql status

# Restart PostgreSQL
sudo service postgresql restart

# Check port
sudo netstat -nlp | grep 5432
```

### Conda Environment Issues

```bash
# Reinitialize conda
conda init bash
source ~/.bashrc

# Recreate environment
conda env remove -n applyflow
conda create -n applyflow python=3.11 -y
conda activate applyflow
pip install -r requirements.txt
```

### Permission Issues

```bash
# Fix ownership (if needed)
sudo chown -R $USER:$USER /mnt/c/projets/ApplyFlow/backend

# Fix PostgreSQL permissions
sudo -u postgres psql
GRANT ALL PRIVILEGES ON DATABASE applyflow_db TO applyflow_user;
```

### Port Already in Use

```bash
# Find process using port 8000
sudo lsof -i :8000

# Kill process
sudo kill -9 <PID>
```

## 💡 Tips

1. **Windows Terminal**: Install Windows Terminal for better WSL experience
   ```powershell
   winget install Microsoft.WindowsTerminal
   ```

2. **VS Code with WSL**: Open project in VS Code from WSL
   ```bash
   code /mnt/c/projets/ApplyFlow/backend
   ```

3. **Conda in VS Code**: Select conda environment in VS Code
   - `Ctrl+Shift+P` → "Python: Select Interpreter"
   - Choose conda environment: `applyflow`

4. **Auto-activate Conda**: Add to `~/.bashrc`
   ```bash
   # Auto-activate applyflow when in project directory
   if [[ $(pwd) == /mnt/c/projets/ApplyFlow/backend* ]]; then
       conda activate applyflow
   fi
   ```

## 📊 Performance Considerations

### WSL2 File System Performance

For better performance, consider keeping the project in WSL filesystem:

```bash
# Copy project to WSL home directory
cp -r /mnt/c/projets/ApplyFlow ~/ApplyFlow

# Work from WSL filesystem
cd ~/ApplyFlow/backend
```

Access from Windows: `\\wsl$\Ubuntu-22.04\home\yourusername\ApplyFlow`

## 🔄 Updating Dependencies

```bash
# Update conda packages
conda update --all

# Update pip packages
pip install --upgrade -r requirements.txt

# Or update specific package
pip install --upgrade fastapi
```

## ✅ Verification Checklist

After setup, verify everything works:

```bash
# 1. Conda environment
conda activate applyflow
python --version  # Should show Python 3.11.x

# 2. PostgreSQL
psql -U applyflow_user -d applyflow_db -c "SELECT version();"

# 3. Dependencies
python -c "import fastapi; import sqlalchemy; print('OK')"

# 4. Run migrations
alembic current

# 5. Start server
uvicorn app.main:app --reload
# Visit http://localhost:8000/docs
```

## 🎯 Next Steps

1. ✅ WSL2 installed and running
2. ✅ Conda environment created and activated
3. ✅ PostgreSQL installed and configured
4. ✅ Dependencies installed
5. ✅ Database migrations applied
6. ✅ Server running
7. 🎉 Start developing!

---

**Need help?** Check the main README.md for API documentation and usage examples.
