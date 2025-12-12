"""
Non-interactive batch runner for simulations.

Example:
    python auto_run.py \
        --sim investment_seed/step_0 \
        --mode investment \
        --steps 3 \
        --reputation y \
        --gossip n
"""

import argparse

from start import Creation


def parse_args():
    parser = argparse.ArgumentParser(description="Run simulations without interactive prompts.")
    parser.add_argument(
        "--sim",
        required=True,
        help="Simulation path (relative to sim_storage), e.g., investment_seed/step_0",
    )
    parser.add_argument(
        "--mode",
        choices=["investment", "sign", "pd_game", "i", "s", "p"],
        required=True,
        help="Choose scenario: investment/sign/pd_game",
    )
    parser.add_argument(
        "--steps",
        type=int,
        default=1,
        help="Number of steps to execute (integer)",
    )
    parser.add_argument(
        "--reputation",
        default="y",
        help="Enable reputation? y/n",
    )
    parser.add_argument(
        "--gossip",
        default="y",
        help="Enable gossip? y/n",
    )
    return parser.parse_args()


def normalize_mode(mode: str) -> str:
    mode = mode.lower()
    if mode in ["investment", "i"]:
        return "investment"
    if mode in ["sign", "s", "signup", "sign_up"]:
        return "sign_up"
    if mode in ["pd_game", "p", "pd"]:
        return "pd_game"
    raise ValueError(f"Unsupported mode: {mode}")


def main():
    args = parse_args()
    mode = normalize_mode(args.mode)
    server = Creation(args.sim, args.reputation, args.gossip, sim=mode)

    if mode == "investment":
        server.start_server_investment(args.steps)
    elif mode == "sign_up":
        server.start_server_sign_up(args.steps)
    elif mode == "pd_game":
        server.start_server_pd_game(args.steps)

    print("Auto run finished.")


if __name__ == "__main__":
    main()
