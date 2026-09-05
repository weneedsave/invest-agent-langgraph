from invest_agent.eval.evaluate import evaluate


def test_extraction_matches_golden():
    results = evaluate()
    # 所有字段必须 PASS
    failed = [r for r in results if not r["ok"]]
    assert failed == [], f"以下字段对拍失败: {failed}"