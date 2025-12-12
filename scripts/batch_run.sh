#!/usr/bin/env bash
set -euo pipefail

# Simple batch launcher: edit the JOBS array to configure experiments to run in parallel.

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON:-python}"
OUTPUT_DIR="${ROOT}/outputs"
if [[ ! -d "${OUTPUT_DIR}" ]]; then
  mkdir -p "${OUTPUT_DIR}"
  echo "[init] created output folder: ${OUTPUT_DIR}"
fi

# Configure experiments here (sample entries provided; add/remove as needed).
declare -a JOBS=(
  # "scenario=invest reputation=y gossip=y steps=1"
  # "scenario=sign reputation=y gossip=n steps=1"
  "scenario=pd gossip=n reputation=n steps=10"
  # "scenario=pd gossip=n reputation=n steps=60"
)

PIDS=()
LOGS=()

start_job() {
  local scenario="" reputation="" gossip="" steps=""
  for kv in "$@"; do
    case "${kv}" in
      scenario=*) scenario="${kv#*=}" ;;
      reputation=*) reputation="${kv#*=}" ;;
      gossip=*) gossip="${kv#*=}" ;;
      steps=*) steps="${kv#*=}" ;;
    esac
  done

  if [[ -z "${scenario}" || -z "${reputation}" || -z "${gossip}" || -z "${steps}" ]]; then
    echo "[error] job config missing fields: scenario/reputation/gossip/steps" >&2
    return 1
  fi

  local ts log_path
  ts="$(date +%Y%m%d_%H%M%S_%3N)" # Millisecond precision for readability
  local run_id="${scenario}_rep${reputation^^}_gos${gossip^^}_s${steps}_${ts}"
  log_path="${OUTPUT_DIR}/${run_id}.log"

  local sim_path="sim_storage/${run_id}/step_0"

  echo "[start] run_id=${run_id} scenario=${scenario} r=${reputation} g=${gossip} steps=${steps} log=${log_path} sim=${sim_path}"
  "${PYTHON_BIN}" "${ROOT}/scripts/run_simulation.py" \
    --scenario "${scenario}" \
    --reputation "${reputation}" \
    --gossip "${gossip}" \
    --steps "${steps}" \
    --sim-name "${run_id}" \
    >"${log_path}" 2>&1 &

  local pid=$!
  PIDS+=("${pid}")
  LOGS+=("${log_path}")
}

for job in "${JOBS[@]}"; do
  start_job ${job}
done

echo "[info] started ${#PIDS[@]} job(s), waiting..."
for idx in "${!PIDS[@]}"; do
  pid="${PIDS[$idx]}"
  log="${LOGS[$idx]}"
  if wait "${pid}"; then
    echo "[done] pid=${pid} log=${log}"
  else
    echo "[fail] pid=${pid} log=${log}"
  fi
done
