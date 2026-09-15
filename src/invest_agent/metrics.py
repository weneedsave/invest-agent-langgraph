def gross_margin(revenue: float,operate_cost:float)-> float|None:
    #毛利率 = (营收 - 营业成本) / 营收
    if revenue is None or operate_cost is None or revenue == 0:
        return None
    return (revenue - operate_cost) / revenue

def net_margin(net_profit:float,revenue:float)-> float|None:
    #净利率 = 净利润 / 营收
    if net_profit is None or revenue is None or revenue == 0:
        return None
    return net_profit / revenue