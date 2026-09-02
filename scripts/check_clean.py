import pandas as pd
from invest_agent.tools.clean import clean_profit

# 情况1：茅台（列齐全）
df1 = pd.read_csv("scripts/profit_600519.csv")
print("茅台:", clean_profit(df1))

# 情况2：银行（缺 OPERATE_COST）
df2 = pd.DataFrame({
      "REPORT_DATE": ["2026-06-30"],
      "OPERATE_INCOME": [100.0],
      "NETPROFIT": [30.0],
      "PARENT_NETPROFIT": [28.0],
      "BASIC_EPS": [2.0],
})
print("银行:", clean_profit(df2))

  # 情况3：列存在但值是 NaN
df3 = pd.DataFrame({
      "REPORT_DATE": ["2026-06-30"],
      "OPERATE_INCOME": [100.0],
      "OPERATE_COST": [float("nan")],   # 列在，值是 NaN
      "NETPROFIT": [30.0],
      "PARENT_NETPROFIT": [28.0],
      "BASIC_EPS": [2.0],
})
print("列在但NaN:", clean_profit(df3))
