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

    result = {}
    for raw_col, std_col in FIELD_MAP.items():
        if raw_col in df.columns:
            val = df[raw_col].iloc[0]
            if not pd.isna(val):  #如果不为空
                if raw_col == "REPORT_DATE":  #如果是日期
                    result[std_col] = val
                else:
                    result[std_col] = float(val)
            else:
                result[std_col] = None
        else:
            result[std_col] = None
    return result


