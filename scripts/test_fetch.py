from invest_agent.tools.akshare_fetcher import fetch_profit

path = fetch_profit("600519")
print("已落盘:", path)

import json
with open(path, "r", encoding="utf-8") as f:
    print(json.load(f))