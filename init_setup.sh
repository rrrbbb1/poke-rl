#!/bin/bash

set -e

# ---- CONFIG ----
ENV_NAME="poke-rl"
ENV_FILE="environment.yml"

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Assume environment.yml is in project root
PROJECT_ROOT="$SCRIPT_DIR"

cd "$PROJECT_ROOT"

echo "******"
echo "Setting up conda environment..."

# Initialize conda for bash (important!)
eval "$(conda shell.bash hook)"

# Create env if it doesn't exist
if ! conda env list | grep -q "^$ENV_NAME "; then
    echo "Creating conda environment: $ENV_NAME"
    conda env create -f "$ENV_FILE"
else
    echo "Environment $ENV_NAME already exists"
fi

# Activate env
echo "Activating environment: $ENV_NAME"
conda activate "$ENV_NAME"

# ---- Pokémon Showdown setup ----

cd "$SCRIPT_DIR"

# Clone repo if it doesn't exist
if [ ! -d "pokemon_showdown" ]; then
    echo "Cloning Pokémon Showdown..."
    git clone https://github.com/smogon/pokemon-showdown.git pokemon_showdown
else
    echo "pokemon_showdown already exists, pulling latest changes..."
    cd pokemon_showdown
    git pull
    cd ..
fi

cd pokemon_showdown

echo "******"
echo "Installing npm dependencies..."
npm install

echo "Building Pokémon Showdown..."
npm run build

cd ..

echo "******"
echo "Setup complete!"
echo "Environment: $ENV_NAME"
echo "Showdown path: $SCRIPT_DIR/pokemon_showdown"

conda activate poke-rl