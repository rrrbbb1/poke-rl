from pathlib import Path

import polars as pl

from battle.models import PokemonSpecies, StatBlock

# charge les information d'un pokemon de pokemon_stats.parquet et le transforme dans le format du programme

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"


class PokemonRepository:
    def __init__(self, pokemon_stats_path: Path | None = None):
        if pokemon_stats_path is None:
            pokemon_stats_path = DATA_DIR / "pokemon_stats.parquet"

        self.pokemon_stats_path = pokemon_stats_path
        self.df = pl.read_parquet(self.pokemon_stats_path)

    def get_by_id(self, pokemon_id: int) -> PokemonSpecies:
        result = self.df.filter(pl.col("id") == pokemon_id)

        if result.height == 0:
            raise ValueError(f"No Pokémon found with id: {pokemon_id}")

        row = result.row(0, named=True)
        return self._row_to_species(row)

    def get_by_name(self, name: str) -> PokemonSpecies:
        normalized_name = self._normalize_name(name)

        result = self.df.filter(pl.col("name") == normalized_name)

        if result.height == 0:
            raise ValueError(f"No Pokémon found with name: {name}")

        row = result.row(0, named=True)
        return self._row_to_species(row)

    def list_names(self) -> list[str]:
        return self.df["name"].to_list()

    def _row_to_species(self, row: dict) -> PokemonSpecies:
        return PokemonSpecies(
            id=int(row["id"]),
            name=row["name"],
            type1=row["type1"],
            type2=row["type2"],
            base_stats=StatBlock(
                hp=int(row["hp"]),
                attack=int(row["attack"]),
                defense=int(row["defense"]),
                sp_attack=int(row["sp_attack"]),
                sp_defense=int(row["sp_defense"]),
                speed=int(row["speed"]),
            ),
        )

    def _normalize_name(self, name: str) -> str:
        return name.strip().lower().replace(" ", "-")