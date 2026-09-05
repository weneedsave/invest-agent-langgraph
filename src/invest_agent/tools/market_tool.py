from langchain_core.tools import tool
import akshare as ak
@tool
def get_stock_hist(code: str, days: int = 15) -> str:
    """获取 A股最近若干交易日的行情（日期、收盘价、涨跌幅）。
    code: 股票代码（如 600519）
    days: 取最近多少个交易日（默认15）
    """
    try:
        df = ak.stock_zh_a_hist(symbol=code, period="daily", adjust="qfq")
        recent = df.tail(days)
        lines = []
        for _, row in recent.iterrows():
            lines.append(f"{row['日期']} 收盘{row['收盘']} 涨跌幅{row['涨跌幅']}%")
        return "\n".join(lines)
    except Exception:
        return "【行情工具调用失败】网络异常或接口限流，无法获取K线行情。请直接向用户说明行情数据暂不可用，不要再调用工具重试。"