# RepuNet Simulation Runner

Paper: https://arxiv.org/html/2505.05029v2  
Anonymous repo mirror: https://anonymous.4open.science/r/RepuNet-B346

RepuNet studies reputation as a remedy for cooperation collapse in LLM-based multi-agent systems. The runner implements the dynamic dual-level reputation framework from the paper: agents update self/peer reputation from direct interactions and gossip, and rewire the network by forming or severing connections. Across investment, sign-up, and prisoner’s dilemma scenarios, RepuNet sustains cooperation, avoids collapse, and shows emergent behaviors such as cooperative clusters, isolation of exploitative agents, and a bias toward sharing positive over negative gossip. Agents reason through an LLM backend, and every simulation step is persisted to disk for inspection or resume.

## Requirements
- Python 3.13+
- A virtual environment tool (`uv`, `venv`, or `conda`)
- Access to an OpenAI-compatible API endpoint

## Install
```bash
# create venv (choose one)
uv venv && source .venv/bin/activate          # or .venv/Scripts/activate on Windows
python -m venv .venv && source .venv/bin/activate

# install deps
uv pip install -e .    # or: pip install -e .
```

## Configure the LLM + storage
Edit `utils.py` before running:
- `openai_api_key` / `key_owner`: your API key and an identifier (do not commit real keys).
- `llm_model` / `llm_api_base`: model name and base URL for your provider.
- `fs_storage`: where seeds and run outputs are written (default `./sim_storage`).

Runtime overrides: `LLM_MODEL`, `LLM_API_BASE`, `LLM_MAX_TOKENS`, `LLM_TEMPERATURE`, `LLM_TOP_P`, `LLM_FREQUENCY_PENALTY`, `LLM_PRESENCE_PENALTY`.

Example `utils.py` setup (swap in your own endpoint/key):
```python
import os

openai_api_key = os.getenv("OPENAI_API_KEY", "sk-your-key")  # load from env; avoid committing secrets
key_owner = "alice"

fs_storage = "./sim_storage"  # where seeds/runs are stored

llm_model = os.getenv("LLM_MODEL", "gpt-4o-mini")
llm_api_base = os.getenv("LLM_API_BASE", "https://api.your-endpoint/v1")

gpt_default_params = {
    "engine": llm_model,
    "max_tokens": int(os.getenv("LLM_MAX_TOKENS", "4096")),
    "temperature": float(os.getenv("LLM_TEMPERATURE", "0")),
    "top_p": float(os.getenv("LLM_TOP_P", "1")),
    "stream": False,
    "frequency_penalty": float(os.getenv("LLM_FREQUENCY_PENALTY", "0")),
    "presence_penalty": float(os.getenv("LLM_PRESENCE_PENALTY", "0")),
    "stop": None,
}

def default_gpt_params():
    return gpt_default_params.copy()
```
After saving, export your key in the shell (`export OPENAI_API_KEY=...`) and proceed to seed + run commands below.

## Seed data
Seeds live at `fs_storage/<sim_name>/step_0` with `reverie/meta.json` and per-persona memory/reputation files. Use the generator to build consistent seeds:
- Built-in personas:  
  ```bash
  python sim_storage/change_sim_folder.py --treatment investment --sim-name demo_invest
  ```
- Inherit learned fields from an existing seed:  
  ```bash
  python sim_storage/change_sim_folder.py --treatment investment --sim-name demo_invest --from-seed sim_storage/invest_seed/step_0
  ```
- Custom personas from JSON (either flat mapping or scenario-keyed):  
  ```bash
  python sim_storage/change_sim_folder.py --treatment pd_game --sim-name demo_pd --persona-file sim_storage/profiles.json
  ```
- Export learned fields from existing seeds for reuse:  
  ```bash
  python sim_storage/export_profiles.py --seeds sim_storage/invest_seed sim_storage/pd_game_seed sim_storage/sign_seed --out sim_storage/profiles.json
  ```

If a default seed is missing, `scripts/run_simulation.py` will auto-create one using the built-ins or `sim_storage/profiles.json` when present.

## Run simulations
### Interactive loop (`start.py`)
```bash
python start.py
```
Prompts:
- Simulation path under `fs_storage` (e.g., `investment_seed/step_0`)
- Use reputation? (y/n)
- Use gossip? (y/n)
- Scenario: Investment (`i`), Sign-up (`s`), or PD game (`p`)

Commands inside the loop:
- `run invest <steps>` / `run sign <steps>` / `run pd <steps>` (e.g., `run invest 3`)
- `save` (write current state), `fin` (save + exit), `exit` (delete current run folder and exit)

Each step copies the previous `step_x` to `step_{x+1}` and writes results into `investment results`, `sign up result`, or `pd_game results` under the new step folder.

### Non-interactive against an existing seed
```bash
python auto_run.py \
  --sim investment_seed/step_0 \
  --mode investment \
  --steps 3 \
  --reputation y \
  --gossip n
```

### Auto seed + run + resume
`scripts/run_simulation.py` finds or builds a seed, copies it to a timestamped run folder, and starts the scenario. It can also resume from any `step_x` inside `fs_storage`.
```bash
python scripts/run_simulation.py \
  --scenario pd \
  --steps 5 \
  --reputation y \
  --gossip n

# resume from an existing run (directory or specific step)
python scripts/run_simulation.py --scenario pd --steps 5 --sim run_pd/step_2
```

### Batch runs
Edit `scripts/batch_run.sh` (array `JOBS`) and execute:
```bash
bash scripts/batch_run.sh
```
Logs go to `outputs/<run_id>.log`; runs land in `fs_storage/<run_id>/step_*`.

## Useful paths
- `start.py`: interactive runner
- `auto_run.py`: non-interactive runner for an existing seed
- `scripts/run_simulation.py`: auto-seed/resume runner
- `scripts/batch_run.sh`: parallel launcher
- `sim_storage/change_sim_folder.py`: seed generator
- `sim_storage/export_profiles.py`: export personas’ learned fields to JSON
