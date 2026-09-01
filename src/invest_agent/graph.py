from tokenize import endpats

from langgraph.graph import StateGraph, START, END
from invest_agent.state import InvestState
from invest_agent.nodes.collect import collect
from invest_agent.nodes.analyze import analyze
from invest_agent.nodes.compare import compare
from invest_agent.nodes.report import report
#任务 4：组装 StateGraph
def build_graph():
    g = StateGraph(InvestState)  #创建一张空白约束类型必须是我们定义的state

    #注册四个节点
    g.add_node("collect",collect)
    g.add_node("analyze",analyze)
    g.add_node("compare",compare)
    g.add_node("report",report)


    #链接为线性

    g.add_edge(START,"collect")
    g.add_edge("collect","analyze")
    g.add_edge("analyze","compare")
    g.add_edge("compare","report")
    g.add_edge("report",END)

    return g.compile()

