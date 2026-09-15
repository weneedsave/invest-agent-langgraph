from langchain_core.tools import tool
import akshare as ak
import pandas as pd

from invest_agent.tools.akshare_fetcher import code_to_symbol

# ---------- 行情数据源的统一中间表示 ----------
# 所有 fetch_* 只返回这三列：
#   date    : datetime.date
#   close   : float
#   pct_chg : float，百分比数值（9.91 表示 +9.91%）
# 先把各家的方言列名统一，格式化逻辑（format_hist）才能被多个源复用。


def code_to_sina_symbol(code: str) -> str:
    """000980 -> sz000980；600519 -> sh600519

    新浪接口要【小写】交易所前缀，而 code_to_symbol 给的是大写。
    复用同一套映射规则再转小写，避免两处各写一份前缀判断。
    """
    return code_to_symbol(code).lower()


def fetch_from_em(code: str, days: int) -> pd.DataFrame:
    """东方财富源。注意它要裸代码，不带交易所前缀。"""
    df = ak.stock_zh_a_hist(symbol=code, period="daily", adjust="qfq")
    if df is None or df.empty:
        raise ValueError("东财返回空数据")
    out = df.tail(days).rename(
        columns={"日期": "date", "收盘": "close", "涨跌幅": "pct_chg"}
    )
    return out[["date", "close", "pct_chg"]]


def fetch_from_sina(code: str, days: int) -> pd.DataFrame:
    """新浪源。它没有涨跌幅列，得自己用收盘价算。"""
    df = ak.stock_zh_a_daily(symbol=code_to_sina_symbol(code), adjust="qfq")
    if df is None or df.empty:
        raise ValueError("新浪返回空数据")
    # pct_change() 算的是"相对前一行"的变化率，第一行没有前一行必然为 NaN。
    # 所以先多取一行，算完再截掉，保证返回的 days 行涨跌幅全部有效。
    recent = df.tail(days + 1).copy()
    recent["pct_chg"] = recent["close"].pct_change() * 100
    return recent.tail(days)[["date", "close", "pct_chg"]]


def format_hist(df: pd.DataFrame) -> str:
    """把中间表示拼成给 LLM 读的文本。多个源共用这一份。"""
    lines = []
    for _, row in df.iterrows():
        lines.append(f"{row['date']} 收盘{row['close']} 涨跌幅{row['pct_chg']:.2f}%")
    return "\n".join(lines)


@tool
def get_stock_hist(code: str, days: int = 15) -> str:
    """获取 A股最近若干交易日的行情（日期、收盘价、涨跌幅）。
    code: 股票代码（如 600519）
    days: 取最近多少个交易日（默认15）
    """
    # 多源降级链：东财优先（字段更全），东财不可用时自动切新浪。
    # 注意"空表"也是失败——akshare 取不到数据时不抛异常而是返回空 DataFrame，
    # 只 catch 异常会把空表当成功返回，报告就空得莫名其妙。
    for fetch in (fetch_from_em, fetch_from_sina):
        try:
            df = fetch(code, days)
            if df is None or df.empty:
                continue
            return format_hist(df)
        except Exception:
            continue
    return "【行情工具调用失败】网络异常或接口限流，无法获取K线行情。请直接向用户说明行情数据暂不可用，不要再调用工具重试。"
