#!/bin/bash

# Directory name for the virtual environment
ENV_DIR=".venv"

# Check if the directory already exists
if [ ! -d "$ENV_DIR" ]; then
    # Create the virtual environment if it does not exist
    python -m venv $ENV_DIR
    echo "Virtual environment '$ENV_DIR' has been created."
    
    # Install libraries from requirements.txt if it exists
    if [ -f "requirements.txt" ]; then
        source "$ENV_DIR/bin/activate"  # Activate the virtual environment
        pip install -r requirements.txt
        echo "Installed libraries from 'requirements.txt'."
    else
        echo "'requirements.txt' not found. No libraries installed."
    fi
else
    echo "Virtual environment '$ENV_DIR' already exists."
fi

# Activate the virtual environment
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    source "$ENV_DIR/bin/activate"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    source "$ENV_DIR/bin/activate"
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    # Windows (Git Bash or Cygwin)
    source "$ENV_DIR/Scripts/activate"
else
    echo "Unsupported operating system."
    exit 1
fi

echo "Virtual environment '$ENV_DIR' has been activated."
