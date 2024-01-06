from faker import Faker
import pandas as pd

# 初始化 Faker
fake_zh_CN = Faker(locale='zh_CN')  # 可以根据需要选择合适的语言环境

count = 1000
# 生成模拟数据
data = {
    '月中文': [fake_zh_CN.month_name() for _ in range(count)],
    '月数字': [fake_zh_CN.month() for _ in range(count)],
    '年月中文': [fake_zh_CN.year() + "年" + fake_zh_CN.month_name() for _ in range(count)],
    '年月数字_横线': [fake_zh_CN.date(pattern="%Y-%m") for _ in range(count)],
    '年月数字_点': [fake_zh_CN.date(pattern="%Y.%m") for _ in range(count)],
    '年月数字_空格': [fake_zh_CN.date(pattern="%Y %m") for _ in range(count)],
    '年月日中文': [fake_zh_CN.date_time().strftime('%Y年%m月%d日') for _ in range(count)],
    '年月日数字_横线': [fake_zh_CN.date(pattern="%Y-%m-%d") for _ in range(count)],
    '年月日数字_点': [fake_zh_CN.date(pattern="%Y.%m.%d") for _ in range(count)],
    '年月日数字_空格': [fake_zh_CN.date(pattern="%Y %m %d") for _ in range(count)],
    '周': [fake_zh_CN.day_of_week() for _ in range(count)],
    '行用卡卡号': [fake_zh_CN.credit_card_number(card_type="mastercard") for _ in range(count)],
    '颜色rgb表示': [fake_zh_CN.hex_color() for _ in range(count)],
    '颜色英文表示': [fake_zh_CN.color_name() for _ in range(count)],
    '条形码': [fake_zh_CN.ean(length=13) for _ in range(count)],
    '英文地理位置+经纬度': [fake_zh_CN.local_latlng(country_code='CN') for _ in range(count)],
    '网址': [fake_zh_CN.url() for _ in range(count)],
    '英文书名': [fake_zh_CN.catch_phrase() for _ in range(count)],
    '人名': [fake_zh_CN.name() for _ in range(count)],
    '手机号': [fake_zh_CN.phone_number() for _ in range(count)],
}

# 创建一个 Excel 写入对象
writer = pd.ExcelWriter('attr_and_random_value.xlsx')

# 把每个数据列写入到不同的工作表
for col, values in data.items():
    df = pd.DataFrame({col: values})
    df.to_excel(writer, sheet_name=col, index=False)

# 保存并关闭 Excel 写入对象
writer._save()
