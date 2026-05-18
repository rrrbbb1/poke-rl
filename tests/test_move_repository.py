import json

import polars as pl
import pytest

from data_loader.move_repository import MoveRepository
from battle.models import Move


@pytest.fixture
def fake_move_repository(tmp_path):
    moves_path = tmp_path / "moves.parquet"
    pokemon_moves_path = tmp_path / "pokemon_moves.json"

    moves_df = pl.DataFrame(
        [
            {
                "move_id": 85,
                "name": "thunderbolt",
                "type": "electric",
                "damage_class": "special",
                "power": 90,
                "accuracy": 100,
                "pp": 15,
                "priority": 0,
            },
            {
                "move_id": 55,
                "name": "water-gun",
                "type": "water",
                "damage_class": "special",
                "power": 40,
                "accuracy": 100,
                "pp": 25,
                "priority": 0,
            },
            {
                "move_id": 98,
                "name": "quick-attack",
                "type": "normal",
                "damage_class": "physical",
                "power": 40,
                "accuracy": 100,
                "pp": 30,
                "priority": 1,
            },
            {
                "move_id": 45,
                "name": "growl",
                "type": "normal",
                "damage_class": "status",
                "power": 0,
                "accuracy": 100,
                "pp": 40,
                "priority": 0,
            },
            {
                "move_id": 129,
                "name": "swift",
                "type": "normal",
                "damage_class": "special",
                "power": 60,
                "accuracy": None,
                "pp": 20,
                "priority": 0,
            },
        ],
        schema={
            "move_id": pl.Int64,
            "name": pl.String,
            "type": pl.String,
            "damage_class": pl.String,
            "power": pl.Int64,
            "accuracy": pl.Int64,
            "pp": pl.Int64,
            "priority": pl.Int64,
        },
    )

    moves_df.write_parquet(moves_path)

    pokemon_moves = {
        "25": [85, 98, 45, 129],  # Pikachu
        "7": [55, 45],            # Squirtle
    }

    with open(pokemon_moves_path, "w") as file:
        json.dump(pokemon_moves, file)

    return MoveRepository(
        moves_path=moves_path,
        pokemon_moves_path=pokemon_moves_path,
    )


def test_get_move_by_id(fake_move_repository):
    move = fake_move_repository.get_by_id(85)

    assert isinstance(move, Move)
    assert move.move_id == 85
    assert move.name == "thunderbolt"
    assert move.type == "electric"
    assert move.damage_class == "special"
    assert move.power == 90
    assert move.accuracy == 100
    assert move.pp == 15
    assert move.priority == 0


def test_get_move_by_name(fake_move_repository):
    move = fake_move_repository.get_by_name("thunderbolt")

    assert move.move_id == 85
    assert move.name == "thunderbolt"


def test_get_move_by_name_normalizes_spaces_and_case(fake_move_repository):
    move = fake_move_repository.get_by_name(" Water Gun ")

    assert move.move_id == 55
    assert move.name == "water-gun"


def test_get_by_id_unknown_move_raises_error(fake_move_repository):
    with pytest.raises(ValueError):
        fake_move_repository.get_by_id(9999)


def test_get_by_name_unknown_move_raises_error(fake_move_repository):
    with pytest.raises(ValueError):
        fake_move_repository.get_by_name("unknown-move")


def test_get_move_ids_for_pokemon(fake_move_repository):
    move_ids = fake_move_repository.get_move_ids_for_pokemon(25)

    assert move_ids == [85, 98, 45, 129]


def test_get_move_ids_for_unknown_pokemon_raises_error(fake_move_repository):
    with pytest.raises(ValueError):
        fake_move_repository.get_move_ids_for_pokemon(9999)


def test_get_moves_for_pokemon(fake_move_repository):
    moves = fake_move_repository.get_moves_for_pokemon(25)

    move_names = [move.name for move in moves]

    assert move_names == [
        "thunderbolt",
        "quick-attack",
        "growl",
        "swift",
    ]


def test_get_damaging_moves_for_pokemon_excludes_status_moves(fake_move_repository):
    moves = fake_move_repository.get_damaging_moves_for_pokemon(25)

    move_names = [move.name for move in moves]

    assert "thunderbolt" in move_names
    assert "quick-attack" in move_names
    assert "swift" in move_names
    assert "growl" not in move_names


def test_choose_strongest_moves_for_pokemon(fake_move_repository):
    moves = fake_move_repository.choose_strongest_moves_for_pokemon(
        pokemon_id=25,
        limit=2,
    )

    move_names = [move.name for move in moves]

    assert move_names == ["thunderbolt", "swift"]


def test_move_with_none_accuracy_is_loaded_as_none(fake_move_repository):
    move = fake_move_repository.get_by_name("swift")

    assert move.accuracy is None
    assert move.is_damaging()