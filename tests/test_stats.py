from battle.models import PokemonSpecies, PokemonBuild, StatBlock
import pytest

#test du calcul des stats du pikachu avec 31 IV niv 50 nature serieux (neutre)
def test_pokemon_stats_with_default_ivs_and_no_evs():
    species = PokemonSpecies(
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

    build = PokemonBuild(
        species=species,
        level=50,
        nature="serious",
    )

    stats = build.calculate_stats()

    assert stats.hp == 110
    assert stats.attack == 75
    assert stats.defense == 60
    assert stats.sp_attack == 70
    assert stats.sp_defense == 70
    assert stats.speed == 110


#test si EV reste en dessous de 252
def test_invalid_ev_above_252_raises_error():
    species = PokemonSpecies(
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

    with pytest.raises(ValueError):
        PokemonBuild(
            species=species,
            evs=StatBlock(
                hp=0,
                attack=0,
                defense=0,
                sp_attack=0,
                sp_defense=0,
                speed=300,
            ),
        )

#test si somme des EV est cohérente
def test_invalid_total_evs_above_510_raises_error():
    species = PokemonSpecies(
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

    with pytest.raises(ValueError):
        PokemonBuild(
            species=species,
            evs=StatBlock(
                hp=252,
                attack=252,
                defense=252,
                sp_attack=0,
                sp_defense=0,
                speed=0,
            ),
        )