import pandas as pd
from invest_agent.tools.clean import clean_profit
from invest_agent.metrics import gross_margin, net_margin
from invest_agent.eval.golden import GOLDEN_600519

def compute_actual(df) -> dict:
    """跑被测代码，得到实际结果
        读取 csv 得到的财报表格"""
    extracted = clean_profit(df)
    extracted["gross_margin"] = gross_margin(extracted["revenue"], extracted["operate_cost"])
    extracted["net_margin"] = net_margin(extracted["net_profit"], extracted["revenue"])
    return extracted

def close(actual, expected, rtol=1e-6) -> bool:
    """相对容差比对，浮点数不能直接用 == 判断
        - `actual`：float，我们代码算出来的值
        - `expected`：float，真值表里面手工算的标准答案
        - `rtol=1e‑6`：相对误差容忍度（允许百万分之一的误差）
    """
    return abs(actual - expected) <= rtol * abs(expected)

def evaluate() -> list[dict]:
    df = pd.read_csv("scripts/profit_600519.csv")
    actual = compute_actual(df)
    results = []
    for field, expected in GOLDEN_600519.items():
        a = actual[field]
        ok = close(a, expected)
        results.append({
            "field": field,
            "actual": a,
            "expected": expected,
            "ok": ok,
        })
    return results

def main():
    results = evaluate()
    passed = sum(1 for r in results if r["ok"])
    print(f"评测结果：{passed}/{len(results)} 项通过\n")
    for r in results:
        mark = "PASS" if r["ok"] else "FAIL"
        print(f"[{mark}] {r['field']}: 实际={r['actual']}, 期望={r['expected']}")

if __name__ == "__main__":
    main()
#1. `compute_actual(df)`：输入 df，输出清洗 + 计算完成的字典；复现业务代码拿到实际结果。
# 2. `close(actual, expected)`：输入两个浮点数，输出 bool；浮点数不能直接`==`，做误差比对。
# 3. `evaluate()`：无输入，内部读取 csv；输出评测结果列表；批量对比真值表。
# 4. `main()`：无输入，无返回；控制台打印评测报告，给人看