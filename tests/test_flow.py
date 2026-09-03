# test_flow.py
from langgraph.checkpoint.memory import InMemorySaver
from invest_agent.graph import build_graph


def test_graph_runs_end_to_end():
    app = build_graph(checkpointer=InMemorySaver())
    cfg = {"configurable": {"thread_id": "t1"}}
    result = app.invoke({"code":"600519"}, config=cfg)
    # 1.报告路径有值(流程结束)
    assert result["report_path"] is not None


def test_state_fields_filled():
    app = build_graph(checkpointer=InMemorySaver())
    cfg = {"configurable": {"thread_id": "t2"}}
    result = app.invoke({"code" : "000001"}, config=cfg)
    # 2.关键字节点全部填充完毕
    assert result["raw_data_path"] is not None
    assert result["metrics"] is not None
    assert result["peers"] is not None


def test_report_contains_code():
    app = build_graph(checkpointer=InMemorySaver())
    cfg = {"configurable": {"thread_id": "t3"}}
    result = app.invoke({"code":"600519"}, config=cfg)
    # 3.报告内容包含股票代码
    with open(result["report_path"],"r",encoding="utf-8") as f:
        content = f.read()
    assert "600519" in content


# ----------新增：断点中断+续跑回归测试----------
def test_interrupt_before_analyze_then_resume():
    app = build_graph(
        checkpointer=InMemorySaver(),
        interrupt_before=["analyze"],
    )
    config = {"configurable": {"thread_id": "test-resume"}}

    # 第一次：应停在 analyze 前
    app.invoke({"code": "600519"}, config=config)
    snap = app.get_state(config)
    assert snap.next == ("analyze",)        # 断点生效

    assert snap.values.get("metrics") is None

    # 第二次：续跑完成
    result = app.invoke(None, config=config)
    assert result["report_path"] is not None
