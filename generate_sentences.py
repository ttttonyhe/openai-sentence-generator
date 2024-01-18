import os
import sys
import time
import random
import traceback

from constants import *
from openai import OpenAI
from dotenv import load_dotenv
from openlimit import ChatRateLimiter
from generate_helpers import (
    GroupHashAlreadyUsedException,
    strip_whitespaces,
    compress_newlines,
    read_properties_workbook,
    read_generated_property_values_workbook,
    read_used_group_hashes,
    read_used_properties,
    save_sentences_to_textfile,
    save_generated_property_values_to_workbook,
    save_used_group_hashes_to_file,
    save_used_properties_to_file,
    print_header,
    print_success,
    print_info,
    print_warning,
    print_error,
)
from generate_value import random_value

MAX_NUMBER_OF_GENERATIONS = 0
MAX_NUMBER_OF_FAILURES = 200

PROMPT_SYSTEM_MESSAGE = """
你将被提供一组属性信息，你的任务是尽你的最大可能以各种不同的形式把这组属性组装成 3 句句式多样并尽可能连贯的话。在你的回答中除了生成的句子外请不要包含任何其他的内容或标点符号，并且请尽可能避免修改属性值在句子中的表现方式。如果你觉得生成通顺的句子真的非常困难，请务必仅回答 "未知"。
"""
PROMPT_EXAMPLE_USER_MESSAGE = """
姓名: 张三, 年龄: 20, 生日: 1990-05-04
"""
PROMPT_EXAMPLE_ASSISTANT_MESSAGE = """
1. 我的姓名是张三，今年 20 岁，出生在 1990 年 5 月 4 日，很高兴认识大家。\n\n
2. 我叫张三，今年已经 20 岁了，我出生在 1990 年 5 月 4 日。\n\n
3. 张三是我的名字，我出生在 1990 年 5 月 4 日，今年 20 岁。
"""

PROPERTY_GROUP_LENGTH_LOWER_BOUND = 5
PROPERTY_GROUP_LENGTH_UPPER_BOUND = 10

load_dotenv()
rate_limiter = ChatRateLimiter(request_limit=GPT_RPM, token_limit=GPT_TPM)
openai_client = OpenAI()


# Data --------------------------------------------

worksheet = read_properties_workbook()
used_group_hashes = read_used_group_hashes()
generated_property_values = read_generated_property_values_workbook()
used_properties = read_used_properties()

# Logic --------------------------------------------


def generate_random_property_group(worksheet, properties):
    group_size_lower_bound = min(PROPERTY_GROUP_LENGTH_LOWER_BOUND, len(properties))
    group_size_upper_bound = min(PROPERTY_GROUP_LENGTH_UPPER_BOUND, len(properties))

    group = random.sample(
        properties,
        random.randint(group_size_lower_bound, group_size_upper_bound),
    )
    group_hash = hash(tuple(sorted(group)))

    if group_hash in used_group_hashes:
        raise GroupHashAlreadyUsedException

    used_group_hashes.append(group_hash)

    return {prop: worksheet[prop] for prop in group}


def generate_property_group_prompt(property_group):
    global generated_property_values

    new_property_group = property_group
    prompt = ""

    for prop, val in property_group.items():
        final_val = val

        if final_val is None:
            final_val, generated_property_values = random_value(
                prop, generated_property_values
            )

        final_val = str(final_val).strip()
        new_property_group[prop] = final_val
        prompt += f"{prop}: {final_val}, "

    prompt = prompt[:-2]

    return prompt, new_property_group


def get_openai_response(prompt):
    openai_params = {
        "model": GPT_MODEL,
        "temperature": GPT_TEMPERATURE,
        "frequency_penalty": GPT_FREQUENCY_PENALTY,
        "messages": [
            # System message
            {"role": "system", "content": PROMPT_SYSTEM_MESSAGE},
            # Example
            {"role": "user", "content": PROMPT_EXAMPLE_USER_MESSAGE},
            {"role": "assistant", "content": PROMPT_EXAMPLE_ASSISTANT_MESSAGE},
            # User message
            {"role": "user", "content": prompt},
        ],
    }

    with rate_limiter.limit(**openai_params):
        response = openai_client.chat.completions.create(**openai_params)

    response_message = response.choices[0]
    response_message_content = response_message.message.content.strip()

    if response_message.finish_reason == "stop" and response_message_content != "未知":
        return response_message_content

    return ""


def generate_sentences(worksheet):
    print_header("[+] Pre-processing")
    properties = list(worksheet.keys())
    property_group = generate_random_property_group(worksheet, properties)
    prompt, property_group = generate_property_group_prompt(property_group)
    print_success("--> Pre-processing")

    print_header("[+] Main process")
    print_info(" => Generating sentences from properties: ", prompt)
    response = get_openai_response(prompt)
    sentences = get_sentences_from_openai_response(response, property_group)
    print_success("--> Main process done")

    print_header("[+] Results")
    print_info(" => Sentences: ", sentences)
    print_success("--> Results shown")

    return sentences


# Logic helpers --------------------------------------------


def get_sentences_from_openai_response(response, property_group):
    sentences = compress_newlines(response).split("\n")

    for idx, sentence in enumerate(sentences):
        # remove trailing and leading spaces
        sentence = strip_whitespaces(sentence)

        # remove leading numbers
        if sentence != "" and sentence[0].isdigit():
            sentences[idx] = sentence[2:]

    # filter out invalid sentences
    sentences = list(
        filter(
            lambda x: x != ""
            and not x.startswith("未知")
            and not x.startswith("Sorry")
            and not x.startswith("抱歉")
            and not x.startswith("注意")
            and "Note" not in x
            and "连贯" not in x,
            sentences,
        )
    )

    # templatize sentences
    for idx, sentence in enumerate(sentences):
        for prop in property_group.items():
            if "是否" not in prop[0]:
                sentences[idx] = sentences[idx].replace(
                    strip_whitespaces(str(prop[1])), f"{{{{{prop[0]}}}}}"
                )

    # record properties used
    for prop in property_group.items():
        used_properties.add(prop[0])

    return sentences


def save_transactional_data(gpv, ugh, up):
    if gpv:
        save_generated_property_values_to_workbook(gpv)

    if ugh:
        save_used_group_hashes_to_file(ugh)

    if up:
        save_used_properties_to_file(up)


# Main --------------------------------------------

# Main loop
success_count = 0
failure_count = 0

while True:
    if (
        MAX_NUMBER_OF_GENERATIONS == 0 or success_count < MAX_NUMBER_OF_GENERATIONS
    ) and (MAX_NUMBER_OF_FAILURES == 0 or failure_count < MAX_NUMBER_OF_FAILURES):
        try:
            print_success("==> Generating sentences")
            sentences = generate_sentences(worksheet)
            save_sentences_to_textfile(sentences)

            print_header("[+] Post-processing")
            save_transactional_data(
                generated_property_values, used_group_hashes, used_properties
            )
            print_success("--> Post-processing done")

            print_success("--> Generating sentences done\n")
            time.sleep(2)
            success_count += 1
        except KeyboardInterrupt:
            print_error(" => Keyboard interrupted, exiting...")
            break
        except GroupHashAlreadyUsedException:
            print_warning(" => Group hash already used, retrying...")
            failure_count += 1
        except:
            print_warning(
                " => Rate limit reached or an error has occurred, retrying in 10 seconds..."
            )
            traceback.print_exc()
            failure_count += 1
            time.sleep(10)
    else:
        break

print_header("[+] Saving transactional data")
save_transactional_data(generated_property_values, used_group_hashes, used_properties)
print_success("--> Saving transactional data done")

sys.exit(0)
