from .prompt_template.run_gpt_prompt import (
    run_gpt_prompt_gossip_v2,
)


def first_order_gossip():
    generate_convo()


def generate_convo():
    convo = run_gpt_prompt_gossip_v2()[0]
    print(convo)
    return convo
