from dotenv import load_dotenv
load_dotenv()

from langchain_core.messages import HumanMessage
from invest_agent.demo_graph import build_demo_graph
from invest_agent.vfs.filesystem import read_json
from invest_agent.metrics import gross_margin,net_margin
from langgraph.store.sqlite import SqliteStore



def format_profit_data(code: str) -> str:
    """读取profit.json，单位转亿元，复用metrics模块计算指标，输出给LLM阅读的文本"""
    data = read_json(f"workspace/{code}/profit.json")

    # 原始数值：单位【元】，交给metrics做计算，保证精度
    revenue = data.get("revenue")
    operate_cost = data.get("operate_cost")
    net_profit = data.get("net_profit")
    parent_netprofit = data.get("parent_netprofit")
    eps = data.get("eps")
    report_date = data.get("report_date")

    def to_yi(val):
        """仅用于展示：元 → 亿元，保留2位小数"""
        if val is None:
            return None
        return round(val / 10**8, 2)

    # 展示用：转为亿元
    rev_yi = to_yi(revenue)
    cost_yi = to_yi(operate_cost)
    np_yi = to_yi(net_profit)
    pnp_yi = to_yi(parent_netprofit)

    # ✅复用metrics模块，传入原始（元）的原始数据，不使用四舍五入后的亿元值，避免精度偏移
    gm = gross_margin(revenue, operate_cost)
    nm = net_margin( net_profit,revenue)

    lines = []
    lines.append(f"【财报原始数据｜报告日期:{report_date}】")
    lines.append(f"- 营业收入：{rev_yi} 亿元")
    lines.append(f"- 营业成本：{cost_yi} 亿元")
    lines.append(f"- 净利润：{np_yi} 亿元")
    lines.append(f"- 归母净利润：{pnp_yi} 亿元")
    lines.append(f"- 每股收益EPS：{eps}")
    lines.append(f"- 毛利率：{gm:.2%} ")
    lines.append(f"- 净利率：{nm:.2%} ")
    #lines.append("\n> 重要说明：只有财报数据可用，**没有提供股价、行情、新闻素材，禁止编造股价、市值、新闻等任何信息**。没有的数据直接说明缺少数据。")

    return "\n".join(lines)
def format_market_data(code: str) -> str:
    try:
        import akshare as ak
        df = ak.stock_zh_a_hist(symbol=code, period="daily", start_date="20260101", end_date="20261231", adjust="qfq")
        recent = df.tail(15)
        lines = ["【行情数据（最近15个交易日）】"]
        for _, row in recent.iterrows():
            lines.append(f"- {row['日期']}: 收盘 {row['收盘']} 涨跌幅 {row['涨跌幅']}%")
        return "\n".join(lines)
    except Exception as e:
        return "【行情数据】获取失败（网络/限流），无法分析行情。"


def format_news_data(code: str) -> str:
    try:
        import akshare as ak
        df = ak.stock_news_em(symbol=code)
        lines = ["【新闻数据（最近几条）】"]
        for _, row in df.head(5).iterrows():
            title = str(row['新闻标题'])[:50]
            lines.append(f"- [{row['发布时间']}] {title}")
        return "\n".join(lines)
    except Exception as e:
        return "【新闻数据】获取失败（网络/限流），无法分析新闻。"





def main():
    code = input("请输入股票代码(如600519)")
    question = input("请输入你的投研问题: ")

    profit_text = format_profit_data(code)
    market_text = format_market_data(code)
    news_text = format_news_data(code)
    prompt = (
        f"【财报数据】\n{profit_text}\n\n"
        f"{market_text}\n\n"
        f"{news_text}\n\n"
        f"【用户问题】\n{question}"
    )

    with SqliteStore.from_conn_string("memory.sqlite")as store:
        app = build_demo_graph(store=store)
        result = app.invoke({"messages":[HumanMessage(content=prompt)],"code":code},)

        print("\n === 最终对话 ===")
        for msg in result["messages"]:
                print(f"\n[{msg.type}] {msg.content}")

if __name__ == "__main__":
    main()