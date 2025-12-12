import inspect
import os
import time
from pathlib import Path
from typing import Any, Dict, Optional

from openai import OpenAI

try:
    # User-provided configuration lives in utils.py
    from utils import openai_api_key, llm_model, llm_api_base, gpt_default_params, default_gpt_params  # type: ignore
except Exception:
    openai_api_key = os.getenv("OPENAI_API_KEY", "")
    llm_model = os.getenv("LLM_MODEL", "gpt-4o-mini")
    llm_api_base = os.getenv("LLM_API_BASE", "https://api.claudeshop.top/v1")
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

    def default_gpt_params():  # type: ignore
        return gpt_default_params.copy()


def temp_sleep(seconds: float = 0.1) -> None:
    time.sleep(seconds)


def resolve_llm(engine: Optional[str] = None, llm_config: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
    """
    Choose which LLM to call:
    - Prefer an explicit override from llm_config
    - Otherwise fall back to llm_model / llm_api_base from utils.py
    (Ignore any hardcoded engine in gpt_param to keep a single source of truth)
    """
    resolved = {"api_name": llm_model, "api_base": llm_api_base}

    if llm_config:
        resolved["api_name"] = llm_config.get("api_name") or resolved["api_name"]
        resolved["api_base"] = llm_config.get("api_base") or llm_config.get("url") or resolved["api_base"]
    return resolved


def llm_request(prompt: Any, gpt_parameter: Dict[str, Any], llm_config: Optional[Dict[str, Any]] = None) -> str:
    """
    Shared LLM caller that supports multiple backends via resolve_llm.
    """
    temp_sleep()
    # Always use llm_model / llm_api_base from utils.py (or llm_config override), ignoring engine in gpt_param
    resolved = resolve_llm(llm_config=llm_config)
    # Start from utils defaults and let caller-provided gpt_parameter override selected keys
    base_params = default_gpt_params()
    gpt_parameter = {**base_params, **(gpt_parameter or {})}
    gpt_parameter["engine"] = resolved["api_name"]
    client = OpenAI(api_key=openai_api_key, base_url=resolved["api_base"])
    try:
        if isinstance(prompt, dict):
            messages = []
            if prompt.get("system"):
                messages.append({"role": "system", "content": prompt["system"]})
            if prompt.get("user"):
                messages.append({"role": "user", "content": prompt["user"] + "\nDONOT OUPUT OUT OF ANY Desired format words!"})
        else:
            messages = [{"role": "user", "content": prompt}]

        completion = client.chat.completions.create(
            model=resolved["api_name"],
            messages=messages,
            max_tokens=gpt_parameter.get("max_tokens", 4096),
            top_p=gpt_parameter.get("top_p", 1),
            frequency_penalty=gpt_parameter.get("frequency_penalty", 0),
            presence_penalty=gpt_parameter.get("presence_penalty", 0),
            temperature=gpt_parameter.get("temperature", 0),
        )
        return completion.choices[0].message.content
    except Exception as e:
        print("Exception in LLM GENERATION: ", e)
        return "Error"


def safe_generate_response(
    prompt: Any,
    gpt_parameter: Dict[str, Any],
    repeat: int = 5,
    fail_safe_response: Any = "error",
    func_validate=None,
    func_clean_up=None,
    verbose: bool = False,
    llm_config: Optional[Dict[str, Any]] = None,
):
    if verbose:
        print(prompt)

    for i in range(repeat):
        curr_gpt_response = llm_request(prompt, gpt_parameter, llm_config)
        if func_validate is None or func_validate(curr_gpt_response, prompt=prompt):
            return func_clean_up(curr_gpt_response, prompt=prompt) if func_clean_up else curr_gpt_response
        if verbose:
            print("---- repeat count: ", i, curr_gpt_response)
            print(curr_gpt_response)
            print("~~~~")
    return fail_safe_response


def _resolve_prompt_path(prompt_lib_file: str) -> Path:
    prompt_path = Path(prompt_lib_file)
    if prompt_path.is_absolute():
        return prompt_path

    for frame in inspect.stack()[2:]:
        frame_path = Path(frame.filename).resolve()
        if frame_path != Path(__file__).resolve():
            return frame_path.parent / prompt_lib_file
    return Path.cwd() / prompt_lib_file


def generate_prompt_role_play(curr_input, prompt_lib_file, role_play: bool = True):
    """
    Reads a prompt template and fills !<INPUT i>! placeholders.
    When role_play is True, returns a {"system":..., "user":...} dict.
    """
    if isinstance(curr_input, str):
        curr_input = [curr_input]
    curr_input = [str(i) for i in curr_input]
    prompt_lib_file = _resolve_prompt_path(prompt_lib_file)

    with open(prompt_lib_file, "r", encoding="utf-8") as f:
        prompt = f.read()
    for count, i in enumerate(curr_input):
        prompt = prompt.replace(f"!<INPUT {count}>!", i)
    if "<commentblockmarker>###</commentblockmarker>" in prompt:
        prompt = prompt.split("<commentblockmarker>###</commentblockmarker>")[1]
    if role_play:
        return {"system": curr_input[0], "user": prompt.strip()}
    return {"user": prompt.strip()}


def generate_prompt(curr_input, prompt_lib_file):
    """
    Same as generate_prompt_role_play but returns a plain string prompt.
    """
    if isinstance(curr_input, str):
        curr_input = [curr_input]
    curr_input = [str(i) for i in curr_input]
    prompt_lib_file = _resolve_prompt_path(prompt_lib_file)

    with open(prompt_lib_file, "r", encoding="utf-8") as f:
        prompt = f.read()
    for count, i in enumerate(curr_input):
        prompt = prompt.replace(f"!<INPUT {count}>!", i)
    if "<commentblockmarker>###</commentblockmarker>" in prompt:
        prompt = prompt.split("<commentblockmarker>###</commentblockmarker>")[1]
    return prompt.strip()


def print_run_prompts(
    prompt_template=None,
    persona=None,
    gpt_param=None,
    prompt_input=None,
    prompt=None,
    output=None,
):
    print(f"=== {prompt_template}")
    if persona:
        print("~~~ persona    ---------------------------------------------------")
        print(getattr(persona, "name", persona), "\n")
    print("~~~ gpt_param ----------------------------------------------------")
    print(gpt_param, "\n")
    print("~~~ prompt_input    ----------------------------------------------")
    print(prompt_input, "\n")
    print("~~~ prompt    ----------------------------------------------------")
    print(prompt, "\n")
    print("~~~ output    ----------------------------------------------------")
    print(output, "\n")
    print("=== END ==========================================================")
    print("\n\n\n")
