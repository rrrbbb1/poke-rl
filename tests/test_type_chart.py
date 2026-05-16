from battle.type_chart import get_type_multiplier
from battle.models import stage_multiplier, accuracy_stage_multiplier

#different test sur les type et leurs efficacités
def test_electric_is_super_effective_against_water():
    multiplier = get_type_multiplier(
        move_type="electric",
        defender_type1="water",
        defender_type2=None,
    )

    assert multiplier == 2.0


def test_electric_has_no_effect_against_ground():
    multiplier = get_type_multiplier(
        move_type="electric",
        defender_type1="ground",
        defender_type2=None,
    )

    assert multiplier == 0.0


def test_dual_type_multiplier():
    multiplier = get_type_multiplier(
        move_type="electric",
        defender_type1="water",
        defender_type2="flying",
    )

    assert multiplier == 4.0


#test de boost
def test_stage_multiplier():
    assert stage_multiplier(-6) == 1 / 4
    assert stage_multiplier(-2) == 1 / 2
    assert stage_multiplier(0) == 1
    assert stage_multiplier(2) == 2
    assert stage_multiplier(6) == 4


def test_accuracy_stage_multiplier():
    assert accuracy_stage_multiplier(-6) == 1 / 3
    assert accuracy_stage_multiplier(-1) == 3 / 4
    assert accuracy_stage_multiplier(0) == 1
    assert accuracy_stage_multiplier(3) == 2
    assert accuracy_stage_multiplier(6) == 3