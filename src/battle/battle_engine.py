import random
from dataclasses import dataclass, field

from battle.damage import DamageResult, calculate_damage
from battle.models import (
    BattlePokemon,
    Move,
    accuracy_stage_multiplier,
)


@dataclass(frozen=True)
class BattleEvent:
    message: str
    attacker_name: str | None = None
    defender_name: str | None = None
    move_name: str | None = None
    damage: int = 0
    hit: bool = True
    defender_hp_after: int | None = None
    defender_ko: bool = False
    type_multiplier: float = 1.0


@dataclass
class BattleState:
    pokemon1: BattlePokemon
    pokemon2: BattlePokemon
    turn: int = 1

    def is_finished(self) -> bool:
        return self.pokemon1.is_ko() or self.pokemon2.is_ko()

    def winner(self) -> BattlePokemon | None:
        if self.pokemon1.is_ko() and self.pokemon2.is_ko():
            return None

        if self.pokemon1.is_ko():
            return self.pokemon2

        if self.pokemon2.is_ko():
            return self.pokemon1

        return None


@dataclass(frozen=True)
class TurnResult:
    turn: int
    events: list[BattleEvent] = field(default_factory=list)
    finished: bool = False
    winner_name: str | None = None


class BattleEngine:
    def execute_turn(
        self,
        state: BattleState,
        move1: Move,
        move2: Move,
    ) -> TurnResult:
        if state.is_finished():
            winner = state.winner()
            return TurnResult(
                turn=state.turn,
                events=[
                    BattleEvent(
                        message="Battle is already finished."
                    )
                ],
                finished=True,
                winner_name=winner.species.name if winner else None,
            )

        events: list[BattleEvent] = []

        first_pokemon, first_move, second_pokemon, second_move = self._get_turn_order(
            state.pokemon1,
            move1,
            state.pokemon2,
            move2,
        )

        first_event = self._execute_move(first_pokemon, second_pokemon, first_move)
        events.append(first_event)

        if not second_pokemon.is_ko():
            second_event = self._execute_move(second_pokemon, first_pokemon, second_move)
            events.append(second_event)

        winner = state.winner()
        finished = state.is_finished()

        result = TurnResult(
            turn=state.turn,
            events=events,
            finished=finished,
            winner_name=winner.species.name if winner else None,
        )

        state.turn += 1

        return result

    def _get_turn_order(
        self,
        pokemon1: BattlePokemon,
        move1: Move,
        pokemon2: BattlePokemon,
        move2: Move,
    ) -> tuple[BattlePokemon, Move, BattlePokemon, Move]:
        if move1.priority > move2.priority:
            return pokemon1, move1, pokemon2, move2

        if move2.priority > move1.priority:
            return pokemon2, move2, pokemon1, move1

        speed1 = pokemon1.get_modified_stat("speed")
        speed2 = pokemon2.get_modified_stat("speed")

        if speed1 > speed2:
            return pokemon1, move1, pokemon2, move2

        if speed2 > speed1:
            return pokemon2, move2, pokemon1, move1

        if random.random() < 0.5:
            return pokemon1, move1, pokemon2, move2

        return pokemon2, move2, pokemon1, move1

    def _execute_move(
        self,
        attacker: BattlePokemon,
        defender: BattlePokemon,
        move: Move,
    ) -> BattleEvent:
        if attacker.is_ko():
            return BattleEvent(
                message=f"{attacker.species.name} is KO and cannot move.",
                attacker_name=attacker.species.name,
                defender_name=defender.species.name,
                move_name=move.name,
                hit=False,
            )

        if not self._does_move_hit(attacker, defender, move):
            return BattleEvent(
                message=f"{attacker.species.name} used {move.name}, but it missed!",
                attacker_name=attacker.species.name,
                defender_name=defender.species.name,
                move_name=move.name,
                hit=False,
                defender_hp_after=defender.current_hp,
            )

        damage_result = calculate_damage(attacker, defender, move)
        defender.take_damage(damage_result.damage)

        message = self._build_damage_message(
            attacker=attacker,
            defender=defender,
            move=move,
            damage_result=damage_result,
        )

        return BattleEvent(
            message=message,
            attacker_name=attacker.species.name,
            defender_name=defender.species.name,
            move_name=move.name,
            damage=damage_result.damage,
            hit=True,
            defender_hp_after=defender.current_hp,
            defender_ko=defender.is_ko(),
            type_multiplier=damage_result.type_multiplier,
        )

    def _does_move_hit(
            self,
            attacker: BattlePokemon,
            defender: BattlePokemon,
            move: Move,
    ) -> bool:
        if move.accuracy is None:
            return True

        accuracy_stage = attacker.accuracy_stage - defender.evasion_stage
        multiplier = accuracy_stage_multiplier(accuracy_stage)

        final_accuracy = move.accuracy * multiplier
        final_accuracy = max(0, min(100, final_accuracy))

        roll = random.uniform(0, 100)

        return roll <= final_accuracy

    def _build_damage_message(
        self,
        attacker: BattlePokemon,
        defender: BattlePokemon,
        move: Move,
        damage_result: DamageResult,
    ) -> str:
        if damage_result.is_immune:
            return (
                f"{attacker.species.name} used {move.name}, "
                f"but it had no effect on {defender.species.name}."
            )

        message = (
            f"{attacker.species.name} used {move.name} and dealt "
            f"{damage_result.damage} damage to {defender.species.name}."
        )

        if damage_result.is_super_effective:
            message += " It's super effective!"

        elif damage_result.is_not_very_effective:
            message += " It's not very effective."

        if defender.is_ko():
            message += f" {defender.species.name} is KO!"

        return message