import  akshare as ak
#贵州茅台
def code_to_symbol(code: str) -> str:
    """
    A股代码转交易所前缀symbol
    60开头 → SH 上交所
    00/30开头 → SZ 深交所
    """
    if code.startswith(("60", "68")):
        return f"SH{code}"
    elif code.startswith(("00", "30")):
        return f"SZ{code}"
    else:
        return code

code = "600519"
symbol = code_to_symbol(code)

#利润表
profit = ak.stock_profit_sheet_by_report_em(symbol)
profit.to_csv("scripts/profit_600519.csv", index=False, encoding="utf-8-sig")

#资产负债表
balance = ak.stock_balance_sheet_by_report_em(symbol)
balance.to_csv("scripts/balance_600519.csv", index=False, encoding="utf-8-sig")

#现金流量表
cash = ak.stock_cash_flow_sheet_by_report_em(symbol)
cash.to_csv("scripts/cash_600519.csv", index=False, encoding="utf-8-sig")

"""#财务分析指标 (可能直接有 ROE/毛利率)
indicator = ak.stock_financial_analysis_indicator(symbol)
indicator.to_csv("scripts/indicator_600519.csv", index=False, encoding="utf-8-sig")
"""
print("全部csv文件已经输出到 scripts/ 目录：")