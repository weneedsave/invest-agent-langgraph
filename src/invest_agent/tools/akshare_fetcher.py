import akshare as ak
from invest_agent.vfs.filesystem import save_json, workspace_dir
from invest_agent.tools.clean import clean_profit

def code_to_symbol(code: str)->str:
    """
    A股代码转交易所前缀symbol
    60开头 → SH 上交所
    00/30开头 → SZ 深交所
    """
    if code.startswith(("60", "68")):
        return f"SH{code}"
    elif code.startswith(("00", "30")):
        return f"SZ{code}"
    elif code.startswith(("8", "4")):
        return f"BJ{code}"  # 北交所
    else:
        return code


def fetch_profit(code:str) -> str:
    symbol = code_to_symbol(code)
    df = ak.stock_profit_sheet_by_report_em(symbol)#获取数据
    clean = clean_profit(df)
    path = f"{workspace_dir(code)}/profit.json"
    return save_json(clean,path)