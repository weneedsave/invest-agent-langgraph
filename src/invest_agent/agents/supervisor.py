from typing import Literal, TypedDict
from invest_agent.agents.llm import get_llm
from langchain_core.messages import SystemMessage


class RouterResponse(TypedDict):
    next: Literal["财报分析师","行情分析师","新闻舆情师","FINISH"]

SYSTEM_PROMPT="""
你是多智能体的总调度 Supervisor，负责根据用户原始查询，选择下一个要执行的专家智能体。
只能从下面列表选择，输出严格遵守结构化格式，next字段仅允许取值：["财报分析师", "行情分析师", "新闻舆情师", "FINISH"]

决策规则：
1. 如果用户需要财务报表、盈利能力、毛利率、净利润、资产负债、财报解读 → next = "财报分析师"
2. 如果用户需要股价走势、K线、历史行情、估值、涨跌幅分析 → next = "行情分析师"
3. 如果用户需要公司新闻、公告、舆论、事件影响 → next = "新闻舆情师"
4. 当已经收集足够信息，所有必要专家已经完成分析，可以回复用户，任务结束 → next = "FINISH"

注意：
- 不要编造信息，不要自己回答业务问题，只做路由决策。
- 参考state中messages历史，判断哪些专家已经执行过，避免重复调用同一个agent。
- 只输出结构化JSON，不要额外解释、不要自然语言闲聊。
    """

def supervisor(state) -> RouterResponse:

    llm = get_llm().with_structured_output(RouterResponse,method="function_calling")

    messages = [SystemMessage(content=SYSTEM_PROMPT)]+state["messages"]
    response = llm.invoke(messages)
    return {"next": response["next"]}