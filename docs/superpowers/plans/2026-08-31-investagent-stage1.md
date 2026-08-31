# InvestAgent 阶段 1 实施计划：LangGraph 线性流水线

> **目标**：搭好项目骨架，用 LangGraph 的 StateGraph 跑通「输入股票代码 → 4 个 stub Agent 依次执行 → 输出 Markdown 报告」的线性流程，数据先用 mock。
>
> **架构**：一个 `StateGraph` 串起 4 个节点（采集→分析→对比→撰写），State 用 TypedDict 定义，通过 `invoke()` 触发。
>
> **技术栈**：Python 3.11、LangGraph、LangChain（工具调用后续用）、pytest。
>
> **Spec**：`docs/superpowers/specs/2026-08-31-investagent-design.md`
>
> **工作方式（全局约束）**：辅助/指导式开发——本计划**不提供完整实现代码**，只给目标、概念、接口签名和验证方式。代码由你动手写，助手答疑纠错。每个任务先理解「为什么」，再动手。

---

## 阶段 1 要交付什么

- 项目骨架：目录 + venv + requirements + git。
- 一个 `State` schema，定义贯穿整个流程的状态字段。
- 一个 `StateGraph`，4 个节点（采集/分析/对比/撰写）用边串成线性。
- 4 个节点先用 mock 数据占位，产出第一份 Markdown 报告。
- 一个 L2 流程测试，验证图能跑通、状态正确流转。

## 阶段 1 文件结构

```
E:\Ai\agent\invest_agent\
├── requirements.txt
├── .gitignore
├── src/
│   └── invest_agent/
│       ├── __init__.py
│       ├── state.py          # State schema（TypedDict）
│       ├── graph.py          # StateGraph 组装 + compile
│       ├── nodes/
│       │   ├── __init__.py
│       │   ├── collect.py    # 数据采集节点（mock）
│       │   ├── analyze.py    # 财务分析节点（mock）
│       │   ├── compare.py    # 同业对比节点（mock）
│       │   └── report.py     # 报告撰写节点（写 Markdown 文件）
│       └── main.py           # CLI 入口：python -m invest_agent.main 600519
└── tests/
    └── test_flow.py          # L2 流程测试
```

---

## 动手前的核心概念（阶段 1 的「为什么」）

LangGraph 把一个工作流建模成**图**。你只需要理解 5 个东西：

1. **State**：贯穿所有节点的共享状态，是一个带类型注解的 dict（`TypedDict`）。每个节点读它、返回部分更新，LangGraph 自动合并。
2. **Node**：一个普通 Python 函数，签名是 `def node(state: State) -> dict:`，返回的要更新的字段（不需要返回整个 State）。
3. **Edge**：节点之间的连线，决定执行顺序。
4. **Graph**：`StateGraph(StateSchema)` 把节点和边组装起来，`.compile()` 生成可执行的 app。
5. **Invoke**：`app.invoke(初始状态)` 跑一遍整个图。

**关键 API 提示**（去查 LangGraph 文档/源码确认当前版本用法）：
- `from langgraph.graph import StateGraph, START, END`
- `graph.add_node("name", func)`
- `graph.add_edge(START, "collect")` / `graph.add_edge("collect", "analyze")` / `graph.add_edge("report", END)`
- `app = graph.compile()`
- `result = app.invoke({"code": "600519"})`

---

## 任务拆解

### 任务 1：项目骨架 + 环境

**学什么**：Python 项目标准结构、venv 隔离、依赖管理。

**做什么**：
- 在 `E:\Ai\agent\invest_agent\` 下建目录结构（如上）。
- 建 `requirements.txt`，至少包含 `langgraph`、`langchain`、`pytest`（先不装 akshare/chroma，阶段 1 用不到，YAGNI）。
- 建 venv 并装依赖。
- `git init` + 写 `.gitignore`（忽略 `.venv/`、`__pycache__/`、`.pytest_cache/`、`workspace/`、`reports/`）。
- 建空的 `src/invest_agent/__init__.py` 和各 `__init__.py`。

**怎么验证**：
- `python --version` 是 3.11。
- `pip list` 能看到 `langgraph`。
- `git status` 正常。

**提交**：`git commit -m "chore: scaffold project structure"`

---

### 任务 2：定义 State schema

**学什么**：`TypedDict` 怎么定义一个带类型的状态；State 里该放什么、不该放什么（长数据放文件路径，不放本体——这是 spec 第 3 节的核心原则）。

**做什么**：在 `state.py` 里用 `TypedDict` 定义一个 `InvestState`，阶段 1 最少需要这些字段：

| 字段 | 类型 | 含义 |
|------|------|------|
| `code` | `str` | 股票代码（入口输入） |
| `raw_data_path` | `str` | 采集结果的落盘路径（阶段1是 mock 路径） |
| `metrics` | `dict` | 财务指标（阶段1 mock） |
| `peers` | `list[dict]` | 同业对比数据（阶段1 mock） |
| `report_path` | `str` | 最终报告路径 |

提示：`TypedDict` 里 `Optional[str]` 表示"运行中途还没值"的字段；`invoke` 时只需给 `code`，其余由节点填充。

**怎么验证**：写一个最小测试或在 `python -c` 里确认 `InvestState` 能实例化、字段类型注解正确。

**提交**：`git commit -m "feat: define InvestState schema"`

---

### 任务 3：4 个 stub 节点（mock 数据）

**学什么**：节点函数的标准写法（读 State、返回部分更新 dict）；为什么节点返回的是「更新」而不是「整个 State」（LangGraph 的合并语义）。

**做什么**：在 `nodes/` 下写 4 个节点函数，阶段 1 先 mock：

- `collect(state) -> dict`：不真调 AKShare，直接返回一个假的 `raw_data_path`（如 `"/workspace/600519/raw.json"`），并打印一行"采集完成"。
- `analyze(state) -> dict`：返回 mock 的 `metrics`（如 `{"revenue_growth": "15%", "gross_margin": "40%", ...}`），并打印"分析完成"。
- `compare(state) -> dict`：返回 mock 的 `peers` 列表。
- `report(state) -> dict`：读 State 里的 code/metrics/peers，拼成一段 Markdown 文本，写入 `reports/{code}.md`，返回 `report_path`。

**关键点（阶段 1 的重点学习）**：`report` 节点是唯一真正干活的节点——它演示了「节点读上游状态 → 生成产物 → 落盘 → 只返回路径」这个模式。这正是 spec 里 VFS 思想的雏形。

**怎么验证**：单独调用每个节点函数，看返回值是否符合 `dict` 类型、字段对不对。

**提交**：`git commit -m "feat: add 4 stub nodes with mock data"`

---

### 任务 4：组装 StateGraph

**学什么**：`StateGraph` 怎么把节点和边连起来；`START`/`END` 是什么；`compile()` 做什么。

**做什么**：在 `graph.py` 里写一个 `build_graph()` 函数：
- 用 `StateGraph(InvestState)` 建图。
- `add_node` 添加 4 个节点。
- `add_edge` 按「采集→分析→对比→撰写」串起来，首尾接 `START`/`END`。
- `compile()` 返回 app。

**怎么验证**：写一个最小脚本 `app = build_graph(); result = app.invoke({"code": "600519"})`，打印 result，确认 4 个节点按顺序执行、`report_path` 有值、报告文件真的生成了。

**提交**：`git commit -m "feat: assemble linear StateGraph"`

---

### 任务 5：CLI 入口

**学什么**：`python -m` 的包入口写法；让项目能被一行命令驱动。

**做什么**：在 `main.py` 写 `def main()`，从 `sys.argv` 读股票代码，调用 `build_graph()` 的 app，`invoke` 后打印报告路径和报告内容摘要。

**怎么验证**：`python -m invest_agent.main 600519` 能跑通，终端打印出采集→分析→对比→撰写的顺序日志，且 `reports/600519.md` 生成。

**提交**：`git commit -m "feat: add CLI entry point"`

---

### 任务 6：L2 流程测试

**学什么**：怎么测「图」这种有状态的东西（不是测单个函数，是测状态流转）；pytest 的基本断言。

**做什么**：在 `tests/test_flow.py` 写测试：

- `test_graph_runs_end_to_end()`：invoke 一个假代码，断言 `result["report_path"]` 存在、文件已生成。
- `test_state_fields_filled()`：断言 result 里 `metrics`、`peers`、`raw_data_path` 都有值（非 None）。
- `test_report_contains_code()`：断言报告内容里包含股票代码。

提示：测试里用 `tmp_path` fixture 来指定一个临时报告目录，避免污染真实 `reports/`（这需要你的 `report` 节点支持一个可配置的输出目录，如果任务 3 没做，这里补上）。

**怎么验证**：`pytest tests/test_flow.py -v` 全绿。

**提交**：`git commit -m "test: add L2 flow tests"`

---

## 阶段 1 完成标准

- [ ] `python -m invest_agent.main 600519` 一行命令跑通，产出 `reports/600519.md`。
- [ ] `pytest -v` 全绿。
- [ ] 你能不看笔记向别人讲清：State 是什么、Node 的返回约定、Edge 的作用、`compile`/`invoke` 各做什么。
- [ ] git 有 6 个语义清晰的提交。

**完成后**：我们做一次代码 review（讲清哪些写法好、哪些是坑），然后进入阶段 2（AKShare 真数据 + 清洗归一化），我会为阶段 2 另出计划。

---

## 阶段 1 自检清单（写计划时核对过）

- 覆盖 spec 第 9 节「阶段 1」的全部内容：State/Schema/Node/Edge、线性流水线、mock 出报告。✓
- 无 placeholder / 无完整答案代码（引导式，代码你写）。✓
- 接口名前后一致：`InvestState`、`build_graph()`、`collect/analyze/compare/report` 在任务间一致。✓
