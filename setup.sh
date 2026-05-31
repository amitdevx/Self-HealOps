#!/bin/bash

# Exit on error
set -e

echo "========================================"
echo "    Self-HealOps Environment Setup      "
echo "========================================"
echo ""

# 1. Virtual Environment Setup
read -p "Do you want to create and use a Python virtual environment (venv)? (y/n) [y]: " create_venv
create_venv=${create_venv:-y}

PYTHON_CMD="python3"
PIP_CMD="pip3"

if [[ "$create_venv" =~ ^[Yy]$ ]]; then
    if [ ! -d "venv" ]; then
        echo "[+] Creating virtual environment in 'venv'..."
        python3 -m venv venv
    else
        echo "[+] Virtual environment 'venv' already exists."
    fi
    echo "[+] Activating virtual environment..."
    source venv/bin/activate
    PYTHON_CMD="python3"
    PIP_CMD="pip3"
else
    echo "[+] Using system Python."
fi

# 2. Install Dependencies
echo ""
echo "[+] Installing required Python packages..."
$PIP_CMD install --upgrade pip
if [ -f "requirements.txt" ]; then
    $PIP_CMD install -r requirements.txt
else
    echo "[-] requirements.txt not found! Skipping package installation."
fi

# 3. Environment Variables (.env)
echo ""
echo "========================================"
echo "    Environment Variables Setup         "
echo "========================================"
echo "Let's configure your .env file."

prompt_for_value() {
    local prompt_text=$1
    local default_value=$2
    local var_name=$3

    if [ -n "$default_value" ]; then
        read -p "$prompt_text [$default_value]: " input_value
        input_value=${input_value:-$default_value}
    else
        read -p "$prompt_text: " input_value
    fi
    eval $var_name=\"$input_value\"
}

prompt_for_value "NVIDIA API Key (Required for NIM LLM inference)" "" NVIDIA_API_KEY
prompt_for_value "GitHub Personal Access Token (Required for PRs and Commits)" "" GITHUB_TOKEN
prompt_for_value "GitHub Webhook Secret" "$(openssl rand -hex 32)" GITHUB_WEBHOOK_SECRET
prompt_for_value "Target GitHub Repository (e.g., amitdevx/OG_GROUP)" "amitdevx/OG_GROUP" GITHUB_REPO
prompt_for_value "NIM Model" "meta/llama-3.1-70b-instruct" NIM_MODEL
prompt_for_value "Database URL" "sqlite+aiosqlite:///./selfhealops.db" DATABASE_URL

echo "[+] Writing configuration to .env file..."
cat <<EOF > .env
PROJECT_NAME="SelfHealOps API"
API_V1_STR="/api/v1"
ENVIRONMENT="development"

# Database
DATABASE_URL="$DATABASE_URL"

# Redis
REDIS_HOST="localhost"
REDIS_PORT="6379"

# Security
SECRET_KEY="$(openssl rand -hex 32)"
ACCESS_TOKEN_EXPIRE_MINUTES=60

# GitHub Integration
GITHUB_TOKEN="$GITHUB_TOKEN"
GITHUB_WEBHOOK_SECRET="$GITHUB_WEBHOOK_SECRET"
GITHUB_REPO="$GITHUB_REPO"

# NVIDIA NIM Integration
NVIDIA_API_KEY="$NVIDIA_API_KEY"
NIM_MODEL="$NIM_MODEL"
EOF
echo "[+] .env file has been created successfully."

# 4. Database Initialization
echo ""
read -p "Would you like to initialize the database now? (y/n) [y]: " init_db
init_db=${init_db:-y}
if [[ "$init_db" =~ ^[Yy]$ ]]; then
    echo "[+] Initializing database..."
    export PYTHONPATH=.
    if [ -f "selfhealops.db" ]; then
        echo "[!] Found existing selfhealops.db. Backing it up to selfhealops.db.bak"
        cp selfhealops.db selfhealops.db.bak
    fi
    $PYTHON_CMD init_db.py
else
    echo "[-] Skipping database initialization."
fi

echo ""
echo "========================================"
echo "    Setup Complete!                     "
echo "========================================"
if [[ "$create_venv" =~ ^[Yy]$ ]]; then
    echo "To get started, make sure your virtual environment is active:"
    echo "    source venv/bin/activate"
fi
echo "Then, you can start testing or running the agent!"
