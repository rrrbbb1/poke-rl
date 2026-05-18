from battle.models import BattlePokemon, PokemonBuild, StatBlock
from data_loader.pokemon_repository import PokemonRepository
from data_loader.move_repository import MoveRepository


def print_move(move):
    accuracy = "always hits" if move.accuracy is None else f"{move.accuracy}%"

    print(
        f"- {move.name:20} "
        f"| type={move.type:10} "
        f"| class={move.damage_class:8} "
        f"| power={move.power:3} "
        f"| acc={accuracy:12} "
        f"| pp={move.pp:2} "
        f"| priority={move.priority}"
    )


def main():
    pokemon_repo = PokemonRepository()
    move_repo = MoveRepository()

    pikachu_species = pokemon_repo.get_by_name("pikachu")

    print("=== POKEMON SPECIES ===")
    print(pikachu_species)

    print("\n=== BASE STATS ===")
    print(pikachu_species.base_stats)

    pikachu_build = PokemonBuild(
        species=pikachu_species,
        level=50,
        nature="hardy",
        evs=StatBlock(
            hp=0,
            attack=0,
            defense=0,
            sp_attack=0,
            sp_defense=0,
            speed=0,
        ),
    )

    pikachu_battle = BattlePokemon(pikachu_build)

    print("\n=== FINAL STATS AT LEVEL 50 ===")
    print(pikachu_battle.stats)

    all_moves = move_repo.get_moves_for_pokemon(pikachu_species.id)
    damaging_moves = move_repo.get_damaging_moves_for_pokemon(pikachu_species.id)
    strongest_moves = move_repo.choose_strongest_moves_for_pokemon(
        pikachu_species.id,
        limit=10,
    )

    print("\n=== MOVE COUNTS ===")
    print(f"Total moves: {len(all_moves)}")
    print(f"Damaging moves: {len(damaging_moves)}")
    print(f"Status moves: {len(all_moves) - len(damaging_moves)}")

    print("\n=== FIRST 20 MOVES ===")
    for move in all_moves[:20]:
        print_move(move)

    print("\n=== TOP 10 STRONGEST DAMAGING MOVES ===")
    for move in strongest_moves:
        print_move(move)

    print("\n=== SPECIFIC MOVE: THUNDERBOLT ===")
    thunderbolt = move_repo.get_by_name("thunderbolt")
    print_move(thunderbolt)

    print("\n=== DEFAULT SELECTED MOVES FOR PIKACHU ===")
    selected_moves = move_repo.choose_strongest_moves_for_pokemon(
        pikachu_species.id,
        limit=4,
    )

    for move in selected_moves:
        print_move(move)


if __name__ == "__main__":
    main()