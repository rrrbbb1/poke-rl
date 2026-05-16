# Pokémon RL Dataset Builder

This project builds structured datasets from the PokéAPI to support **Reinforcement Learning (RL)** for Pokémon battles.

It extracts:
- Pokémon stats and types
- Learnable move mappings
- Detailed move mechanics (damage, effects, stat changes, etc.)

The output is optimized for fast loading and modeling using **Parquet** and **JSON** formats.

---

# Installation

## 1. Create Conda environment & install dependencies

Run
    bash init_setup.sh

## 2. Get data

Run the scraper using:
    python src/scraper/main.py
A folder data should be created at the root of the project.
At the end of the process you should get:
    data/
        - pokemon_stats.parquet
        - moves.parquet
        - pokemon_moves.json
