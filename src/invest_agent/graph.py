from langgraph.graph import StateGraph, START, END
from invest_agent.state import InvestState
from invest_agent.nodes.collect import collect
from invest_agent.nodes.analyze import analyze
from invest_agent.nodes.compare import compare
from invest_agent.nodes.report import report_full,report_bank
from langgraph.types import RetryPolicy

#任务 4：组装 StateGraph
def route_report(state) ->str:
    if state ["metrics"]["gross_margin"] is None:
        return "bank"
    return "full"


def build_graph(checkpointer=None,interrupt_before = None,collect_fn=collect):
    g = StateGraph(InvestState)  #创建一张空白约束类型必须是我们定义的state

    #注册四个节点
    g.add_node("collect",collect_fn,retry_policy=RetryPolicy(max_attempts=3))
    g.add_node("analyze",analyze)
    g.add_node("compare",compare)
    g.add_node("report_full",report_full)
    g.add_node("report_bank",report_bank)



    #链接为线性


    g.add_edge(START,"collect")
    g.add_edge("collect","analyze")
    g.add_edge("analyze","compare")
    g.add_conditional_edges("compare",route_report,{"full":"report_full","bank":"report_bank"})
    g.add_edge("report_full",END)
    g.add_edge("report_bank",END)

    return g.compile(checkpointer = checkpointer,interrupt_before = interrupt_before)


