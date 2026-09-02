import pandas as pd
from invest_agent.tools.clean import clean_profit


def test_clean_profit_selects_and_renames():
      # 构造假数据：两行（两个报告期），列名是原始英文
      df = pd.DataFrame({
          "REPORT_DATE": ["2026-06-30", "2026-03-31"],
          "OPERATE_INCOME": [100.0, 80.0],
          "OPERATE_COST": [40.0, 30.0],
          "NETPROFIT": [30.0, 20.0],
          "PARENT_NETPROFIT": [28.0, 18.0],
          "BASIC_EPS": [2.0, 1.5],
          "无关列": [1, 2],   # 故意加一个不该被选中的列
      })
      result = clean_profit(df)
      # 断言：字段名是标准名，且取的是第一行（最新）
      assert result["revenue"] == 100.0
      assert result["report_date"] == "2026-06-30"
      assert "无关列" not in result