from tqdm import tqdm
import polars as pl
import requests
import json
import os

BASE_URL = "https://pokeapi.co/api/v2/"

def get_all_pokemon_list():
    url = BASE_URL + "pokemon?limit=100000"
    return requests.get(url).json()["results"]


def get_pokemon_data(url):
    data = requests.get(url).json()

    types = [t["type"]["name"] for t in data["types"]]

    stats = {
        s["stat"]["name"]: s["base_stat"]
        for s in data["stats"]
    }

    moves = [int(m["move"]["url"].split('/')[-2]) for m in data["moves"]]

    return {
        "id": data["id"],
        "name": data["name"],
        "types": types,
        "stats": stats,
        "moves": moves
    }


def get_move_details(move_url):
    move = requests.get(move_url).json()
    return {
        "name": move["name"],
        "power": move["power"],
        "accuracy": move["accuracy"],
        "pp": move["pp"],
        "type": move["type"]["name"],
        "damage_class": move["damage_class"]["name"]
    }


def build_poke_stats_moves():
    pokemon_list = get_all_pokemon_list()

    rows = []
    pokemon_moves = {}

    for p in tqdm(pokemon_list, desc='getting pokemon stats & moves'):
        poke = get_pokemon_data(p["url"])

        # Types (handle 1 or 2 types)
        type1 = poke["types"][0] if len(poke["types"]) > 0 else None
        type2 = poke["types"][1] if len(poke["types"]) > 1 else None

        stats = poke["stats"]

        row = {
            "id": poke["id"],
            "name": poke["name"],
            "type1": type1,
            "type2": type2,
            "hp": stats.get("hp"),
            "attack": stats.get("attack"),
            "defense": stats.get("defense"),
            "sp_attack": stats.get("special-attack"),
            "sp_defense": stats.get("special-defense"),
            "speed": stats.get("speed"),
        }

        rows.append(row)

        # Map pokemon → move ids
        pokemon_moves[poke["id"]] = poke["moves"]

    # Save parquet
    df = pl.DataFrame(rows)
    df.write_parquet("data/pokemon_stats.parquet")

    # Save moves mapping
    with open("data/pokemon_moves.json", "w") as f:
        json.dump(pokemon_moves, f)

    print("Saved pokemon_stats.parquet and pokemon_moves.json")


def build_move_stats():
    with open("data/pokemon_moves.json", "r") as f:
        pokemon_moves = json.load(f)

    # ---- unique move ids ----
    move_ids = set()
    for moves in pokemon_moves.values():
        move_ids.update(moves)

    rows = []

    for move_id in tqdm(sorted(move_ids), desc="building move parquet"):
        url = f"{BASE_URL}move/{move_id}/"

        try:
            move = requests.get(url).json()
            meta = move.get("meta") or {}

            # ---- initialize stat changes ----
            stat_changes = {
                "attack_change": 0,
                "defense_change": 0,
                "sp_attack_change": 0,
                "sp_defense_change": 0,
                "speed_change": 0,
                "accuracy_change": 0,
                "evasion_change": 0,
            }

            for sc in move.get("stat_changes", []):
                stat = sc["stat"]["name"].replace("-", "_")
                key = f"{stat}_change"
                if key in stat_changes:
                    stat_changes[key] = sc["change"]

            row = {
                # ---- identifiers ----
                "move_id": move["id"],
                "name": move["name"],

                # ---- core ----
                "type": move["type"]["name"] if move["type"] else None,
                "damage_class": move["damage_class"]["name"] if move["damage_class"] else None,
                "power": move["power"] or 0,
                "accuracy": move["accuracy"], #enlever or 100 pour avoir les None
                "pp": move["pp"],
                "priority": move["priority"],

                # ---- effects ----
                "ailment": meta.get("ailment", {}).get("name"),
                "ailment_chance": meta.get("ailment_chance") or 0,
                "flinch_chance": meta.get("flinch_chance") or 0,
                "stat_chance": meta.get("stat_chance") or 0,

                # ---- mechanics ----
                "min_hits": meta.get("min_hits") or 1,
                "max_hits": meta.get("max_hits") or 1,
                "min_turns": meta.get("min_turns") or 1,
                "max_turns": meta.get("max_turns") or 1,
                "drain": meta.get("drain") or 0,
                "healing": meta.get("healing") or 0,
                "crit_rate": meta.get("crit_rate") or 0,
            }

            row.update(stat_changes)

            rows.append(row)

        except Exception as e:
            print(f"Error with move {move_id}: {e}")

    # ---- build parquet ----
    df = pl.DataFrame(rows)

    # Optional: enforce column order
    df = df.select([
        "move_id", "name", "type", "damage_class",
        "power", "accuracy", "pp", "priority",
        "ailment", "ailment_chance", "flinch_chance", "stat_chance",
        "min_hits", "max_hits", "min_turns", "max_turns",
        "drain", "healing", "crit_rate",
        "attack_change", "defense_change", "sp_attack_change",
        "sp_defense_change", "speed_change",
        "accuracy_change", "evasion_change"
    ])

    df.write_parquet("data/moves.parquet")

    print("Saved clean moves.parquet")


if __name__ == '__main__':
    os.makedirs("data", exist_ok=True)

    build_poke_stats_moves()
    build_move_stats()

    print("\n=== Preview: pokemon_stats.parquet ===")
    df_pokemon = pl.read_parquet("data/pokemon_stats.parquet")
    print(df_pokemon.head())

    print("\n=== Preview: moves.parquet ===")
    df_moves = pl.read_parquet("data/moves.parquet")
    print(df_moves.head())

    print("\n=== Preview: pokemon_moves.json ===")
    with open("data/pokemon_moves.json", "r") as f:
        pokemon_moves = json.load(f)

    # print first 5 entries
    for i, (poke_id, moves) in enumerate(pokemon_moves.items()):
        print(f"{poke_id}: {moves[:10]}")  # show first 10 moves only
        if i >= 4:
            break