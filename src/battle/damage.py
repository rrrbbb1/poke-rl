import random
from dataclasses import dataclass

from battle.models import BattlePokemon, Move
from battle.type_chart import get_type_multiplier

#Classe qui représente les degats
@dataclass(frozen=True)
class DamageResult:
    damage: int
    type_multiplier: float
    stab: float
    random_factor: float

    @property
    def is_immune(self) -> bool:
        return self.type_multiplier == 0

    @property
    def is_super_effective(self) -> bool:
        return self.type_multiplier > 1

    @property
    def is_not_very_effective(self) -> bool:
        return 0 < self.type_multiplier < 1

#Calcul des dégats
def calculate_damage(
    attacker: BattlePokemon,
    defender: BattlePokemon,
    move: Move,
    random_factor: float | None = None,
) -> DamageResult:
    if not move.is_damaging():
        return DamageResult(
            damage=0,
            type_multiplier=1.0,
            stab=1.0,
            random_factor=1.0,
        )

    if random_factor is None:
        random_factor = random.uniform(0.85, 1.0)

    type_multiplier = get_type_multiplier(
        move_type=move.type,
        defender_type1=defender.species.type1,
        defender_type2=defender.species.type2,
    )

    if type_multiplier == 0:
        return DamageResult(
            damage=0,
            type_multiplier=0.0,
            stab=1.0,
            random_factor=random_factor,
        )
#physique ou spé
    if move.damage_class == "physical":
        attack = attacker.get_modified_stat("attack")
        defense = defender.get_modified_stat("defense")
    elif move.damage_class == "special":
        attack = attacker.get_modified_stat("sp_attack")
        defense = defender.get_modified_stat("sp_defense")
    else:
        return DamageResult(
            damage=0,
            type_multiplier=type_multiplier,
            stab=1.0,
            random_factor=random_factor,
        )

    stab = 1.5 if move.type in attacker.species.types else 1.0

    level = attacker.level
    power = move.power

    base_damage = (((2 * level // 5 + 2) * power * attack // defense) // 50) + 2

    final_damage = base_damage * stab * type_multiplier * random_factor

    return DamageResult(
        damage=max(1, int(final_damage)),
        type_multiplier=type_multiplier,
        stab=stab,
        random_factor=random_factor,
    )