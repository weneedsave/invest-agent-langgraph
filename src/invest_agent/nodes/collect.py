from invest_agent.tools.akshare_fetcher import fetch_profit

def collect(state: dict) -> dict:
    code = state["code"]
    print(f"[collect] 采集股票 {code} 数据...")
    path = fetch_profit(code)
    print(f"[collect]数据已落盘:{path}")
    return {"raw_data_path":  path}