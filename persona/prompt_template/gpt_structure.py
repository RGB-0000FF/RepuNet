# import json
# import time

# import openai
# from openai import OpenAI

# from utils import *

# api_base = "https://api.claudeshop.top/v1"

# client = openai.OpenAI(api_key=openai_api_key, base_url=api_base)


# def temp_sleep(seconds=0.1):
#     time.sleep(seconds)


# def GPT_4o_request(prompt, gpt_parameter):
#     """
#     Given a prompt and a dictionary of GPT parameters, make a request to OpenAI
#     server and returns the response.
#     ARGS:
#       prompt: a str prompt
#       gpt_parameter: a python dictionary with the keys indicating the names of
#                      the parameter and the values indicating the parameter
#                      values.
#     RETURNS:
#       a str of GPT-4o-mini's response.
#     """
#     temp_sleep()
#     try:
#         if prompt.get("system"):
#             msg = [
#                 {"role": "system", "content": prompt["system"]},
#                 {"role": "user", "content": gpt_parameter["user"]},
#             ]
#         else:
#             msg = [{"role": "user", "content": gpt_parameter["user"]}]
#         completion = client.chat.completions.create(
#             model="gpt-4o-mini",
#             messages=msg,
#             max_tokens=gpt_parameter["max_tokens"],
#             top_p=gpt_parameter["top_p"],
#             frequency_penalty=gpt_parameter["frequency_penalty"],
#             presence_penalty=gpt_parameter["presence_penalty"],
#             temperature=gpt_parameter["temperature"],
#         )
#         return completion.choices[0].message.content
#     except Exception as e:
#         print("Exception: ", e)
#         return "Error"


# def safe_generate_response(
#     prompt,
#     gpt_parameter,
#     repeat=5,
#     fail_safe_response="error",
#     func_validate=None,
#     func_clean_up=None,
#     verbose=False,
# ):
#     if verbose:
#         print(prompt)

#     for i in range(repeat):
#         curr_gpt_response = GPT_4o_request(prompt, gpt_parameter)
#         if func_validate(curr_gpt_response, prompt=prompt):
#             return func_clean_up(curr_gpt_response, prompt=prompt)
#         if verbose:
#             print("---- repeat count: ", i, curr_gpt_response)
#             print(curr_gpt_response)
#             print("~~~~")
#     return fail_safe_response


# def generate_prompt(curr_input, prompt_lib_file):
#     """
#     Takes in the current input (e.g. comment that you want to classifiy) and
#     the path to a prompt file. The prompt file contains the raw str prompt that
#     will be used, which contains the following substr: !<INPUT>! -- this
#     function replaces this substr with the actual curr_input to produce the
#     final promopt that will be sent to the GPT3 server.
#     ARGS:
#       curr_input: the input we want to feed in (IF THERE ARE MORE THAN ONE
#                   INPUT, THIS CAN BE A LIST.)
#       prompt_lib_file: the path to the promopt file.
#     RETURNS:
#       a str prompt that will be sent to OpenAI's GPT server.
#     """
#     if isinstance(curr_input, str):
#         curr_input = [curr_input]
#     curr_input = [str(i) for i in curr_input]

#     f = open(prompt_lib_file, "r")
#     prompt = f.read()
#     f.close()
#     for count, i in enumerate(curr_input):
#         prompt = prompt.replace(f"!<INPUT {count}>!", i)
#     if "<commentblockmarker>###</commentblockmarker>" in prompt:
#         prompt = prompt.split("<commentblockmarker>###</commentblockmarker>")[1]
#     return prompt.strip()


# def print_run_prompts(
#     prompt_template=None,
#     persona=None,
#     gpt_param=None,
#     prompt_input=None,
#     prompt=None,
#     output=None,
# ):
#     print(f"=== {prompt_template}")
#     print("~~~ persona    ---------------------------------------------------")
#     print(persona.name, "\n")
#     print("~~~ gpt_param ----------------------------------------------------")
#     print(gpt_param, "\n")
#     print("~~~ prompt_input    ----------------------------------------------")
#     print(prompt_input, "\n")
#     print("~~~ prompt    ----------------------------------------------------")
#     print(prompt, "\n")
#     print("~~~ output    ----------------------------------------------------")
#     print(output, "\n")
#     print("=== END ==========================================================")
#     print("\n\n\n")


# def ChatGPT_safe_generate_response_OLD(
#     prompt,
#     repeat=3,
#     fail_safe_response="error",
#     func_validate=None,
#     func_clean_up=None,
#     verbose=False,
# ):
#     if verbose:
#         print("CHAT GPT PROMPT")
#         print(prompt)

#     for i in range(repeat):
#         try:
#             curr_gpt_response = ChatGPT_request(prompt).strip()
#             if func_validate(curr_gpt_response, prompt=prompt):
#                 return func_clean_up(curr_gpt_response, prompt=prompt)
#             if verbose:
#                 print(f"---- repeat count: {i}")
#                 print(curr_gpt_response)
#                 print("~~~~")

#         except Exception as e:
#             print(e)
#     print("FAIL SAFE TRIGGERED")
#     return fail_safe_response


# def ChatGPT_request(prompt):
#     """
#     Given a prompt and a dictionary of GPT parameters, make a request to OpenAI
#     server and returns the response.
#     ARGS:
#       prompt: a str prompt
#       gpt_parameter: a python dictionary with the keys indicating the names of
#                      the parameter and the values indicating the parameter
#                      values.
#     RETURNS:
#       a str of GPT-3's response.
#     """
#     # temp_sleep()
#     try:
#         completion = openai.ChatCompletion.create(
#             model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}]
#         )
#         return completion["choices"][0]["message"]["content"]

#     except Exception as e:
#         print("ChatGPT ERROR")
#         print(e)
#         return "ChatGPT ERROR"


# def get_embedding_v2(text, model="text-embedding-3-small"):
#     text = text.replace("\n", " ")
#     if not text:
#         text = "this is blank"
#     return openai.Embedding.create(input=[text], model=model)["data"][0]["embedding"]


# def ChatGPT_safe_generate_response(
#     prompt,
#     example_output,
#     special_instruction,
#     repeat=3,
#     fail_safe_response="error",
#     func_validate=None,
#     func_clean_up=None,
#     verbose=False,
# ):
#     # prompt = 'GPT-3 Prompt:\n"""\n' + prompt + '\n"""\n'
#     prompt = '"""\n' + prompt + '\n"""\n'
#     prompt += (
#         f"Output the response to the prompt above in json. {special_instruction}\n"
#     )
#     prompt += "Example output json:\n"
#     prompt += '{"output": "' + str(example_output) + '"}'

#     if verbose:
#         print("CHAT GPT PROMPT")
#         print(prompt)

#     for i in range(repeat):
#         try:
#             curr_gpt_response = ChatGPT_request(prompt).strip()
#             end_index = curr_gpt_response.rfind("}") + 1
#             curr_gpt_response = curr_gpt_response[:end_index]
#             curr_gpt_response = json.loads(curr_gpt_response)["output"]

#             # print ("---ashdfaf")
#             # print (curr_gpt_response)
#             # print ("000asdfhia")

#             if func_validate(curr_gpt_response, prompt=prompt):
#                 return func_clean_up(curr_gpt_response, prompt=prompt)

#             if verbose:
#                 print("---- repeat count: \n", i, curr_gpt_response)
#                 print(curr_gpt_response)
#                 print("~~~~")

#         except Exception as e:
#             print(e)

#     return False
