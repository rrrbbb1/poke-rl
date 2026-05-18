from dataclasses import dataclass, field
from typing import Optional


STAT_NAMES = ("hp", "attack", "defense", "sp_attack", "sp_defense", "speed")
NON_HP_STATS = ("attack", "defense", "sp_attack", "sp_defense", "speed")

def stage_multiplier(stage: int) -> float:
    stage = max(-6, min(6, stage))

    if stage >= 0:
        return (2 + stage) / 2

    return 2 / (2 - stage)


def accuracy_stage_multiplier(stage: int) -> float:
    stage = max(-6, min(6, stage))

    if stage >= 0:
        return (3 + stage) / 3

    return 3 / (3 - stage)

# Tt les natures et leurs effets sous forme de dictionnaire de tuple ( + , - )
NATURES = {
    # neutres
    "hardy":   (None, None),
    "docile":  (None, None),
    "bashful": (None, None),
    "quirky":  (None, None),
    "serious": (None, None),

    # +attack
    "lonely":  ("attack", "defense"),
    "brave":   ("attack", "speed"),
    "adamant": ("attack", "sp_attack"),
    "naughty": ("attack", "sp_defense"),

    # +defense
    "bold":    ("defense", "attack"),
    "relaxed": ("defense", "speed"),
    "impish":  ("defense", "sp_attack"),
    "lax":     ("defense", "sp_defense"),

    # +sp_attack
    "modest": ("sp_attack", "attack"),
    "mild":   ("sp_attack", "defense"),
    "quiet":  ("sp_attack", "speed"),
    "rash":   ("sp_attack", "sp_defense"),

    # +sp_defense
    "calm":    ("sp_defense", "attack"),
    "gentle":  ("sp_defense", "defense"),
    "sassy":   ("sp_defense", "speed"),
    "careful": ("sp_defense", "sp_attack"),

    # +speed
    "timid": ("speed", "attack"),
    "hasty": ("speed", "defense"),
    "jolly": ("speed", "sp_attack"),
    "naive": ("speed", "sp_defense"),
}

#Classe qui définit les stat
@dataclass(frozen=True)
class StatBlock:
    hp: int
    attack: int
    defense: int
    sp_attack: int
    sp_defense: int
    speed: int

    def get(self, stat_name: str) -> int:
        return getattr(self, stat_name)

    def as_dict(self) -> dict[str, int]:
        return {
            "hp": self.hp,
            "attack": self.attack,
            "defense": self.defense,
            "sp_attack": self.sp_attack,
            "sp_defense": self.sp_defense,
            "speed": self.speed,
        }

#Classe qui définit un pokemon avec ses BASE STATS
@dataclass(frozen=True)
class PokemonSpecies:
    id: int
    name: str
    type1: str
    type2: Optional[str]
    base_stats: StatBlock

    @property
    def types(self) -> list[str]:
        if self.type2 is None:
            return [self.type1]

        return [self.type1, self.type2]

#Classe qui définit les attaques
@dataclass(frozen=True)
class Move:
    move_id: int
    name: str
    type: str
    damage_class: str
    power: int
    accuracy: int | None #valeur none = ne peut pas echouer pour les attaques offensives
    pp: int
    priority: int = 0

    def is_damaging(self) -> bool:
        return self.power > 0 and self.damage_class in ("physical", "special")

    def is_status(self) -> bool:
        return self.damage_class == "status"

#Classe qui définit un pokemon et ces "VALUES" (IV, EV, NATURE, NIVEAU) et permet de calculer ses stats grace aux values
@dataclass(frozen=True)
class PokemonBuild:
    species: PokemonSpecies
    level: int = 50
    ivs: StatBlock = field(default_factory=lambda: StatBlock(
        hp=31,
        attack=31,
        defense=31,
        sp_attack=31,
        sp_defense=31,
        speed=31,
    ))
    evs: StatBlock = field(default_factory=lambda: StatBlock(
        hp=0,
        attack=0,
        defense=0,
        sp_attack=0,
        sp_defense=0,
        speed=0,
    ))
    nature: str = "serious"
    moves: list[Move] = field(default_factory=list)

    def __post_init__(self):
        self._validate_level()
        self._validate_ivs()
        self._validate_evs()
        self._validate_nature()
        self._validate_moves()

    def _validate_level(self):
        if not 1 <= self.level <= 100:
            raise ValueError(f"Invalid level: {self.level}. Level must be between 1 and 100.")

    def _validate_ivs(self):
        for stat_name, value in self.ivs.as_dict().items():
            if not 0 <= value <= 31:
                raise ValueError(f"Invalid IV for {stat_name}: {value}. IV must be between 0 and 31.")
#Verifie si les EV respectent les règles de repartition
    def _validate_evs(self):
        total_evs = sum(self.evs.as_dict().values())

        if total_evs > 510:
            raise ValueError(f"Invalid EV total: {total_evs}. Maximum is 510.")

        for stat_name, value in self.evs.as_dict().items():
            if not 0 <= value <= 252:
                raise ValueError(f"Invalid EV for {stat_name}: {value}. EV must be between 0 and 252.")

    def _validate_nature(self):
        if self.nature not in NATURES:
            raise ValueError(f"Unknown nature: {self.nature}")

    def _validate_moves(self):
        if len(self.moves) > 4:
            raise ValueError("A Pokémon cannot have more than 4 moves.")

#Calcul toutes les stats du pokemon (avec des méthodes décrites après)
    def calculate_stats(self) -> StatBlock:
        return StatBlock(
            hp=self._calculate_hp(),
            attack=self._calculate_non_hp_stat("attack"),
            defense=self._calculate_non_hp_stat("defense"),
            sp_attack=self._calculate_non_hp_stat("sp_attack"),
            sp_defense=self._calculate_non_hp_stat("sp_defense"),
            speed=self._calculate_non_hp_stat("speed"),
        )
#Caclul du nombre de HP du pokemon
    def _calculate_hp(self) -> int:
        base = self.species.base_stats.hp
        iv = self.ivs.hp
        ev = self.evs.hp

        # Cas spécial : Shedinja a toujours 1 HP.
        if self.species.name == "shedinja":
            return 1
#L'arrondie au plus bas se fait grace à //
        return ((2 * base + iv + ev // 4) * self.level) // 100 + self.level + 10

#Calcul de la valeur des stat (SAUF HP)
    def _calculate_non_hp_stat(self, stat_name: str) -> int:
        base = self.species.base_stats.get(stat_name)
        iv = self.ivs.get(stat_name)
        ev = self.evs.get(stat_name)

        raw_stat = ((2 * base + iv + ev // 4) * self.level) // 100 + 5

        nature_multiplier = self._get_nature_multiplier(stat_name)

        return int(raw_stat * nature_multiplier)

#Applique l'effet de la nature
    def _get_nature_multiplier(self, stat_name: str) -> float:
        increased_stat, decreased_stat = NATURES[self.nature]

        if stat_name == increased_stat:
            return 1.1

        if stat_name == decreased_stat:
            return 0.9

        return 1.0

#Definit le pokemon pendant le combat
@dataclass
class BattlePokemon:
    build: PokemonBuild
    stats: StatBlock = field(init=False)
    current_hp: int = field(init=False)
#Boost de stats
    attack_stage: int = 0
    defense_stage: int = 0
    sp_attack_stage: int = 0
    sp_defense_stage: int = 0
    speed_stage: int = 0
    accuracy_stage: int = 0
    evasion_stage: int = 0

    status: Optional[str] = None

    def __post_init__(self):
        self.stats = self.build.calculate_stats()
        self.current_hp = self.stats.hp

    @property
    def level(self) -> int:
        return self.build.level

    @property
    def species(self) -> PokemonSpecies:
        return self.build.species

    @property
    def moves(self) -> list[Move]:
        return self.build.moves

    def is_ko(self) -> bool:
        return self.current_hp <= 0

    def take_damage(self, damage: int):
        self.current_hp = max(0, self.current_hp - damage)

    def heal(self, amount: int):
        self.current_hp = min(self.stats.hp, self.current_hp + amount)

    def get_stage(self, stat_name: str) -> int:
        if stat_name == "attack":
            return self.attack_stage
        if stat_name == "defense":
            return self.defense_stage
        if stat_name == "sp_attack":
            return self.sp_attack_stage
        if stat_name == "sp_defense":
            return self.sp_defense_stage
        if stat_name == "speed":
            return self.speed_stage
        if stat_name == "accuracy":
            return self.accuracy_stage
        if stat_name == "evasion":
            return self.evasion_stage

        raise ValueError(f"Unknown stat stage: {stat_name}")

    def set_stage(self, stat_name: str, value: int):
        value = max(-6, min(6, value))

        if stat_name == "attack":
            self.attack_stage = value
        elif stat_name == "defense":
            self.defense_stage = value
        elif stat_name == "sp_attack":
            self.sp_attack_stage = value
        elif stat_name == "sp_defense":
            self.sp_defense_stage = value
        elif stat_name == "speed":
            self.speed_stage = value
        elif stat_name == "accuracy":
            self.accuracy_stage = value
        elif stat_name == "evasion":
            self.evasion_stage = value
        else:
            raise ValueError(f"Unknown stat stage: {stat_name}")

    def change_stage(self, stat_name: str, delta: int):
        current = self.get_stage(stat_name)
        self.set_stage(stat_name, current + delta)

    def get_modified_stat(self, stat_name: str) -> int:
        if stat_name == "hp":
            return self.stats.hp

        base_value = self.stats.get(stat_name)
        stage = self.get_stage(stat_name)

        return max(1, int(base_value * stage_multiplier(stage)))