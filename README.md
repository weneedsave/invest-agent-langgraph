# InvestAgent — 基于 LangGraph 的多智能体投研助手

一个以「学会从零搭建多智能体系统」为主线的学习项目，载体是 A 股上市公司投研分析。边做边学 LangGraph 编排，覆盖从单节点流水线到 Supervisor 多智能体协作、工具调用、长期记忆、评测的完整进阶路径。

## 技术栈

| 类别 | 库 | 用途 |
|------|-----|------|
| 编排框架 | [LangGraph](https://github.com/langchain-ai/langgraph) | 状态图（StateGraph）、断点恢复、多智能体、长期记忆 |
| LLM 接入 | `langchain-openai` + DeepSeek V4 | 决策路由、专家分析、结构化输出、工具调用 |
| 数据源 | [AKShare](https://github.com/akfamily/akshare) | A 股财报、行情、新闻数据 |
| 持久化 | SQLite（`langgraph-checkpoint-sqlite` / `SqliteStore`） | checkpoint 快照 + 跨会话长期记忆 |
| 测试 | pytest | 单元测试、链路测试、评测回归 |
| 环境 | `python-dotenv` | API key 环境变量管理 |

## 学习主线（6 阶段）

1. **LangGraph 基础** — 线性流水线，State/Node/Edge/Graph/invoke 五大核心概念
2. **工具调用 + 数据清洗** — AKShare 财报采集、203 列通用模板清洗归一化、指标计算
3. **断点恢复** — SQLite checkpointer、thread_id、interrupt_before、续跑不重复采集
4. **多 Agent 协作** — 条件路由 + 重试（4a）；Supervisor 委派 + 消息（4b）
5. **长期记忆** — checkpointer（会话快照）vs store（跨会话记忆）、SqliteStore 持久化
6. **评测** — 黄金真值对拍、相对容差比对、财务指标提取准确率

## 架构（两种并存）

- **主流水线** `graph.py`：`collect → analyze → compare → 路由 → report_full/report_bank`（确定性编排，含重试）
- **Supervisor 多智能体** `demo_graph.py`：supervisor（LLM 决策路由）+ 三个专家 worker（财报/行情/新闻），MessagesState 共享对话

### 方案 A vs 方案 B（数据获取两种架构）

| | 方案 A | 方案 B |
|---|---|---|
| 数据获取 | 入口预取，塞进 prompt | LLM 自主调工具取数 |
| LLM 角色 | 被动读数据 | 主动决策 + 调工具 |
| 核心机制 | — | `@tool` + `bind_tools` + 工具循环 |

## 目录结构

```
src/invest_agent/
├── graph.py              # 主流水线（确定性）
├── demo_graph.py         # Supervisor 多智能体 demo
├── state.py              # 主流水线状态
├── metrics.py            # 毛利率/净利率等指标
├── memory.py             # 长期记忆封装（store 读写）
├── nodes/                # collect/analyze/compare/report 节点
├── tools/                # AKShare 采集、清洗、行情工具
├── agents/               # supervisor + workers + llm
└── eval/                 # 评测（golden 真值 + evaluate）
```

## 快速开始

```bash
# 1. 安装
python -m venv .venv
.venv/Scripts/activate        # Windows
pip install -e .

# 2. 配置 DeepSeek key
cp .env.example .env          # 填入 DEEPSEEK_API_KEY

# 3. 跑主流水线（财报分析）
python -m invest_agent.main 600519

# 4. 跑 Supervisor 多智能体 demo
python scripts/demo_supervisor.py

# 5. 评测
python -m invest_agent.eval.evaluate

# 6. 测试
python -m pytest -q
```

## 关键踩坑（详见 notebook）

- checkpointer 保存流程轨迹，store 保存业务记忆，二者用途不同
- `get_store()` 仅可在节点内部调用
- 工具失败返回字符串（非抛异常）会导致 LLM 反复重试死循环，需「不要重试」引导 + `max_loop` 兜底
- prompt 约束的松紧平衡：太松幻觉/越界，太紧该干不干
