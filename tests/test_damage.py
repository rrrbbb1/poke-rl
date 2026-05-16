from battle.damage import calculate_damage
from battle.models import BattlePokemon, Move, PokemonBuild, PokemonSpecies, StatBlock


def test_damage_against_immune_type_is_zero():
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

    geodude_species = PokemonSpecies(
        id=74,
        name="geodude",
        type1="rock",
        type2="ground",
        base_stats=StatBlock(
            hp=40,
            attack=80,
            defense=100,
            sp_attack=30,
            sp_defense=30,
            speed=20,
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

    pikachu = BattlePokemon(PokemonBuild(species=pikachu_species, level=50))
    geodude = BattlePokemon(PokemonBuild(species=geodude_species, level=50))

    result = calculate_damage(
        attacker=pikachu,
        defender=geodude,
        move=thunderbolt,
        random_factor=1.0,
    )

    assert result.damage == 0
    assert result.type_multiplier == 0.0

#test pikachu tonnerre sur rondoudou (les deux nature neutre et 31iv)
def test_pikachu_thunderbolt_against_jigglypuff_deals_94_damage():
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

    jigglypuff_species = PokemonSpecies(
        id=39,
        name="jigglypuff",
        type1="normal",
        type2="fairy",
        base_stats=StatBlock(
            hp=115,
            attack=45,
            defense=20,
            sp_attack=45,
            sp_defense=25,
            speed=20,
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
        priority=0,
    )

    pikachu = BattlePokemon(
        PokemonBuild(
            species=pikachu_species,
            level=50,
            nature="hardy",
        )
    )

    jigglypuff = BattlePokemon(
        PokemonBuild(
            species=jigglypuff_species,
            level=50,
            nature="hardy",
        )
    )

    result = calculate_damage(
        attacker=pikachu,
        defender=jigglypuff,
        move=thunderbolt,
        random_factor=1.0,
    )

    assert pikachu.stats.sp_attack == 70
    assert jigglypuff.stats.sp_defense == 45
    assert result.damage == 94