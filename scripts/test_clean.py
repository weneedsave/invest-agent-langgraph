import pandas as pd
from invest_agent.tools.clean import clean_profit


df = pd.read_csv("scripts/profit_600519.csv")
result = clean_profit(df)
print(result)