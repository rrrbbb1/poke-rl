from pathlib import Path
import json

import polars as pl

from battle.models import Move

# charge les information d'une attaque de moves.parquet et le transforme dans le format du programme

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"


class MoveRepository:
    def __init__(
        self,
        moves_path: Path | None = None,
        pokemon_moves_path: Path | None = None,
    ):
        if moves_path is None:
            moves_path = DATA_DIR / "moves.parquet"

        if pokemon_moves_path is None:
            pokemon_moves_path = DATA_DIR / "pokemon_moves.json"

        self.moves_path = moves_path
        self.pokemon_moves_path = pokemon_moves_path

        self.df = pl.read_parquet(self.moves_path)

        with open(self.pokemon_moves_path, "r") as file:
            self.pokemon_moves = json.load(file)

    def get_by_id(self, move_id: int) -> Move:
        result = self.df.filter(pl.col("move_id") == move_id)

        if result.height == 0:
            raise ValueError(f"No move found with id: {move_id}")

        row = result.row(0, named=True)
        return self._row_to_move(row)

    def get_by_name(self, name: str) -> Move:
        normalized_name = self._normalize_name(name)

        result = self.df.filter(pl.col("name") == normalized_name)

        if result.height == 0:
            raise ValueError(f"No move found with name: {name}")

        row = result.row(0, named=True)
        return self._row_to_move(row)

    def get_move_ids_for_pokemon(self, pokemon_id: int) -> list[int]:
        key = str(pokemon_id)

        if key not in self.pokemon_moves:
            raise ValueError(f"No moves found for Pokémon id: {pokemon_id}")

        return self.pokemon_moves[key]

    def get_moves_for_pokemon(self, pokemon_id: int) -> list[Move]:
        move_ids = self.get_move_ids_for_pokemon(pokemon_id)

        moves = []

        for move_id in move_ids:
            try:
                moves.append(self.get_by_id(move_id))
            except ValueError:
                pass

        return moves

    def get_damaging_moves_for_pokemon(self, pokemon_id: int) -> list[Move]:
        moves = self.get_moves_for_pokemon(pokemon_id)

        return [
            move
            for move in moves
            if move.is_damaging()
        ]

    def choose_strongest_moves_for_pokemon(self, pokemon_id: int, limit: int = 4) -> list[Move]:
        moves = self.get_damaging_moves_for_pokemon(pokemon_id)

        moves.sort(
            key=lambda move: (
                move.power,
                move.accuracy if move.accuracy is not None else 100,
            ),
            reverse=True,
        )

        return moves[:limit]

    def _row_to_move(self, row: dict) -> Move:
        return Move(
            move_id=int(row["move_id"]),
            name=row["name"],
            type=row["type"],
            damage_class=row["damage_class"],
            power=int(row["power"] or 0),
            accuracy=None if row["accuracy"] is None else int(row["accuracy"]),
            pp=int(row["pp"] or 0),
            priority=int(row["priority"] or 0),
        )

    def _normalize_name(self, name: str) -> str:
        return name.strip().lower().replace(" ", "-")