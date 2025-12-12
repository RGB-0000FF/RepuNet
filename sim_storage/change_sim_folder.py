"""
Seed generator for simulations.

Usage:
    # 1) Generate from built-in default descriptions
    python sim_storage/change_sim_folder.py --treatment investment --sim-name demo_invest

    # 2) Inherit each persona's learned value from an existing seed's scratch.json
    python sim_storage/change_sim_folder.py --treatment investment --sim-name demo_invest --from-seed sim_storage/invest_seed/step_0

    # 3) Generate from profiles.json (may contain multiple treatments)
    python sim_storage/change_sim_folder.py --treatment pd_game --sim-name demo_pd --persona-file sim_storage/profiles.json

This script keeps the scratch structure consistent while allowing learned content per persona and scenario to be inherited from an existing seed.
"""

import argparse
import json
import shutil
from pathlib import Path

try:
    from utils import fs_storage
except Exception:
    fs_storage = "./sim_storage"


# Default learned descriptions. Replace or extend with your own if needed.
PERSONA_DESCRIPTIONS = {
    # Rational
    "Liam OConnor": "You are Liam OConnor, a 53-year-old male from Ireland. You are a rational and self-interested individual who tends to prioritize your own benefits and often chooses strategies that maximize personal gains, even at the expense of others. You are participating in a multi-round Prisoner's Dilemma game, where each round may involve a different partner.",
    "Hiroshi Tanaka": "You are Hiroshi Tanaka, a 36-year-old male from Japan. You are a rational and self-interested individual who tends to prioritize your own benefits and often chooses strategies that maximize personal gains, even at the expense of others. You are participating in a multi-round Prisoner's Dilemma game, where each round may involve a different partner.",
    "David Johnson": "You are David Johnson, a 33-year-old male from the USA. You are a rational and self-interested individual who tends to prioritize your own benefits and often chooses strategies that maximize personal gains, even at the expense of others. You are participating in a multi-round Prisoner's Dilemma game, where each round may involve a different partner.",
    "Maria Rossi": "You are Maria Rossi, a 40-year-old female from Italy. You are a rational and self-interested individual who tends to prioritize your own benefits and often chooses strategies that maximize personal gains, even at the expense of others. You are participating in a multi-round Prisoner's Dilemma game, where each round may involve a different partner.",
    "Sofia Hernandez": "You are Sofia Hernandez, a 26-year-old female from Mexico. You are a rational and self-interested individual who tends to prioritize your own benefits and often chooses strategies that maximize personal gains, even at the expense of others. You are participating in a multi-round Prisoner's Dilemma game, where each round may involve a different partner.",
    "James Wang": "You are James Wang, a 34-year-old male from China. You are a rational and self-interested individual who tends to prioritize your own benefits and often chooses strategies that maximize personal gains, even at the expense of others. You are participating in a multi-round Prisoner's Dilemma game, where each round may involve a different partner.",
    "Sergey Petrov": "You are Sergey Petrov, a 45-year-old male from Russia. You are a rational and self-interested individual who tends to prioritize your own benefits and often chooses strategies that maximize personal gains, even at the expense of others. You are participating in a multi-round Prisoner's Dilemma game, where each round may involve a different partner.",
    "Hannah Muller": "You are Hannah Muller, a 33-year-old female from Germany. You are a rational and self-interested individual who tends to prioritize your own benefits and often chooses strategies that maximize personal gains, even at the expense of others. You are participating in a multi-round Prisoner's Dilemma game, where each round may involve a different partner.",
    "Nadia Novak": "You are Nadia Novak, a 37-year-old female from Poland. You are a rational and self-interested individual who tends to prioritize your own benefits and often chooses strategies that maximize personal gains, even at the expense of others. You are participating in a multi-round Prisoner's Dilemma game, where each round may involve a different partner.",
    "Elena Ivanova": "You are Elena Ivanova, a 47-year-old female from Russia. You are a rational and self-interested individual who tends to prioritize your own benefits and often chooses strategies that maximize personal gains, even at the expense of others. You are participating in a multi-round Prisoner's Dilemma game, where each round may involve a different partner.",
    # Altruistic
    "Mohammed Al-Farsi": "You are Mohammed Al-Farsi, a 27-year-old male from Oman. You are an altruistic and cooperative individual who seeks mutually beneficial outcomes and often chooses strategies that promote trust and shared success. You are participating in a multi-round Prisoner's Dilemma game, where each round may involve a different partner.",
    "Aisha Ibrahim": "You are Aisha Ibrahim, a 41-year-old female from Nigeria. You are an altruistic and cooperative individual who seeks mutually beneficial outcomes and often chooses strategies that promote trust and shared success. You are participating in a multi-round Prisoner's Dilemma game, where each round may involve a different partner.",
    "Akiko Sato": "You are Akiko Sato, a 38-year-old female from Japan. You are an altruistic and cooperative individual who seeks mutually beneficial outcomes and often chooses strategies that promote trust and shared success. You are participating in a multi-round Prisoner's Dilemma game, where each round may involve a different partner.",
    "Emma Dubois": "You are Emma Dubois, a 23-year-old female from France. You are an altruistic and cooperative individual who seeks mutually beneficial outcomes and often chooses strategies that promote trust and shared success. You are participating in a multi-round Prisoner's Dilemma game, where each round may involve a different partner.",
    "Ahmed Hassan": "You are Ahmed Hassan, a 29-year-old male from Egypt. You are an altruistic and cooperative individual who seeks mutually beneficial outcomes and often chooses strategies that promote trust and shared success. You are participating in a multi-round Prisoner's Dilemma game, where each round may involve a different partner.",
    "Fatima Ali": "You are Fatima Ali, a 47-year-old female from Pakistan. You are an altruistic and cooperative individual who seeks mutually beneficial outcomes and often chooses strategies that promote trust and shared success. You are participating in a multi-round Prisoner's Dilemma game, where each round may involve a different partner.",
    "Isabella Costa": "You are Isabella Costa, an 18-year-old female from Brazil. You are an altruistic and cooperative individual who seeks mutually beneficial outcomes and often chooses strategies that promote trust and shared success. You are participating in a multi-round Prisoner's Dilemma game, where each round may involve a different partner.",
    "Mateo Garcia": "You are Mateo Garcia, a 36-year-old male from Argentina. You are an altruistic and cooperative individual who seeks mutually beneficial outcomes and often chooses strategies that promote trust and shared success. You are participating in a multi-round Prisoner's Dilemma game, where each round may involve a different partner.",
    "Juan Carlos Reyes": "You are Juan Carlos Reyes, a 57-year-old male from Spain. You are an altruistic and cooperative individual who seeks mutually beneficial outcomes and often chooses strategies that promote trust and shared success. You are participating in a multi-round Prisoner's Dilemma game, where each round may involve a different partner.",
    "Robert Miller": "You are Robert Miller, a 44-year-old male from the UK. You are an altruistic and cooperative individual who seeks mutually beneficial outcomes and often chooses strategies that promote trust and shared success. You are participating in a multi-round Prisoner's Dilemma game, where each round may involve a different partner.",
}


TREATMENTS = {
    "investment": {"investment": True},
    "pd_game": {"investment": False},
    "sign_up": {"investment": False},
}


def _normalize_learned(learned_value, investment: bool):
    if investment:
        if isinstance(learned_value, dict):
            investor = learned_value.get("investor") or next(iter(learned_value.values()), "")
            trustee = learned_value.get("trustee") or investor
        elif isinstance(learned_value, list):
            investor = learned_value[0] if len(learned_value) > 0 else ""
            trustee = learned_value[1] if len(learned_value) > 1 else investor
        else:
            investor = trustee = learned_value
        return {"investor": investor, "trustee": trustee}
    # For non-investment scenarios, always return a string (prefer "value", otherwise first element)
    if isinstance(learned_value, dict):
        return learned_value.get("value") or next(iter(learned_value.values()), "")
    if isinstance(learned_value, list):
        return learned_value[0] if learned_value else ""
    return learned_value


def _build_scratch(persona_name: str, learned_value, persona_idx: int, investment: bool) -> dict:
    learned = _normalize_learned(learned_value, investment)
    return {
        "name": persona_name,
        "innate": None,
        "learned": learned,
        "currently": None,
        "ID": persona_idx,
        "role": None,
        "curr_step": 0,
        "complain_buffer": [],
        "total_num_investor": 0,
        "success_num_investor": 0,
        "total_num_trustee": 0,
        "success_num_trustee": 0,
        "total_chat_num": 0,
        "success_chat_num": 0,
        "relationship": {"bind_list": [], "black_list": []},
        "resources_unit": 10,
        "observed": {},
    }


def init_persona(base_folder: Path, persona_name: str, learned_value: str, persona_idx: int, investment: bool) -> None:
    persona_folder = base_folder / "personas" / persona_name
    (persona_folder / "memory" / "associative_memory").mkdir(parents=True, exist_ok=True)
    (persona_folder / "reputation").mkdir(parents=True, exist_ok=True)

    with open(persona_folder / "memory" / "associative_memory" / "nodes.json", "w") as f:
        json.dump([], f, indent=4)
    with open(persona_folder / "reputation" / "gossip_database.json", "w") as f:
        json.dump([], f, indent=4)
    with open(persona_folder / "reputation" / "reputation_database.json", "w") as f:
        json.dump({}, f, indent=4)
    with open(persona_folder / "reputation" / "out_of_date_reputation_database.json", "w") as f:
        json.dump({}, f, indent=4)

    scratch = _build_scratch(persona_name, learned_value, persona_idx, investment)
    with open(persona_folder / "memory" / "scratch.json", "w", encoding="utf-8") as f:
        json.dump(scratch, f, indent=4, ensure_ascii=False)


def write_meta(base_folder: Path, persona_names) -> None:
    reverie_folder = base_folder / "reverie"
    reverie_folder.mkdir(parents=True, exist_ok=True)
    meta = {"persona_names": list(persona_names), "step": 0}
    with open(reverie_folder / "meta.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)


def load_persona_descriptions(custom_path: str = None) -> dict:
    if not custom_path:
        return PERSONA_DESCRIPTIONS
    path = Path(custom_path)
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError("Custom persona description file must be a JSON object of name -> learned text.")
    return data


def load_from_existing_seed(seed_path: Path, investment: bool):
    """Read learned content from an existing seed, mapped by persona name."""
    personas_folder = seed_path / "personas"
    if not personas_folder.exists():
        raise ValueError(f"Seed path {seed_path} missing personas directory")

    meta_path = seed_path / "reverie" / "meta.json"
    if meta_path.exists():
        persona_names = json.load(open(meta_path, "r", encoding="utf-8")).get("persona_names", [])
    else:
        persona_names = [p.name for p in personas_folder.iterdir() if p.is_dir()]

    learned_map = {}
    for name in persona_names:
        scratch_path = personas_folder / name / "memory" / "scratch.json"
        if not scratch_path.exists():
            continue
        loaded = json.load(open(scratch_path, "r", encoding="utf-8")).get("learned")
        learned_map[name] = _normalize_learned(loaded, investment)
    return learned_map, persona_names


def generate_seed(treatment: str, sim_name: str = None, persona_desc_path: str = None, from_seed: str = None) -> Path:
    if treatment not in TREATMENTS:
        raise ValueError(f"Unsupported treatment '{treatment}'. Options: {list(TREATMENTS)}")

    sim_dir_name = sim_name or f"{treatment}_seed"
    base_folder = Path(fs_storage) / sim_dir_name / "step_0"

    if base_folder.exists():
        shutil.rmtree(base_folder)
    base_folder.mkdir(parents=True, exist_ok=True)

    investment = TREATMENTS[treatment]["investment"]
    learned_map = {}
    if from_seed:
        learned_map, persona_names = load_from_existing_seed(Path(from_seed), investment)
    else:
        persona_descriptions = load_persona_descriptions(persona_desc_path)
        persona_names = list(persona_descriptions.keys())
        learned_map = persona_descriptions
        # If persona_descriptions is a multi-scenario profile (top-level contains treatment), extract the current one
        if treatment in persona_descriptions and isinstance(persona_descriptions[treatment], dict):
            learned_map = persona_descriptions[treatment]
            persona_names = list(learned_map.keys())

    write_meta(base_folder, persona_names)
    for idx, persona in enumerate(persona_names):
        learned_value = learned_map.get(persona, "")
        init_persona(base_folder, persona, learned_value, idx, investment)

    return base_folder


def parse_args():
    parser = argparse.ArgumentParser(description="Generate simulation seeds with consistent scratch structure.")
    parser.add_argument(
        "--treatment",
        choices=list(TREATMENTS.keys()),
        required=True,
        help="Which task/treatment to seed (controls learned structure).",
    )
    parser.add_argument(
        "--sim-name",
        help="Folder name under sim_storage; defaults to '<treatment>_seed'.",
    )
    parser.add_argument(
        "--persona-file",
        help="Optional path to JSON file mapping persona_name -> learned text. Defaults to built-in PERSONA_DESCRIPTIONS.",
    )
    parser.add_argument(
        "--from-seed",
        help="Path to an existing step_0 (with personas/.../scratch.json) to inherit each persona's learned value.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    target = generate_seed(args.treatment, args.sim_name, args.persona_file, args.from_seed)
    print(f"Seed generated at: {target}")
