# SkyJSON

## 可执行文件

- `gen_file.py`:
  - 使用给定的模板句子生成不同类型的 Human-bot 问答对
- `generate_sentences.py`:
  - 使用 OpenAI API 使用给定的属性列表生成并模板化包含 5-10 个随机属性的句子 (long-running)
  - `generate_progress.py`
    - 汇报当前句子生成进度：属性利用量

<br/>

## 前置数据要求

\* 必须项:

- `gen_file.py`
  - \* data/sentences.txt
  - data/property_aliases.xlsx
  - data/text2json_templates.xlsx
  - data/json2json_templates.xlsx
  - data/text2table_templates.xlsx
- `generate_sentences.py`
  - \* data/properties.xlsx

<br/>

## 环境变量

在 `constants.py` 里进行配置:

- `VERBOSE`: 是否打印详细数据
- `DEBUGGING`: 是否打印过程数据
- `USE_PROPERTY_ALIASES`: 是否在问答中使用属性别名

<br/>

## 其他

- `gen_text_tpl.py`:
  - 生成 Human 提问时使用的属性列表模板
- `generate_value.py`
  - 使用 Faker 或 OpenAI API 为一属性生成合适的随机值
