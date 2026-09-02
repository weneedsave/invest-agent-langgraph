from invest_agent.metrics import gross_margin, net_margin

revenue = 90703260964.48
operate_cost = 9473762565.88
net_profit = 46033330566.78

print("毛利率:", gross_margin(revenue, operate_cost))   # 期望 ≈0.8955
print("净利率:", net_margin(net_profit, revenue))        # 期望 ≈0.5075