from invest_agent.metrics import gross_margin, net_margin


def test_gross_margin_normal():
    assert abs(gross_margin(100, 40) - 0.6) < 1e-9  # (100-40)/100= 0.6


def test_gross_margin_zero_revenue():
    assert gross_margin(0, 40) is None  # 分母为0 →None


def test_net_margin_normal():
    assert abs(net_margin(30, 100) - 0.3) < 1e-9  # 30/100 = 0.3两个关键点


def test_gross_margin_zero_revenue():
    assert gross_margin(0, 40) is None  # 分母为0 →None


def test_net_margin_normal():
    assert abs(net_margin(30, 100) - 0.3) < 1e-9  # 30/100 =0.3