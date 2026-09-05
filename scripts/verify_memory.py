from dotenv import load_dotenv
load_dotenv()

import sys
from langchain_core.messages import HumanMessage
from langgraph.store.sqlite import SqliteStore
from invest_agent.demo_graph import build_demo_graph
from invest_agent.vfs.filesystem import read_json
from invest_agent.metrics import gross_margin, net_margin


def format_profit_data(code):
    data = read_json(f"workspace/{code}/profit.json")
    revenue = data.get("revenue"); operate_cost = data.get("operate_cost")
    net_profit = data.get("net_profit"); parent_netprofit = data.get("parent_netprofit")
    eps = data.get("eps"); report_date = data.get("report_date")
    to_yi = lambda v: None if v is None else round(v / 1e8, 2)
    gm = gross_margin(revenue, operate_cost)
    nm = net_margin(net_profit, revenue)
    lines = [
        f"【财报原始数据｜报告日期:{report_date}】",
        f"- 营业收入：{to_yi(revenue)} 亿元",
        f"- 营业成本：{to_yi(operate_cost)} 亿元",
        f"- 净利润：{to_yi(net_profit)} 亿元",
        f"- 归母净利润：{to_yi(parent_netprofit)} 亿元",
        f"- 每股收益EPS：{eps}",
        f"- 毛利率：{gm:.2%}",
        f"- 净利率：{nm:.2%}",
    ]
    return "\n".join(lines)


code = "600519"
question = "分析一下贵州茅台的财务状况"
prompt = f"【财报数据】\n{format_profit_data(code)}\n\n【用户问题】\n{question}"

# 关键：每次运行都连同一个 memory.sqlite，实现跨进程持久
with SqliteStore.from_conn_string("memory.sqlite") as store:
    app = build_demo_graph(store=store)
    result = app.invoke({"messages": [HumanMessage(content=prompt)], "code": code})

    ai_msgs = [m for m in result["messages"] if m.type == "ai"]
    print(f"本次 AI 消息条数: {len(ai_msgs)}")
    print(f"最后一条 AI 消息开头: {result['messages'][-1].content[:80]}")
