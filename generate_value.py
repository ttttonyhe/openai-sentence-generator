import time
import random
import traceback

from faker import Faker
from constants import *
from openai import OpenAI
from dotenv import load_dotenv
from generate_helpers import (
    strip_whitespaces,
    print_header,
    print_success,
    print_info,
    print_warning,
    print_error,
)
from openlimit import ChatRateLimiter

load_dotenv()

fake = Faker("zh_CN")
fake.seed_instance(int(time.time()))

PROPERTY_CLASS_KEYWORDS = {
    "address": ["地址", "住址", "地点", "位置"],
    "bank": ["网点", "银行", "分行", "支行"],
    "date_time": ["日期", "时间", "生日", "期限"],
    "phone_number": ["电话", "手机", "联系方式"],
    "card_number": ["卡号", "账号", "账户"],
    "id": [
        "ID",
        "编码",
        "证件号",
        "证号",
        "籍号",
        "编号",
        "序号",
        "文号",
        "执照",
        "登记证",
        "代码",
        "身份证",
        "护照",
        "单号",
        "书号",
    ],
    "integer": [
        "库存",
        "数量",
        "人数",
        "成绩",
        "量",
        "价值",
        "流量",
        "净额",
        "现金",
        "总价",
        "单价",
        "行号",
        "次号",
        "位号",
    ],
    "small_integer": ["班级", "批次", "等级", "年级", "排名", "得分", "次数", "年龄", "分数", "楼层", "区块"],
    "city": ["站", "地点", "位置"],
    "ph_value": ["PH"],
    "length": [
        "长度",
        "宽度",
        "高度",
        "厚度",
        "深度",
        "直径",
        "半径",
    ],
    "weight": ["重量", "质量", "体重", "水量", "容量", "毛重", "净重", "气量", "油量"],
    "temperature": ["温度"],
    "speed": ["速度"],
    "area": ["面积"],
    "volume": ["体积"],
    "pressure": ["压力"],
    "energy": ["能量, 电量"],
    "power": ["功率"],
    "voltage": ["电压"],
    "current": ["电流"],
    "frequency": ["频率"],
    "angle": ["角度"],
    "geolocation": ["经度", "纬度"],
    "yes_no": ["是否"],
    "name": ["姓名", "名字", "负责人", "创建人", "更新人", "修改人", "购票人", "联系人", "审核人"],
    "content": ["内容", "描述", "说明", "备注"],
    "money": ["金额", "价格", "费用", "成本"],
    "country": ["国家", "国籍"],
    "gender": ["性别"],
    "company": ["公司", "企业", "单位", "机构"],
    "percent": ["比例", "浓度", "率", "折旧", "概率"],
    "color": ["颜色"],
    "ip": ["IP"],
    "url": ["URL"],
    "email": ["邮箱", "电子邮件"],
}

VALUE_PROMPT_SYSTEM_MESSAGE = """
你将被提供一种属性 (如: 日期, 班级等)，你的任务是给出 10 个该属性的示例值 (如: 1990 年 1 月 1 日, 2020 届 1 班等)。在你的回答中除了生成的示例外请不要包含任何其他的内容、序号或标点符号，示例请务必只用 ";" 隔开。如果你不能给出示例值，请回答 "未知"。
"""
VALUE_PROMPT_EXAMPLE_USER_MESSAGE = """
姓名
"""
VALUE_PROMPT_EXAMPLE_ASSISTANT_MESSAGE = """
张三;李四;王五;小明;小红;赵六;刘七;朱八;郑九;刘芳
"""


def get_openai_value_response(prop):
    rate_limiter = ChatRateLimiter(request_limit=GPT_RPM, token_limit=GPT_TPM)
    openai_client = OpenAI()

    openai_params = {
        "model": GPT_MODEL,
        "temperature": GPT_TEMPERATURE,
        "frequency_penalty": GPT_FREQUENCY_PENALTY,
        "messages": [
            # System message
            {"role": "system", "content": VALUE_PROMPT_SYSTEM_MESSAGE},
            # Example
            {"role": "user", "content": VALUE_PROMPT_EXAMPLE_USER_MESSAGE},
            {"role": "assistant", "content": VALUE_PROMPT_EXAMPLE_ASSISTANT_MESSAGE},
            # User message
            {"role": "user", "content": prop},
        ],
    }

    with rate_limiter.limit(**openai_params):
        response = openai_client.chat.completions.create(**openai_params)

    response_message = response.choices[0]

    if response_message.finish_reason == "stop":
        return response_message.message.content.strip()

    return None


def random_value(prop, generated_property_values, offline=False, ignore_units=False):
    print_info(" => Generating random value for property: ", prop)

    random_value = None
    new_generated_property_values = generated_property_values

    # First, try to match keywords and use Faker to generate a value
    random_float = fake.pyfloat(positive=True, min_value=1, max_value=100)

    if any(keyword in prop for keyword in PROPERTY_CLASS_KEYWORDS["address"]):
        random_value = fake.address()
    elif any(keyword in prop for keyword in PROPERTY_CLASS_KEYWORDS["bank"]):
        random_value = f"{fake.company()} 银行"
    elif any(keyword in prop for keyword in PROPERTY_CLASS_KEYWORDS["date_time"]):
        random_value = fake.date(pattern="%Y年%m月%d日")
    elif any(keyword in prop for keyword in PROPERTY_CLASS_KEYWORDS["phone_number"]):
        random_value = fake.phone_number()
    elif any(keyword in prop for keyword in PROPERTY_CLASS_KEYWORDS["card_number"]):
        random_value = fake.credit_card_number(card_type="mastercard")
    elif any(keyword in prop for keyword in PROPERTY_CLASS_KEYWORDS["id"]):
        random_value = fake.passport_number()
    elif any(keyword in prop for keyword in PROPERTY_CLASS_KEYWORDS["integer"]):
        random_value = fake.random_int(min=1)
    elif any(keyword in prop for keyword in PROPERTY_CLASS_KEYWORDS["small_integer"]):
        random_value = fake.random_int(min=1, max=100)
    elif any(keyword in prop for keyword in PROPERTY_CLASS_KEYWORDS["city"]):
        random_value = fake.city()
    elif any(keyword in prop for keyword in PROPERTY_CLASS_KEYWORDS["ph_value"]):
        random_value = fake.pyfloat(min_value=0, max_value=14)
    elif any(keyword in prop for keyword in PROPERTY_CLASS_KEYWORDS["length"]):
        random_value = random_float if ignore_units else f"{random_float} 米"
    elif any(keyword in prop for keyword in PROPERTY_CLASS_KEYWORDS["weight"]):
        random_value = random_float if ignore_units else f"{random_float} 千克"
    elif any(keyword in prop for keyword in PROPERTY_CLASS_KEYWORDS["temperature"]):
        random_value = random_float if ignore_units else f"{random_float} 摄氏度"
    elif any(keyword in prop for keyword in PROPERTY_CLASS_KEYWORDS["speed"]):
        random_value = random_float if ignore_units else f"{random_float} 公里每小时"
    elif any(keyword in prop for keyword in PROPERTY_CLASS_KEYWORDS["area"]):
        random_value = random_float if ignore_units else f"{random_float} 平方米"
    elif any(keyword in prop for keyword in PROPERTY_CLASS_KEYWORDS["volume"]):
        random_value = random_float if ignore_units else f"{random_float} 立方米"
    elif any(keyword in prop for keyword in PROPERTY_CLASS_KEYWORDS["pressure"]):
        random_value = random_float if ignore_units else f"{random_float} 帕"
    elif any(keyword in prop for keyword in PROPERTY_CLASS_KEYWORDS["energy"]):
        random_value = random_float if ignore_units else f"{random_float} 焦"
    elif any(keyword in prop for keyword in PROPERTY_CLASS_KEYWORDS["power"]):
        random_value = random_float if ignore_units else f"{random_float} 瓦"
    elif any(keyword in prop for keyword in PROPERTY_CLASS_KEYWORDS["voltage"]):
        random_value = random_float if ignore_units else f"{random_float} 伏"
    elif any(keyword in prop for keyword in PROPERTY_CLASS_KEYWORDS["current"]):
        random_value = random_float if ignore_units else f"{random_float} 安"
    elif any(keyword in prop for keyword in PROPERTY_CLASS_KEYWORDS["frequency"]):
        random_value = random_float if ignore_units else f"{random_float} 赫兹"
    elif any(keyword in prop for keyword in PROPERTY_CLASS_KEYWORDS["angle"]):
        random_value = f"{fake.pyfloat(positive=True, min_value=1, max_value=100)} °"
    elif any(keyword in prop for keyword in PROPERTY_CLASS_KEYWORDS["geolocation"]):
        random_value = fake.latitude()
    elif any(keyword in prop for keyword in PROPERTY_CLASS_KEYWORDS["yes_no"]):
        random_value = "是" if fake.pybool() else "否"
    elif any(keyword in prop for keyword in PROPERTY_CLASS_KEYWORDS["name"]):
        random_value = fake.name()
    elif any(keyword in prop for keyword in PROPERTY_CLASS_KEYWORDS["content"]):
        random_value = fake.catch_phrase()
    elif any(keyword in prop for keyword in PROPERTY_CLASS_KEYWORDS["money"]):
        random_value = (
            fake.random_int(min=1) if ignore_units else f"{fake.random_int(min=1)} 元"
        )
    elif any(keyword in prop for keyword in PROPERTY_CLASS_KEYWORDS["country"]):
        random_value = fake.country()
    elif any(keyword in prop for keyword in PROPERTY_CLASS_KEYWORDS["gender"]):
        random_value = "男" if fake.pybool() else "女"
    elif any(keyword in prop for keyword in PROPERTY_CLASS_KEYWORDS["company"]):
        random_value = fake.company()
    elif any(keyword in prop for keyword in PROPERTY_CLASS_KEYWORDS["percent"]):
        random_value = random_float if ignore_units else f"{random_float}%"
    elif any(keyword in prop for keyword in PROPERTY_CLASS_KEYWORDS["color"]):
        random_value = fake.color_name()
    elif any(keyword in prop for keyword in PROPERTY_CLASS_KEYWORDS["ip"]):
        random_value = fake.ipv4()
    elif any(keyword in prop for keyword in PROPERTY_CLASS_KEYWORDS["url"]):
        random_value = fake.url()
    elif any(keyword in prop for keyword in PROPERTY_CLASS_KEYWORDS["email"]):
        random_value = fake.email()

    if random_value is not None:
        print_info(" => => Random value generated by Faker: ", random_value)
        return random_value, new_generated_property_values

    # If no match, try to generate a value using ChatGPT
    try:
        # Read from previously generated values
        if (
            prop in generated_property_values
            and len(generated_property_values[prop]) > 1
        ):
            random_value = random.choice(generated_property_values[prop])
            print_info(
                " => => Using random value previously generated by ChatGPT: ",
                random_value,
            )
            return random_value, new_generated_property_values

        # If no previously generated values, generate new values
        if not offline:
            random_value = get_openai_value_response(prop)
            if (
                random_value.startswith("未知")
                or random_value.startswith("请")
                or "抱歉" in random_value
                or random_value is None
            ):
                random_value = None
            else:
                new_generated_property_values[prop] = strip_whitespaces(
                    random_value
                ).split(";")

                if len(new_generated_property_values[prop]) > 1:
                    random_value = random.choice(new_generated_property_values[prop])
                else:
                    random_value = None

            # Sleep for 1 second to avoid OpenAI rate limit
            time.sleep(1)
    except:
        traceback.print_exc()
        print_warning(" => => Using Faker...")

    if random_value is not None:
        print_info(" => => Random value generated by ChatGPT: ", random_value)
        return random_value, new_generated_property_values
    else:
        random_value = fake.word()
        print_info(" => => Random value generated by Faker: ", random_value)

    return random_value, new_generated_property_values
