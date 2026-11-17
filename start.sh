#!/bin/bash

set -e

# Always run from the project directory
cd "$(dirname "$0")"

echo "Starting TaxiTech Solutions..."

# Create virtual environment if needed
if [ ! -d ".venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Install project dependencies
echo "Checking dependencies..."
python -m pip install -r requirements.txt

# Generate Flask secret key if missing
if [ ! -f ".secret_key" ]; then
    echo "Generating Flask secret key..."
    python -c "import secrets; print(secrets.token_hex(32))" > .secret_key
    chmod 600 .secret_key
fi

# Create login password on first run
if [ ! -f "auth.json" ]; then
    echo "First-time login setup:"
    python -c "from auth import Auth; Auth().login()"
fi

# Start the web application on the local network
echo "TaxiTech is starting on port 5001"
exec gunicorn --bind 0.0.0.0:5001 --workers 1 api:app
