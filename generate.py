import openpyxl
import random
import time

from openai import OpenAI
from openlimit import ChatRateLimiter
from faker import Faker

PROPERTIES_WORKBOOK_FILE = "./properties.xlsx"
SENTENCES_TEXT_FILE = "./sentences.txt"

GPT_MODEL = "gpt-3.5-turbo"
GPT_TEMPERATURE = 0.8
GPT_FREQUENCY_PENALTY = 0.8
GPT_TPM = 60000
GPT_RPM = 500

PROMPT_SYSTEM_MESSAGE = """
你将被提供一组属性信息，你的任务是尽你的最大可能以各种不同的形式把这组属性组装成 3 句句式多样并尽可能连贯的话。如果某一属性的值为未知，你可以随机生成合适的值来代替。在你的回答中除了生成的句子外请不要包含任何其他的内容。
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
PROPERTY_CLASSES = {
    "address": ["地址", "住址", "地点", "位置"],
    "bank": ["网点", "银行", "分行", "支行"],
    "date_time": ["日期", "时间"],
    "phone_number": ["电话", "手机"],
}

fake = Faker("zh_CN")
rate_limiter = ChatRateLimiter(request_limit=GPT_RPM, token_limit=GPT_TPM)
openai_client = OpenAI(api_key="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")
used_group_hashes = []


def generate_random_property_group(worksheet, properties):
    group = random.sample(
        properties,
        random.randint(
            PROPERTY_GROUP_LENGTH_LOWER_BOUND, PROPERTY_GROUP_LENGTH_UPPER_BOUND
        ),
    )
    group_hash = hash(tuple(sorted(group)))

    if group_hash in used_group_hashes:
        return generate_random_property_group(worksheet, properties)

    used_group_hashes.append(group_hash)

    return {prop: worksheet[prop] for prop in group}


def generate_property_group_prompt(property_group):
    prompt = ""

    for prop in property_group.items():
        val = prop[1] if prop[1] is not None else generate_random_value(prop[0])
        prompt += f"{prop[0]}: {str(val).strip()}, "

    prompt = prompt[:-2]

    return prompt


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

    if response_message.finish_reason == "stop":
        return response_message.message.content

    return ""


def get_sentences_from_openai_response(response):
    sentences = response.split("\n")

    for idx, sentence in enumerate(sentences):
        # remove trailing and leading spaces
        sentence = sentence.strip()

        # remove leading numbers
        if sentence != "" and sentence[0].isdigit():
            sentences[idx] = sentence[3:]

    sentences = list(filter(lambda x: x != "", sentences))

    return sentences


def generate_sentences(worksheet):
    properties = list(worksheet.keys())
    property_group = generate_random_property_group(worksheet, properties)
    prompt = generate_property_group_prompt(property_group)

    print("Generating sentences from properties: ", prompt)

    response = get_openai_response(prompt)
    sentences = get_sentences_from_openai_response(response)

    print("Complete. Sentences: ", sentences)

    return sentences


def read_workbook():
    worksheet = {}

    wb = openpyxl.load_workbook(PROPERTIES_WORKBOOK_FILE)
    ws = wb.active

    for row in ws.rows:
        if row[0].value is None:
            continue
        worksheet[row[0].value] = row[1].value

    return worksheet


def generate_random_value(prop):
    if any(keyword in prop for keyword in PROPERTY_CLASSES["address"]):
        return fake.address()
    elif any(keyword in prop for keyword in PROPERTY_CLASSES["bank"]):
        return f"{fake.company()} 银行"
    elif any(keyword in prop for keyword in PROPERTY_CLASSES["date_time"]):
        return fake.date()
    elif any(keyword in prop for keyword in PROPERTY_CLASSES["phone_number"]):
        return fake.phone_number()

    return fake.word()


def save_to_textfile(sentences):
    with open(SENTENCES_TEXT_FILE, "a") as f:
        for sentence in sentences:
            f.write(sentence + "\n")


# --------------------------------------------

worksheet = read_workbook()
counter = 0
error_counter = 0

while True:
    if counter < 5 and error_counter < 5:
        try:
            sentences = generate_sentences(worksheet)
            save_to_textfile(sentences)
            print("")
            counter += 1
        except:
            print("Error occurred, retrying...")
            error_counter += 1
    else:
        break
