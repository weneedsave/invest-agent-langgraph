from typing import Literal, TypedDict
from invest_agent.agents.llm import get_llm
from invest_agent.memory import recall, save_conclusion
from langchain_core.messages import SystemMessage, AIMessage


class RouterResponse(TypedDict):
    next: Literal["财报分析师", "行情分析师", "新闻舆情师", "FINISH"]


SYSTEM_PROMPT = """
你是投研任务总调度supervisor。
根据用户的投研问题，选择交给对应的专家执行：
- 财报分析师：负责财务指标、利润表、毛利率净利率分析
- 行情分析师：负责股价、走势相关分析
- 新闻舆情师：负责行业新闻、公告舆情分析

规则：
1. 一次只选择一个agent执行；
2. 专家输出完成后再次回到你这里；
3. 所有必要分析全部完成之后输出 FINISH；
4. 不编造没有提供的原始数据。
"""


def supervisor(state) -> dict:
    code = state["code"]

    # -------- ① 查记忆：是否已经分析过这只股票 --------
    past = recall(code)
    if past is not None:
        # 命中历史记忆，直接返回历史结论，走向结束
        return {
            "messages": [AIMessage(content=f"（引用历史分析，无需重新分析）\n{past}")],
            "next": "FINISH",
        }

    # -------- ② 没有历史记忆 → LLM做路由决策 --------
    llm = get_llm().with_structured_output(RouterResponse, method="function_calling")
    messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
    response = llm.invoke(messages)
    next_step = response["next"]

    # -------- ③ 如果决定FINISH，提取最后一条专家消息存入记忆 --------
    if next_step == "FINISH":
        ai_messages = [m for m in state["messages"] if isinstance(m, AIMessage)]
        if ai_messages:

            conclusion = ai_messages[-1].content

            save_conclusion(code, conclusion)

    return {"next": next_step}
