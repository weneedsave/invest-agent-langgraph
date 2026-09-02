import pandas as pd
FIELD_MAP = {
      "REPORT_DATE": "report_date",#日期
      "OPERATE_INCOME": "revenue",#收入
      "OPERATE_COST": "operate_cost",#成本
      "NETPROFIT": "net_profit",#利润
      "PARENT_NETPROFIT": "parent_netprofit",#归母净利润
      "BASIC_EPS": "eps",#基本每股收益
}


def clean_profit(df : pd.DataFrame) -> dict:
    selected = df.rename(columns=FIELD_MAP)[list(FIELD_MAP.values())]

    #取第一行最新(按位取第零行)
    latest = selected.iloc[0]
    #转成dict返回
    return latest.to_dict()