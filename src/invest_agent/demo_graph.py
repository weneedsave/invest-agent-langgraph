from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import MessagesState
from invest_agent.agents.supervisor import supervisor
from invest_agent.agents.workers import (
    financial_analyst, market_analyst, news_analyst,
)


class DemoState(MessagesState):
    code: str
    next: str
    tried: list[str]      # 已派遣过的专家名，supervisor 用它防止重复派遣


def build_demo_graph(store = None):
    g = StateGraph(DemoState)

    # 注册节点：supervisor + 3 个专家
    g.add_node("supervisor", supervisor)
    g.add_node("财报分析师", financial_analyst)
    g.add_node("行情分析师", market_analyst)
    g.add_node("新闻舆情师", news_analyst)

    g.add_edge(START,"supervisor")
    g.add_conditional_edges(
        "supervisor",lambda state: state["next"],
        {
            "财报分析师": "财报分析师",
            "行情分析师": "行情分析师",
            "新闻舆情师": "新闻舆情师",
            "FINISH": END,
        },

    )

    g.add_edge("财报分析师", "supervisor")
    g.add_edge("行情分析师", "supervisor")
    g.add_edge("新闻舆情师", "supervisor")

    return g.compile(store = store)
