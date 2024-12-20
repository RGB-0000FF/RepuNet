gpt_parameter = {"max_tokens": 4096, "top_p": 1, "frequency_penalty": 0, "presence_penalty": 0, "temperature": 0, }

prompt = "who are u?"

res = GPT4o_request(prompt, gpt_parameter)
print(res)
