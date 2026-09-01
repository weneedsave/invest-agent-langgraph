from importlib.resources import contents

from invest_agent.graph import build_graph


def test_graph_runs_end_to_end():
    app = build_graph()
    result = app.invoke({"code":"600519"})
    #1.报告路径有值(流程结束)
    assert result["report_path"] is not None

def test_state_fields_filled():
    app = build_graph()
    result = app.invoke({"code" : "000001"})
    #2.关键字节点全部填充完毕
    assert result["raw_data_path"] is not None
    assert result["metrics"] is not None
    assert result["peers"] is not None


def test_report_contains_code():
    app = build_graph()
    result = app.invoke({"code":"600519"})
    #3.报告内容包含股票代码
    with open(result["report_path"],"r",encoding="utf-8") as f:
        content = f.read()
    assert "600519" in content