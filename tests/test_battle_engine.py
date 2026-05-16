from battle.battle_engine import BattleEngine, BattleState
from battle.models import BattlePokemon, Move, PokemonBuild, PokemonSpecies, StatBlock


def test_faster_pokemon_attacks_first():
    pikachu_species = PokemonSpecies(
        id=25,
        name="pikachu",
        type1="electric",
        type2=None,
        base_stats=StatBlock(
            hp=35,
            attack=55,
            defense=40,
            sp_attack=50,
            sp_defense=50,
            speed=90,
        ),
    )

    squirtle_species = PokemonSpecies(
        id=7,
        name="squirtle",
        type1="water",
        type2=None,
        base_stats=StatBlock(
            hp=44,
            attack=48,
            defense=65,
            sp_attack=50,
            sp_defense=64,
            speed=43,
        ),
    )

    thunderbolt = Move(
        move_id=85,
        name="thunderbolt",
        type="electric",
        damage_class="special",
        power=90,
        accuracy=100,
        pp=15,
    )

    water_gun = Move(
        move_id=55,
        name="water-gun",
        type="water",
        damage_class="special",
        power=40,
        accuracy=100,
        pp=25,
    )

    pikachu = BattlePokemon(
        PokemonBuild(
            species=pikachu_species,
            level=50,
            moves=[thunderbolt],
        )
    )

    squirtle = BattlePokemon(
        PokemonBuild(
            species=squirtle_species,
            level=50,
            moves=[water_gun],
        )
    )

    state = BattleState(
        pokemon1=pikachu,
        pokemon2=squirtle,
    )

    engine = BattleEngine()

    result = engine.execute_turn(
        state=state,
        move1=thunderbolt,
        move2=water_gun,
    )

    assert result.events[0].attacker_name == "pikachu"

