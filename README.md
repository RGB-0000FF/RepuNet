# RepuNet Simulation Runner

End-to-end runner for reputation-aware social simulations. The project supports multiple scenarios (Investment, Sign-up, and Prisoner’s Dilemma) with optional reputation and gossip mechanisms, and relies on an LLM backend for agent reasoning.

## Prerequisites
- Python 3.13+ (per `pyproject.toml`)
- A virtual environment manager (e.g., `uv`, `venv`, or `conda`)
- Access to an OpenAI-compatible API endpoint

## Installation
1) Create and activate a virtual environment  
   - With `uv`:  
     ```bash
     uv venv
     source .venv/bin/activate  # or .venv/Scripts/activate on Windows
     ```  
   - With built-in `venv`:  
     ```bash
     python -m venv .venv
     source .venv/bin/activate
     ```
2) Install dependencies from `pyproject.toml`:  
   ```bash
   uv pip install -e .   # or: pip install -e .
   ```

## Configure LLM access
Update `utils.py` in the repository root:
- Set `openai_api_key` and `key_owner`.
- Adjust `llm_model` and `llm_api_base` if you use a non-default model or endpoint.
- Set `fs_storage` to the folder where simulation runs and seeds will be stored (default: `./sim_storage`).

Environment variables such as `LLM_MODEL`, `LLM_API_BASE`, `LLM_MAX_TOKENS`, and `LLM_TEMPERATURE` can override the defaults at runtime.

## Prepare simulation seeds
Seeds live under `fs_storage/<sim_name>/step_0` and must include:
- `reverie/meta.json` with `persona_names` and `step`
- `personas/` (created automatically if empty)

Use the helper to generate consistent seeds:
- From built-ins:  
  ```bash
  python sim_storage/change_sim_folder.py --treatment investment --sim-name demo_invest
  ```
- Inherit learned data from an existing seed:  
  ```bash
  python sim_storage/change_sim_folder.py --treatment investment --sim-name demo_invest --from-seed sim_storage/invest_seed/step_0
  ```
- From a custom persona profile file:  
  ```bash
  python sim_storage/change_sim_folder.py --treatment pd_game --sim-name demo_pd --persona-file sim_storage/profiles.json
  ```

## Running simulations
You can run simulations interactively or in batch mode.

### Interactive (CLI)
```bash
python start.py
```
Follow the prompts:
- Simulation path (e.g., `investment_seed/step_0`)
- Enable reputation? (y/n)
- Enable gossip? (y/n)
- Scenario: Investment (`i`), Sign-up (`s`), or PD game (`p`)
- Commands inside the loop: `run <steps>` (e.g., `run 3`), `save`, `fin`, or `exit`

### Non-interactive single run
```bash
python auto_run.py \
  --sim investment_seed/step_0 \
  --mode investment \
  --steps 3 \
  --reputation y \
  --gossip n
```

### Auto seed + run (with resume support)
`scripts/run_simulation.py` will reuse an existing seed or create one automatically from `sim_storage/profiles.json`:
```bash
python scripts/run_simulation.py \
  --scenario pd \
  --steps 5 \
  --reputation y \
  --gossip n
# To resume an existing run:
python scripts/run_simulation.py --scenario pd --steps 5 --sim run_pd/step_2
```

### Batch runs
Edit `scripts/batch_run.sh` to list the jobs you want to run in parallel, then execute:
```bash
bash scripts/batch_run.sh
```
Logs are written to `outputs/<run_id>.log` and runs are stored under `fs_storage/<run_id>/step_*`.

## Folder layout (key paths)
- `fs_storage/`: root for seeds and generated runs
- `sim_storage/change_sim_folder.py`: seed generator
- `start.py`: interactive runner
- `auto_run.py`: non-interactive runner for an existing seed
- `scripts/run_simulation.py`: auto-seed/resume runner
- `scripts/batch_run.sh`: batch launcher

## Tips
- Ensure your API endpoint matches the model specified in `utils.py`.
- Clean up old run folders in `fs_storage` if storage grows large.
- If a run fails mid-way, you can resume from the latest `step_x` with `scripts/run_simulation.py --sim <path>`.
