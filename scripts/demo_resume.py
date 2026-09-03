from langgraph.checkpoint.sqlite import SqliteSaver
from invest_agent.graph import build_graph

config = {"configurable": {"thread_id": "demo-600519"}}

with SqliteSaver.from_conn_string("checkpoints.sqlite") as cp:
    app = build_graph(checkpointer=cp, interrupt_before=["analyze"])

    print("=== 第一次 invoke：应在 analyze 前中断 ===")
    app.invoke({"code": "600519"}, config=config)
    snap = app.get_state(config)
    print("中断点，next =", snap.next)
    print("此时 metrics =", snap.values.get("metrics"))
    print("=== 第二次 invoke(None)：续跑，不应再打印 [collect] ===")
    result = app.invoke(None, config=config)
    print("报告路径:", result["report_path"])
