from invest_agent.agents.llm import get_llm
from langchain_core.messages import AIMessage,SystemMessage, ToolMessage   # 加 ToolMessage
from invest_agent.tools.market_tool import get_stock_hist

# 三个专家的角色提示词
FINANCIAL_PROMPT = """
你是财报分析师，只负责对提供的财务数据做解读，不要越界讨论行情、新闻舆情。
你的输入是财报相关字段数据。
只有当消息中完全没有营业收入、净利润等财报字段时，才回复【缺少财报原始数据，无法分析】。
如果提供了财报数据，即使仅仅只有单期数据，也必须基于现有数据开展分析；分析结尾需要主动标注说明：注：仅有单期数据，无法开展同比对比。
禁止编造任何输入中不存在的财务数字，所有判断严格依据给到的数据。
"""

MARKET_PROMPT = """
你是行情分析师专家，负责分析股价、行情、估值。
  你有一个工具 get_stock_hist
  可以获取股票的历史行情数据。
  规则：
  1. 当用户需要行情/股价/估值分析时，必须调用
  get_stock_hist
  工具获取数据，不要凭空编造行情数字。
  2. 拿到工具返回的数据后，基于真实数据分析（走势、
  涨跌幅、波动等）。
  3. 如果工具调用失败（返回失败信息），就如实说明"行
  情数据获取失败，无法分析"。
  4. 禁止越界讨论财务报表、新闻舆情。
"""

NEWS_PROMPT = """
你是新闻舆情分析师，只负责解读给到的新闻素材，不要越界分析财务指标、股价行情。
消息中提供的任何与公司相关的新闻标题、资金动向、行业动态，全部属于可分析素材。
只要存在任意一条相关新闻，就基于素材完成舆情解读，可以分析市场情绪、资金态度、潜在利好或者利空。
不要因为内容不是公司官方公告就拒绝分析。
只有消息内完全不存在任何新闻素材的时候，才回复【当前没有新闻素材，无法进行舆情分析】。
禁止编造新闻事件，全部结论严格依赖给出的新闻内容。

"""


def make_worker(system_prompt: str):
    llm = get_llm()          # worker专家不需要结构化输出，输出自然语言文本
    def worker(state) -> dict:
        messages = [SystemMessage(content=system_prompt)] + state["messages"]
        reply = llm.invoke(messages)          # 返回 AIMessage 对象
        return {"messages": [reply]}          # LangGraph增量更新：把新消息追加到state["messages"]
    return worker


financial_analyst = make_worker(FINANCIAL_PROMPT)
def market_analyst(state) -> dict:
    code = state["code"]
    llm = get_llm().bind_tools([get_stock_hist])
    sys_msg = SystemMessage(content=MARKET_PROMPT + f"\n\n当前要分析的股票代码：{code}")
    base = [sys_msg] + state["messages"]
    ai_msg = llm.invoke(base)
    conversation = [ai_msg]
    loop_cnt = 0
    max_loop = 3
    while ai_msg.tool_calls and loop_cnt < max_loop:
        tool_msgs = []
        for tc in ai_msg.tool_calls:
            result = get_stock_hist.invoke(tc)
            tool_msgs.append(ToolMessage(content=str(result), tool_call_id=tc["id"]))
        conversation.extend(tool_msgs)
        ai_msg = llm.invoke(base + conversation)
        conversation.append(ai_msg)
        loop_cnt += 1
    return {"messages": [ai_msg]}


news_analyst = make_worker(NEWS_PROMPT)