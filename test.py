import pytz
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

# 获取当前时间
current_time = datetime.now(pytz.utc)

# 加上三个月的时间
future_time = current_time + relativedelta(months=3)

# 将时间转换为指定格式的字符串
formatted_time = future_time.astimezone(pytz.utc).strftime('%Y-%m-%dT%H:%M:%S+00:00')

# 输出结果
print(formatted_time)