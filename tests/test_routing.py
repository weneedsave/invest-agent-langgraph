from invest_agent.graph import route_report
from langgraph.checkpoint.memory import InMemorySaver
from invest_agent.graph import build_graph


def test_route_report_full_when_gross_margin_present():
    state = {"metrics": {"gross_margin": 0.5,
                         "net_margin": 0.2}}
    assert route_report(state) == "full"


def test_route_report_bank_when_gross_margin_none():
    state = {"metrics": {"gross_margin": None,
                         "net_margin": 0.2}}
    assert route_report(state) == "bank"



def test_collect_retries_then_succeeds():
    calls = {"n": 0}

    def flaky_collect(state):
        calls["n"] += 1
        if calls["n"] < 3:
            raise ConnectionError("网络抖动")
        return {"raw_data_path":"workspace/600519/profit.json"}

    app = build_graph(
          checkpointer=InMemorySaver(),
          collect_fn=flaky_collect,
    )
    result = app.invoke(
        {"code": "600519"},
        config={"configurable": {"thread_id":"retry-test"}},
    )
    assert calls["n"] == 3                 # 被调用了 3次（2 失败 + 1 成功）
    assert result["report_path"] is not None