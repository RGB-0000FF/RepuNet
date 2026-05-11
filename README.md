<div align="center">

# 🤝 RepuNet Simulations

**Reputation as a remedy for cooperation collapse in LLM-based multi-agent systems**

[![Python](https://img.shields.io/badge/Python-3.13%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![arXiv](https://img.shields.io/badge/arXiv-2505.05029-b31b1b.svg)](https://arxiv.org/abs/2505.05029)
[![LLM Backend](https://img.shields.io/badge/LLM-OpenAI--compatible-0f766e)](#configuration)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

<a href="README.md"><kbd>English</kbd></a> <a href="README_ZH.md"><kbd>简体中文</kbd></a>

[Paper](https://arxiv.org/abs/2505.05029) |
[HTML](https://arxiv.org/html/2505.05029v2) |
[Architecture](#architecture) |
[Quick Start](#quick-start) |
[Citation & License](#citation--license)

</div>

## Overview

**RepuNet** is a simulation framework for studying how operational reputation systems can mitigate cooperation collapse in LLM-based multi-agent systems (MASs). Agents reason with an OpenAI-compatible LLM backend, update self and peer reputations from direct interactions and gossip, rewire their social network, and act across investment, sign-up, and prisoner's dilemma scenarios.

## Key Contributions

| Cooperation collapse | Operational reputation | Emergent collective behavior |
| --- | --- | --- |
| We replicate cooperation collapse within LLM-based MASs, confirming its widespread prevalence and emphasizing the need to address it. | We propose **RepuNet**, the first operational reputation system to generalize reputation mechanisms to LLM-based MASs. | RepuNet exhibits emergent behaviors, highlighting how reputation systems drive complex collective behavior in LLM-based MASs. |

## Architecture

<p align="center">
  <img src="asset/Final_frameworkReputation_system.png" alt="RepuNet framework" width="900">
</p>

<p align="center">
  <em>Overview of the RepuNet reputation system.</em><br>
  <a href="asset/Final_frameworkReputation_system.pdf">View the original architecture PDF</a>
</p>

## At a Glance

| Item | Description |
| --- | --- |
| Scenarios | Investment, sign-up, and prisoner's dilemma |
| Core mechanisms | Reputation update, gossip propagation, and network rewiring |
| Agent backend | OpenAI-compatible LLM API |
| State management | Step-wise persistence under `sim_storage/` |
| Main entrypoints | `start.py`, `auto_run.py`, `scripts/run_simulation.py` |

## Contents

- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Quick Start](#quick-start)
- [Experiment Modes](#experiment-modes)
- [Run Simulations](#run-simulations)
- [Seed Data](#seed-data)
- [Outputs and Useful Paths](#outputs-and-useful-paths)
- [Citation & License](#citation--license)
- [License](#license)

## Requirements

- Python 3.13+
- A virtual environment tool such as `uv`, `venv`, or `conda`
- Access to an OpenAI-compatible API endpoint

## Installation

```bash
# Create and activate a virtual environment.
uv venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# Install RepuNet in editable mode.
uv pip install -e .
```

If you do not use `uv`, the standard Python workflow also works:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Configuration

Configure the LLM backend and storage path in `utils.py` before running simulations.

| Setting | Purpose |
| --- | --- |
| `openai_api_key` | API key for your OpenAI-compatible provider. Do not commit real keys. |
| `key_owner` | Identifier for the key owner or experiment runner. |
| `llm_model` | Model name used by all prompt calls. |
| `llm_api_base` | Base URL of the OpenAI-compatible endpoint. |
| `fs_storage` | Root directory for seeds and run outputs. Defaults to `./sim_storage`. |

Runtime overrides are available for model parameters:

```bash
export LLM_MODEL="gpt-4o-mini"
export LLM_API_BASE="https://api.your-endpoint/v1"
export LLM_MAX_TOKENS="4096"
export LLM_TEMPERATURE="0"
```

Recommended local key pattern:

```python
import os

openai_api_key = os.getenv("OPENAI_API_KEY", "sk-your-key")
key_owner = "your-name"
```

## Quick Start

Run a small prisoner's dilemma simulation with reputation enabled and gossip disabled:

```bash
python scripts/run_simulation.py \
  --scenario pd \
  --steps 5 \
  --reputation y \
  --gossip n
```

`scripts/run_simulation.py` will find or create a default seed, copy it into a timestamped run folder, execute the requested scenario, and persist all step outputs under `fs_storage`.

## Experiment Modes

| Reputation | Gossip | Typical purpose |
| --- | --- | --- |
| `y` | `y` | Full RepuNet setting with both reputation and gossip enabled. |
| `y` | `n` | Reputation-only setting for isolating the effect of direct reputation updates. |
| `n` | `y` | Gossip-enabled ablation without reputation-driven mechanisms. |
| `n` | `n` | Baseline setting without reputation or gossip. |

## Run Simulations

### Interactive Loop

```bash
python start.py
```

Prompts:

- Simulation path under `fs_storage`, such as `investment_seed/step_0`
- Whether to use reputation: `y` or `n`
- Whether to use gossip: `y` or `n`
- Scenario: investment (`i`), sign-up (`s`), or prisoner's dilemma (`p`)

Commands inside the loop:

- `run invest <steps>` / `run sign <steps>` / `run pd <steps>`
- `save`: write the current state
- `fin`: save and exit
- `exit`: delete the current run folder and exit

### Non-Interactive Run From an Existing Seed

```bash
python auto_run.py \
  --sim investment_seed/step_0 \
  --mode investment \
  --steps 3 \
  --reputation y \
  --gossip n
```

### Auto Seed, Run, and Resume

```bash
python scripts/run_simulation.py \
  --scenario investment \
  --steps 3 \
  --reputation y \
  --gossip y
```

Resume from an existing run directory or a specific step:

```bash
python scripts/run_simulation.py --scenario pd --steps 5 --sim run_pd/step_2
```

### Batch Runs

Edit the `JOBS` array in `scripts/batch_run.sh`, then run:

```bash
bash scripts/batch_run.sh
```

Logs are written to `outputs/<run_id>.log`; simulation states are written to `fs_storage/<run_id>/step_*`.

## Seed Data

Seeds live at `fs_storage/<sim_name>/step_0` and include `reverie/meta.json` plus per-persona memory and reputation files.

Create built-in personas:

```bash
python sim_storage/change_sim_folder.py --treatment investment --sim-name demo_invest
```

Inherit learned fields from an existing seed:

```bash
python sim_storage/change_sim_folder.py \
  --treatment investment \
  --sim-name demo_invest \
  --from-seed sim_storage/invest_seed/step_0
```

Create custom personas from JSON:

```bash
python sim_storage/change_sim_folder.py \
  --treatment pd_game \
  --sim-name demo_pd \
  --persona-file sim_storage/profiles.json
```

Export learned fields from existing seeds for reuse:

```bash
python sim_storage/export_profiles.py \
  --seeds sim_storage/invest_seed sim_storage/pd_game_seed sim_storage/sign_seed \
  --out sim_storage/profiles.json
```

If a default seed is missing, `scripts/run_simulation.py` automatically creates one using built-in personas or `sim_storage/profiles.json` when available.

## Outputs and Useful Paths

| Path | Description |
| --- | --- |
| `start.py` | Interactive simulation runner. |
| `auto_run.py` | Non-interactive runner for an existing seed. |
| `scripts/run_simulation.py` | Auto-seed, run, and resume entrypoint. |
| `scripts/batch_run.sh` | Batch launcher for multiple experiment jobs. |
| `sim_storage/change_sim_folder.py` | Seed generator. |
| `sim_storage/export_profiles.py` | Export personas' learned fields to JSON. |
| `outputs/` | Run logs. |
| `sim_storage/` | Seeds, generated runs, and `step_*` state folders. |

Each simulation step copies `step_x` to `step_{x+1}` and writes scenario outputs such as `investment results`, `sign up result`, or `pd_game results` under the new step folder.

## Citation & License

If you use RepuNet in your research, please cite our paper:

```bibtex
@misc{ren2026reputation,
  title         = {Reputation as a Solution to Cooperation Collapse in LLM-based MASs},
  author        = {Ren, Siyue and Li, Dong and Zhao, Wenyi and Chen, Jintai and He, Xu and Hu, Shuyue and Wang, Pengfei and Deng, Lidong and Li, Xiu and Xiao, Yanghua},
  year          = {2026},
  eprint        = {2505.05029},
  archivePrefix = {arXiv},
  primaryClass  = {cs.AI},
  doi           = {10.48550/arXiv.2505.05029},
  url           = {https://arxiv.org/abs/2505.05029}
}
```

RepuNet is released under the [MIT License](LICENSE). MIT is a common permissive license for academic research code because it allows reuse, modification, and redistribution with attribution while keeping the license text lightweight.
