# InvestAgent 阶段 2 实施计划：真实数据 + 清洗归一化

> **目标**：把阶段 1 的 mock 数据换成 AKShare 真实财报数据，攻克"数据清洗归一化"这个真正的技术难点，让第一份报告里的指标来自真实财报。
>
> **架构**：新增 `tools/`（AKShare 采集 + 清洗）和 `vfs/`（目录管理）两个模块，`collect` 节点改用真实数据落盘。
>
> **技术栈**：Python 3.11、AKShare、LangChain tool、pytest。
>
> **Spec**：`docs/superpowers/specs/2026-08-31-investagent-design.md`（重点看第 5 节「数据清洗归一化」和第 4 节「数据采集 Agent 职责」）
>
> **工作方式（全局约束）**：辅助/指导式开发——本计划不提供完整实现代码，只给目标、概念、接口签名、验证方式，代码你写。

---

## 阶段 2 要交付什么

- AKShare 真实财报数据成功落盘 VFS（不再是 mock 路径）。
- 一个**清洗归一化模块**，解决字段名不稳定、单位不统一、缺失值三大问题。
- 一个**财务指标计算**模块，从清洗后数据算出营收增速、毛利率、净利率、ROE。
- L1 单元测试覆盖清洗和指标计算函数。

## 阶段 2 文件结构（在阶段 1 基础上新增）

```
src/invest_agent/
├── tools/
│   ├── __init__.py
│   ├── akshare_fetcher.py   # AKShare 采集（封装成 tool）
│   └── clean.py             # 清洗归一化（字段映射/单位/缺失）
├── vfs/
│   ├── __init__.py
│   └── filesystem.py        # 目录管理（workspace/reports/logs）
├── metrics.py               # 财务指标计算
├── state.py                 # （可能微调：metrics 字段类型更明确）
├── graph.py                 # （不变）
├── nodes/
│   ├── collect.py           # （改造：用真实数据）
│   └── analyze.py           # （改造：用真实指标）
└── main.py                  # （不变）
```

---

## 动手前的核心概念（阶段 2 的「为什么」）

1. **为什么要有 `tools/` 目录**：在 LLM Agent 架构里，"工具"是**模型可以调用的外部能力**（查数据、搜网页、算数）。数据采集就是把 AKShare 包成一个工具。这是 LangChain `@tool` 装饰器的用武之地。

2. **为什么清洗归一化是"真正的难点"**：AKShare 是社区维护的开源库，数据来自不同接口、不同券商，**字段名和单位在不同公司/不同接口间不统一**。如果你不处理，ROE、毛利率这些指标会算错 10000 倍。这是"AI 应用落地"里最真实、最不被教程重视的一环。

3. **为什么要有 VFS（虚拟文件系统）模块**：阶段 1 你发现 `report.py` 里硬编码了 `"reports"` 目录、还要手动 `makedirs`。VFS 就是把"目录在哪、文件怎么读写"这件事**集中到一个模块**，其他代码只调 VFS 接口，不关心底层路径。这也是 spec 第 3 节"原始财报落盘、不进上下文"的落地。

---

## 任务拆解

### 任务 1：安装 akshare + 探索真实数据（探针）

**学什么**：真实 API 的不可预测性——你必须在设计清洗逻辑**之前**先亲眼看到数据长什么样。

**做什么**：
1. 安装并声明依赖：`pip install akshare`，并把 `"akshare"` 加进 `pyproject.toml` 的 `dependencies`。
2. 写一个**探针脚本**（可以放 `scripts/probe_akshare.py`，也可以临时 `python -c`），调用这几个接口，把结果打印出来看：
   - `ak.stock_profit_sheet_by_report_em("600519")` —— 利润表
   - `ak.stock_balance_sheet_by_report_em("600519")` —— 资产负债表
   - `ak.stock_cash_flow_sheet_by_report_em("600519")` —— 现金流量表
   - `ak.stock_financial_analysis_indicator("600519")` —— 财务分析指标（可能直接有 ROE/毛利率）
3. 重点观察并**记录**（写进 `notebook.txt`）：
   - 每个接口返回的 DataFrame 的**列名**是什么？（中文？英文？）
   - **行**是什么？（每个报告期一行？还是每个科目一行？）
   - **单位**是什么？（元/万元/亿元？字段名里有没有标注？）
   - 有没有 **NaN 缺失值**？

**关键提醒**：AKShare 接口名和返回格式**可能和你预期不同，甚至接口名已经变了**。如果某个接口报错或不存在，用 `dir(ak)` 或 AKShare 官方文档搜替代接口。**这个"踩坑→查文档→换接口"的过程，本身就是阶段 2 的核心学习。**

**怎么验证**：探针脚本能跑通，打印出至少一个接口的真实 DataFrame，你搞清楚了它的行列结构。

**提交**：`git commit -m "chore: add akshare dependency and probe script"`

---

### 任务 2：VFS 模块

**学什么**：单一职责原则——目录管理只归 VFS 管，其他模块不碰路径字符串。

**做什么**：建 `vfs/filesystem.py`，提供这几个函数（先想清楚签名再写）：

| 函数 | 作用 | 签名示意 |
|------|------|---------|
| `ensure_dir(path)` | 目录不存在则创建 | `(path: str) -> None` |
| `save_json(data, path)` | 存 JSON（自动建目录） | `(data: dict, path: str) -> str`（返回路径） |
| `read_json(path)` | 读 JSON | `(path: str) -> dict` |
| `workspace_dir(code)` | 某股票的 workspace 路径 | `(code: str) -> str` |
| `reports_dir()` | 报告目录路径 | `() -> str` |

**关键点**：这些函数内部调用 `os.makedirs(..., exist_ok=True)`，**把阶段 1 里散落的目录管理收口到这里**。以后 `report.py`、`collect.py` 都不再自己 `makedirs`，而是调 VFS。

**怎么验证**：写个最小脚本，调用 `save_json` 存一个 dict，再 `read_json` 读回来，内容一致。

**提交**：`git commit -m "feat: add VFS module for file/dir management"`

---

### 任务 3：清洗归一化模块（核心）

**学什么**：这是阶段 2 的灵魂。基于任务 1 的探索结果，写三个"纯函数"来解决三大问题。

**做什么**：建 `tools/clean.py`，写这三个纯函数（**纯函数** = 不碰网络、不碰文件，只吃数据吐数据，因此最好测）：

1. **字段映射** `normalize_columns(df)`：把不稳定的字段名映射到标准名。
   - 用一个**字典映射表**，例如 `{"营业总收入": "revenue", "营业收入": "revenue", ...}`。
   - 具体映射表内容**取决于你任务 1 看到的真实列名**，我们一起定。

2. **单位归一化** `normalize_units(value, unit)`：把元/万元/亿元统一成"元"。
   - 乘数：元 ×1，万元 ×1e4，亿元 ×1e8。
   - 难点：**如何判断一个数字的单位**？AKShare 有的在字段名里标注，有的不标。这是你要思考的核心。

3. **缺失值处理** `drop_or_mark_missing(df)`：明确"无数据"而非静默填 0。

**关键设计问题（先想清楚再写）**：
- 单位归一化，你怎么知道某列是"万元"还是"元"？是字段名里带了"（万元）"后缀，还是要靠数量级判断？
- 这决定了 `normalize_units` 的输入应该是什么。**别急着写，先想清楚数据从哪来、单位信息藏在哪。**

**怎么验证**：写几个简单的输入输出断言（这个正好是任务 7 的 L1 测试素材）。

**提交**：`git commit -m "feat: add data cleaning/normalization module"`

---

### 任务 4：封装 AKShare 采集 tool

**学什么**：LangChain 的 `@tool` 装饰器；"工具"的输入输出约定。

**做什么**：建 `tools/akshare_fetcher.py`，写一个采集函数：
- 输入：股票代码
- 内部：调 AKShare 三个报表接口 → 清洗（调 `clean.py`）→ 存 JSON（调 VFS）
- 输出：落盘的 JSON 文件路径（**不是数据本体**，呼应 spec 第 3 节）

**关键点**：这个函数是"数据采集 Agent 的工具"。阶段 2 你可以先写成一个普通函数（不用急着加 `@tool` 装饰器），跑通后再学 `@tool` 的用法——这是为了循序渐进。如果你状态好，也可以直接用 `@tool`。

**怎么验证**：调用 `fetch("600519")`，返回一个路径，且该路径下的 JSON 文件存在、内容是清洗后的财报。

**提交**：`git commit -m "feat: add AKShare fetch tool"`

---

### 任务 5：接入 collect 节点（替换 mock）

**学什么**：把工具接入图；节点从"返回假数据"变成"返回真实结果"。

**做什么**：改造 `nodes/collect.py`：
- 不再 `return {"raw_data_path": f"/workspace/{code}/raw.json"}` 这种假的。
- 改成调用 `akshare_fetcher.fetch(code)`，把返回的真实路径放进 state。

**怎么验证**：`python -m invest_agent.main 600519` 跑通，且 `raw_data_path` 指向一个**真实存在**的 JSON 文件。

**提交**：`git commit -m "feat: wire real AKShare data into collect node"`

---

### 任务 6：财务指标计算（analyze 真实化）

**学什么**：从原始财报算出衍生指标；"财务分析是纯计算，LLM 只做解读"的边界。

**做什么**：建 `metrics.py`，写纯函数计算：
- 营收增速（同比）：`(本期营收 - 上年同期营收) / 上年同期营收`
- 毛利率：`(营收 - 营业成本) / 营收`
- 净利率：`净利润 / 营收`
- ROE：`净利润 / 净资产`

改造 `nodes/analyze.py`：读真实财报（通过 VFS 读 JSON），调 `metrics.py` 算指标，写进 state。

**关键点**：这些公式需要你**从清洗后的数据里找到对应字段**（营收、营业成本、净利润、净资产）。这就是为什么任务 1 的探索和任务 3 的清洗是前提。

**怎么验证**：`python -m invest_agent.main 600519` 产出的报告里，财务指标是**真实数字**（不再是 mock 的 "15.2%"）。

**提交**：`git commit -m "feat: compute real financial metrics"`

---

### 任务 7：L1 单元测试

**学什么**：对"纯函数"写单元测试——这是最容易测、也最该测的代码。

**做什么**：建 `tests/test_clean.py` 和 `tests/test_metrics.py`：
- 测 `normalize_columns`：给一个带中文列名的 df，断言映射成标准名。
- 测 `normalize_units`：给 "万元" 的值 100，断言变成 1_000_000。
- 测指标计算：给一组已知营收/成本/净利润，断言算出正确的毛利率/净利率/ROE。

**怎么验证**：`pytest -v` 全绿（阶段 1 的 3 个测试 + 阶段 2 新增测试都过）。

**提交**：`git commit -m "test: add L1 unit tests for cleaning and metrics"`

---

## 阶段 2 完成标准

- [ ] `python -m invest_agent.main 600519` 产出的报告里，财务指标来自**真实 AKShare 财报**。
- [ ] 清洗模块解决了字段映射、单位归一化、缺失值三件事。
- [ ] VFS 模块收口了所有目录管理，`report.py`/`collect.py` 不再自己 `makedirs`。
- [ ] `pytest -v` 全绿，包含 L1 单元测试。
- [ ] 你能讲清：为什么清洗归一化是难点、VFS 解决什么问题、"数据落盘只传路径"的价值。

**完成后**：code review + 整理记忆，进入阶段 3（断点恢复）。

---

## 阶段 2 自检清单

- 覆盖 spec 第 4 节（数据采集 Agent）、第 5 节（清洗归一化）、第 3 节（VFS 雏形）。✓
- 无 placeholder、无完整答案代码（引导式）。✓
- 接口名前后一致：`fetch`、`normalize_columns`、`normalize_units`、`save_json`、`read_json`、`ensure_dir`。✓
- **诚实说明**：任务 3 的字段映射表、任务 6 的指标公式，具体内容依赖任务 1 的探索结果，届时一起定。✓
