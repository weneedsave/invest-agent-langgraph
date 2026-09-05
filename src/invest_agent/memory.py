from langgraph.config import get_store

# 命名空间：("analysis",)
# namespace 相当于文件夹/分类，用来隔离不同类型的数据
NAMESPACE = ("analysis",)


def save_conclusion(code: str, conclusion: str) -> None:
    """保存某只股票的分析结论到LangGraph内置Store"""
    # get_store()：拿到本次运行上下文中注入的全局Store实例
    store = get_store()
    # put(命名空间, key, value字典)
    # key：股票code，例如 "600519"
    # value：存字典，里面放conclusion分析结论
    store.put(NAMESPACE, code, {"conclusion": conclusion})


def recall(code: str) -> str | None:
    """根据股票代码读取历史保存的分析结论；没找到返回None"""
    store = get_store()
    # get(命名空间, key)
    item = store.get(NAMESPACE, code)
    if item is None:
        return None
    # item.value 就是我们put进去的字典 {"conclusion":"xxx"}
    return item.value.get("conclusion")
