"""
Minimal automation runner: specify the scenario, whether to enable reputation/gossip, and how many steps to run.
Flow:
- If a seed exists (default fs_storage/<treatment>_seed/step_0), reuse it;
- Otherwise generate a seed from sim_storage/profiles.json;
- Copy the seed to a timestamped run folder and start the chosen scenario.
"""

import argparse
import shutil
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from start import Creation
from sim_storage.change_sim_folder import generate_seed
from utils import fs_storage

SCENARIO_ALIASES = {
    "invest": "invest",
    "investment": "invest",
    "i": "invest",
    "sign": "sign",
    "sign_up": "sign",
    "signup": "sign",
    "s": "sign",
    "pd": "pd",
    "pd_game": "pd",
    "pdgame": "pd",
    "p": "pd",
}

SCENARIO_TO_TREATMENT = {
    "invest": "investment",
    "sign": "sign_up",
    "pd": "pd_game",
}


def parse_args():
    parser = argparse.ArgumentParser(description="Auto-run simulation with minimal inputs.")
    parser.add_argument(
        "--scenario",
        required=True,
        choices=sorted(set(SCENARIO_ALIASES.keys())),
        help="Scenario to run: invest / sign / pd (aliases: investment, pd_game, etc.)",
    )
    parser.add_argument("--steps", type=int, default=None, help="Number of steps to run (>=1)")
    parser.add_argument("--step", type=int, default=None, help="Alias for --steps")
    parser.add_argument("--reputation", choices=["y", "n"], default="y", help="Use reputation? (y/n)")
    parser.add_argument("--gossip", choices=["y", "n"], default="y", help="Use gossip? (y/n)")
    parser.add_argument(
        "--sim-name",
        help="Custom run directory name (fs_storage/<sim-name>/step_0). Defaults to a timestamp.",
    )
    parser.add_argument(
        "--sim",
        help="Resume from an existing run folder (relative to fs_storage or a path to step_x). Skips seeding and continues from the latest step.",
    )
    return parser.parse_args()


def ensure_seed(scenario: str) -> Path:
    treatment = SCENARIO_TO_TREATMENT[scenario]
    seed_step = Path(fs_storage) / f"{treatment}_seed" / "step_0"
    if seed_step.exists():
        print(f"[seed] found existing seed: {seed_step}")
        return seed_step

    profiles = Path(fs_storage) / "profiles.json"
    persona_file = str(profiles) if profiles.exists() else None
    print(f"[seed] not found, generating default seed: {seed_step}")
    generate_seed(treatment, sim_name=f"{treatment}_seed", persona_desc_path=persona_file)
    return seed_step


def prepare_run_name(scenario: str, reputation: str, gossip: str, steps: int, sim_name: str | None) -> str:
    if sim_name:
        return sim_name
    ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]  # Millisecond precision for readability and uniqueness
    rep = reputation.upper()
    gos = gossip.upper()
    return f"{scenario}_rep{rep}_gos{gos}_s{steps}_{ts}"


def copy_seed_to_run(seed_step: Path, run_name: str) -> str:
    dest_step = Path(fs_storage) / run_name / "step_0"
    dest_step.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(seed_step, dest_step)
    print(f"[run] created run folder: {dest_step}")
    return f"{run_name}/step_0"


def normalize_existing_sim(sim_arg: str) -> str:
    """
    Return the latest step_x path relative to fs_storage.
    Accepts:
      - run/step_3
      - run               (picks the largest step_x under run)
      - sim_storage/run/step_2 or absolute paths (must be under fs_storage)
    """
    path = Path(sim_arg).expanduser()
    fs_root = Path(fs_storage).resolve()

    if not path.is_absolute():
        path = fs_root / path

    try:
        path.relative_to(fs_root)
    except Exception:
        raise ValueError(f"--sim must be inside fs_storage: {fs_root}")

    if not path.exists():
        raise FileNotFoundError(f"--sim path does not exist: {path}")

    # If the path is already step_x
    if path.name.startswith("step_") and path.is_dir():
        return str(path.relative_to(fs_root))

    # Otherwise find the largest step_x among subdirectories
    step_dirs = [p for p in path.iterdir() if p.is_dir() and p.name.startswith("step_")]
    if not step_dirs:
        raise ValueError(f"--sim has no step_x subdirectories: {path}")
    latest = max(step_dirs, key=lambda p: int(p.name.split("_")[1]))
    return str(latest.relative_to(fs_root))


def run_simulation(sim_code: str, scenario: str, reputation: str, gossip: str, steps: int):
    server = Creation(sim_code, reputation, gossip, sim=SCENARIO_TO_TREATMENT[scenario])

    if scenario == "invest":
        server.start_server_investment(steps)
    elif scenario == "sign":
        server.start_server_sign_up(steps)
    else:
        server.start_server_pd_game(steps)


def main():
    args = parse_args()
    scenario = SCENARIO_ALIASES[args.scenario.lower()]
    steps = args.steps if args.steps is not None else args.step
    if steps is None:
        steps = 1
    if steps < 1:
        raise ValueError("steps must be >= 1")

    # If resuming from an existing experiment, continue from the latest step
    if args.sim:
        sim_code = normalize_existing_sim(args.sim)
        run_name = Path(sim_code).parts[0]
        print(f"[resume] use existing sim_code={sim_code} (run_id={run_name})")
    else:
        seed_step = ensure_seed(scenario)
        run_name = prepare_run_name(scenario, args.reputation, args.gossip, steps, args.sim_name)
        sim_code = copy_seed_to_run(seed_step, run_name)

    print(f"[info] start: scenario={scenario} steps={steps} reputation={args.reputation} gossip={args.gossip} run_id={run_name} sim_code={sim_code}")
    run_simulation(sim_code, scenario, args.reputation, args.gossip, steps)
    print(f"[done] run_id={run_name} sim_code={sim_code}")


if __name__ == "__main__":
    main()
