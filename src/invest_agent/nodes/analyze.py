from invest_agent.vfs.filesystem import read_json
from invest_agent.metrics import gross_margin, net_margin

def analyze(state: dict) -> dict:
    print("[analyze] 分析财务指标...")

    data = read_json(state["raw_data_path"])

    revenue = data["revenue"]
    operate_cost = data["operate_cost"]
    net_profit = data["net_profit"]

    gm = gross_margin(revenue, operate_cost)
    nm = net_margin(net_profit, revenue)

    return {
        "metrics": {
            "gross_margin": gm,  # 小数，如 0.8956
            "net_margin": nm,  # 小数，如 0.5075
        }
    }
