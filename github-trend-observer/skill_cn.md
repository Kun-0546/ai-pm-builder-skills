---
name: GitHub Radar
description: >
  AI PM 视角的 GitHub Intelligence Tool。
  不只展示数据，产出 PM 级别的 paradigm insight。
  底层调用本机已登录的 gh CLI + GitHub API。
version: 0.1.1
author: Kun
tags: [github, intelligence, pm-insight, trending, ecosystem-analysis]
categories: [research, developer-tools, product-intelligence]
tools:
  - name: gh
    version: ">=2.40.0"
    type: cli
    required: true
    install_url: https://cli.github.com
    auth_required: true
    check: "gh auth status"
  - name: python
    version: ">=3.9"
    type: runtime
    required: true
    check: "python --version"
    packages: []  # 仅用标准库，无需 pip 安装
---

# GitHub Radar

AI PM 的开源情报引擎。五种模式，一套 Layer 分析框架。

## 语言选择

本 Skill 同时提供中文和英文版本。Agent 应**自动匹配用户的语言**：

- 用户使用**英文** → 读 `skill.md`、`agents/analyzer.md`、`references/layer_model.md`、`templates/*.html`，生成英文报告
- 用户使用**中文** → 读 `skill_cn.md`、`agents/analyzer_cn.md`、`references/layer_model_cn.md`、`templates/*_cn.html`，生成中文报告
- 脚本（`scripts/`）和配置（`config/`）为语言无关，两个版本共用

## 何时使用

- 「今天有什么值得看的」/ `--pulse` → Mode 1
- 「帮我找 [方向] 相关的 GitHub 项目」→ Mode 2
- 「监控异常信号」/ `--watch` → Mode 3
- 「分析 [repo] 的关联生态」→ Mode 4
- 「帮我梳理 [主题] 的演化脉络」/ `--evolve` → Mode 5
- 任何涉及 GitHub 项目发现、趋势分析、范式判断的需求

## 文件结构

```
github-trend-observer/
├── skill.md                     # Agent 执行指令（英文）
├── skill_cn.md                  # Agent 执行指令（中文）
├── ONBOARD.md                   # Agent 冷启动指引（英文）
├── ONBOARD_CN.md                # Agent 冷启动指引（中文）
├── requirements.txt             # 依赖声明
├── agents/
│   ├── analyzer.md              # PM 洞察分析 agent（英文）
│   └── analyzer_cn.md           # PM 洞察分析 agent（中文）
├── scripts/
│   ├── gh_utils.py              # 统一 gh CLI 工具函数
│   ├── check_rate_limit.py      # API 速率检查
│   ├── fetch_star_history.py    # star 增长数据拉取
│   ├── radar_pulse.py           # Mode 1 trending 拉取
│   ├── search_repos.py          # Mode 2 搜索
│   ├── watch_signals.py         # Mode 3 异常检测
│   ├── deep_link.py             # Mode 4 关联分析
│   ├── evolution_timeline.py    # Mode 5 主题演化数据采集
│   ├── generate_report.py       # HTML/MD 报告生成
│   └── test_oss.py              # 自动化测试（6 层 48 测试）
├── config/
│   ├── seed_list.json           # 关键开发者列表
│   └── domain_keywords.json     # 领域关键词映射
├── templates/
│   ├── radar-pulse.html         # Mode 1 报告模板（含 _cn 中文变体）
│   ├── direction-search.html    # Mode 2 报告模板
│   ├── signal-watch.html        # Mode 3 报告模板
│   ├── deep-link.html           # Mode 4 报告模板
│   └── evolution-timeline.html  # Mode 5 报告模板（D3.js 交互时间线）
├── evals/
│   ├── evals.json               # 测试用例（英文）
│   └── evals_cn.json            # 测试用例（中文）
└── references/
    ├── layer_model.md           # Layer 分类标准（英文）
    └── layer_model_cn.md        # Layer 分类标准（中文）
```

## 依赖

| 依赖 | 要求 | 检查命令 |
|------|------|----------|
| gh CLI | >= 2.40.0，已登录 | `gh auth status` |
| Python | >= 3.9 | `python --version` |
| 额外 Python 包 | 无，仅用标准库 | — |
| API 额度 | 认证状态 5000 次/小时 | `python scripts/check_rate_limit.py` |

## 通用前置步骤

**每种模式执行前都必须先做：**

```bash
# 1. 检查 API 额度
python scripts/check_rate_limit.py
```

根据返回的 `mode` 字段决定运行策略：
- `full` → 正常执行，含 star 历史拉取
- `degraded` → 跳过 fetch_star_history.py，只用基础数据
- `minimal` → 只执行搜索脚本，不调详情 API

---

## Mode 1: 主动探索 (Radar Pulse)

**触发**：`--pulse` 或「今天有什么值得看的」

### 执行步骤

```bash
# Step 1: 检查额度
python scripts/check_rate_limit.py

# Step 2: 拉取候选
python scripts/radar_pulse.py --days 7

# Step 3: 读取 agents/analyzer.md + references/layer_model.md
#         Layer 分类 → 过滤 L1/L5 → 选 1-2 个最有 PM 价值的

# Step 4: 对精选项目拉取 star 历史（full 模式下）
python scripts/fetch_star_history.py owner/repo
```

### 过滤规则

1. 标注每个候选的 Layer
2. 移除 L1（模型本体，太底层）和 L5（wrapper/demo，噪声）
3. PM 价值加权：L2 × 1.5, L3 × 1.3, L4 × 1.0
4. 取 Top 3-5，精选 1-2 个展开

### 输出格式

```markdown
# Radar Pulse — {日期}
> L2/L3/L4 精选 | 从 {n} 个候选筛出 {m} 个 | API: {remaining}/{limit}

## 今日精选
### {repo} [L?]
> {description}
| Stars | 30d 增长 | 语言 | 创建 |
|-------|----------|------|------|
**为什么选它**：{理由}
**范式信号**：{stack 哪里在动}
**建议**：Mode 4 深挖 / 持续观察

## 其他值得一看
| Repo | Layer | Stars | 一句话 |
|------|-------|-------|--------|

## 过滤掉的
- L1: {n} 个（{代表}）
- L5: {n} 个（{代表}）
```

报告保存至：`output/radar-pulse_{date}.md`

---

## Mode 2: 重点方向搜索 (Direction Search)

**触发**：用户给出技术方向或关键词

### 执行步骤

#### Step 1: 检查额度
```bash
python scripts/check_rate_limit.py
```

#### Step 2: 关键词扩展 + Layer 1 相关性审查

1. **理解主题**：用一句话说清用户搜索的核心概念
2. **扩展关键词**：围绕主题生成 8-15 个搜索关键词，覆盖：
   - 同义表达（swarm → fleet, colony）
   - 场景限定（swarm observability, coding agent swarm）
   - 相邻概念（swarm 旁边的 coordination, monitoring）
3. **Layer 1 自审**：逐个审查，判断标准是**「搜出来的项目是否大部分在讲同一类事」**，不要求完全匹配每个词：
   - **保留**：搜出来的项目和主题是同一个话题的不同角度
   - **删除**：搜出来的项目大部分是更大的范畴，主题只是其中一小部分
   - 示例 — 主题「agent swarm」：`swarm orchestration` 保留（同话题）、`multi-agent framework` 删除（swarm 只是 multi-agent 的子集，搜出来大部分不是 swarm）
   - 示例 — 主题「Agent 和人协作」：`human-in-the-loop agent` 保留（同话题）、`AI assistant` 删除（助手 ≠ 人机协作）
4. **呈现给用户确认**：列出保留 + 删除的关键词及理由，用户确认后再搜

#### Step 3: 搜索
```bash
python scripts/search_repos.py "{主关键词}" \
  --also "{关键词2}" "{关键词3}" ... \
  --expand "{备用1}" "{备用2}" ... \
  --min-stars 20 --min-recall 50
```

#### Step 3.5: 召回不足时的动态策略

如果去重结果 < 50 个，**不要默默扩展**，而是向用户呈现当前情况并提供三个选项：

> 搜索了 {n} 个关键词，去重后只有 {m} 个结果。可能的原因和选项：
>
> **A. 该方向尚未形成独立品类** — 相关能力可能嵌在更大的框架里作为 feature 存在，而非独立项目。建议放弃搜索，这本身就是一个有价值的发现。
>
> **B. 关键词覆盖不够** — 当前关键词可能遗漏了社区常用的表达方式。我建议追加以下关键词：{列出}。确认后继续搜。
>
> **C. 用现有结果分析** — {m} 个结果虽然少，但如果质量足够，可以直接进入分析。适合快速了解方向概况。

判断倾向的依据：
- 大部分关键词返回 0 → 倾向 A（品类不存在）
- 只有主关键词有结果，扩展词无结果 → 倾向 B（表达方式没覆盖到）
- 结果少但高度相关 → 倾向 C（小品类但信号清晰）

#### Step 4: Layer 2 结果相关性分类

搜索返回原始结果后，**在分析前**对每个 repo 做相关性判断：

| 分类 | 标准 | 处理 |
|------|------|------|
| **high** | 这个项目就是在做这个主题的事 | 进入竞争格局分析 |
| **medium** | 和主题相关，但不是它的主要方向 | 视质量决定是否纳入 |
| **low** | 碰巧关键词匹配，实际在做另一件事 | 过滤掉，列入"过滤掉的项目" |

判断依据：repo 的名字 + 描述，问自己「这个项目的作者会认为自己在做{用户主题}吗？」

#### Step 5: Star 历史 + PM 分析

```bash
# 对 high/medium 中的重点项目拉取 star 增长（full 模式下）
python scripts/fetch_star_history.py owner/repo

# 读取 agents/analyzer.md 和 references/layer_model.md
# 对数据做 Layer 分类 + PM 洞察
```

### 输出结构

```
headline（一句范式级判断）
→ 值得关注（3-5 个深度分析卡片）
→ 竞争格局（按子类分表，数量取决于实际相关项目数）
→ 范式判断（蓝色边框段落）
→ 建议深挖（3-5 个，指向其他 Mode）
→ 过滤掉的（折叠，分组说明原因）
```

报告同时生成 HTML 和 MD：`output/search_{keyword}_{date}.html/.md`

---

## Mode 3: 异常信号监控 (Signal Watch)

**触发**：`--watch` 或「监控异常信号」

> **已知盲区**：当前只能检测**新项目**（90 天内创建）的增长异常。老项目突然爆发需要持久化存储做差值比较，留作后续迭代。

### 执行步骤

#### Step 1: 检查额度
```bash
python scripts/check_rate_limit.py
```

#### Step 2: 候选发现
```bash
python scripts/watch_signals.py
# 全局扫描（默认），三窗口: 7d/30d/90d
# 领域扫描: python scripts/watch_signals.py --domain ai-agent
# domain 可选: ai-agent, llm-tools, ai-infra, mcp, all(默认)
```

脚本返回候选列表（按粗速度降序），每个候选包含：
- `stars`, `forks`, `created`, `age_days`
- `rough_velocity` = stars / age_days（粗速度）
- `fork_ratio` = forks / stars（使用深度信号）

#### Step 3: 初筛 + 拉取增长曲线

1. **排除明显不相关的**：看 description，排除游戏、教程、awesome-list 等非技术项目
2. **对剩余候选拉取 star history**（full 模式下）：
```bash
python scripts/fetch_star_history.py owner/repo
```

返回的增长指标：
| 指标 | 含义 |
|------|------|
| `avg_daily_7d` / `avg_daily_30d` | 日均增长 |
| `acceleration` | 7d 日均 / 30d 日均，>1 加速中 |
| `trend_direction` | 最近 3 天均值 / 前 4 天均值，看当前趋势 |
| `consecutive_growth_days` | 连续增长天数 |
| `peak_recency` | 峰值距今天数，0=今天 |
| `burst_ratio` | 峰值日 / 7d 日均，高=spike 型 |
| `recent_7_days[]` | 每日明细，用于判断增长形态 |

#### Step 4: 增长形态判断

看 `recent_7_days[]` 的形状，判断增长属于哪种类型：

| 形态 | 特征 | PM 含义 | 信号质量 |
|------|------|---------|---------|
| **sustained** | `consecutive > 7` + `burst_ratio < 3` | 有机增长，真实需求 | 高 |
| **accelerating** | `trend_direction > 2` + `consecutive > 5` | 正在爆发，要抓住 | 最高 |
| **spike+decay** | `burst_ratio > 5` + `trend_direction < 0.5` | launch 一波流，可能是噪声 | 低 |
| **step** | 单日暴涨 + 前后平稳 | 事件驱动（大 V 转发） | 中，看后续 |

#### Step 5: 三级判断 + PM 分析

读取 `agents/analyzer.md`，对每个候选综合判断：

- **值得深挖**：sustained/accelerating 形态 + L2/L3 层
- **观察**：有增长信号但形态不明，或 step 型等后续
- **忽略**：spike+decay + L5 wrapper / 教程 / fork_ratio < 0.02

### 输出结构

```
headline（一句话总结本期最重要的信号）
→ 信号总览（表格：repo / stars / 粗速度 / 形态 / 判断）
→ 值得深挖（3-5 个深度卡片，含增长曲线数据和 PM 洞察）
→ 观察列表（表格，简要说明原因）
→ 本期忽略（折叠，列出原因）
```

报告保存至：`output/signal-watch_{date}.html`

---

## Mode 4: 深度拆解 (Deep Link)

**触发**：用户给出 repo URL 或 owner/repo 名称

### 执行步骤

```bash
# Step 1: 检查额度
python scripts/check_rate_limit.py

# Step 2: 拉取完整数据
python scripts/deep_link.py langchain-ai/langgraph
# 支持 URL 输入: python scripts/deep_link.py https://github.com/langchain-ai/langgraph

# Step 3: 拉取 star 增长曲线（full 模式下）
python scripts/fetch_star_history.py langchain-ai/langgraph

# Step 4: 读取 agents/analyzer.md + references/layer_model.md
#         生成 ecosystem map + Layer 定位 + 范式判断
```

### 输出结构

```
headline（一句有张力的判断，点明核心矛盾或最重要的信号）
→ 基础画像（表格 + spark 趋势图 + commit 分布）
→ Layer 定位（badge + 判断依据 + "为什么不是 X"）
→ 采纳深度（fork 率 / watcher 率 / issue 活跃度 — 区分"围观"和"真用"）
→ Contributor 结构（表格 + PM 解读：bus factor / 团队 vs 独立 / 企业 vs 社区）
→ Release 节奏（timeline 组件 + 产品策略解读，不只是"发了几版"）
→ Issue 构成（表格 + PM 解读。如果分类失效（>50% 未分类），
   必须手动抽样 recent_titles 做定性分析作为 fallback，不能留空白）
→ 核心创新（ASCII 对比图：传统方式 vs 这个项目的方式。
   这是 PM 理解项目价值的最快路径，每份报告必须有。）
→ Ecosystem Map（ASCII 图 + PM 解读）
→ 竞品候选（折叠 details，标注"是否直接竞品"过滤噪声）
→ 范式判断（蓝色段落，结构：
   1. 一句话范式论断
   2. 旧方式 vs 新方式的核心差异
   3. 谁可能受威胁
   4. 谁不受威胁
   注意：不加"与你的关联"，保护隐私）
→ PM 总结（summary-table：成熟度 / 可信度 / 增长性质 / PM 价值 / 风险 / 建议）
```

### 输出风格

- CSS 使用 `--bg/--surface/--border/--accent/--muted` 变量体系，与其他 mode 一致
- PM 洞察用 `.pm-box` 卡片组件（白底 + border），不用内联 `<p>`
- Layer 定位用 `.layer-box` 组件，含 badge + 原因列表 + "为什么不是 X"
- 范式判断用 `.paradigm` 组件（蓝底 + border）
- 竞品候选放 `<details>` 折叠
- 所有技术指标附白话解释（说人话原则）

报告保存至：`output/deep-link_{owner}_{repo}_{date}.html`

---

## Mode 5: 单主题演化时间线 (Topic Evolution Timeline)

**触发**：`--evolve` 或用户给出一个技术主题，希望看到该领域开源项目的完整演化图景

### 核心理念

Mode 5 不只是搜索+列表。它站在技术演化史的脉络上，用未来学框架定位当前所处阶段，从发展路径推导分类体系，再用迭代搜索填充项目。分类来自**技术演化逻辑**，不是搜索关键词。

### 理论基础

| 框架 | 作者 | 核心思想 | 在 Mode 5 中的作用 |
|------|------|---------|-------------------|
| 技术革命周期 | Carlota Perez | Irruption→Frenzy→Synergy→Maturity（50-60年） | 定位主题所处阶段，决定分类粒度 |
| 演化轴 | Simon Wardley | Genesis→Custom→Product→Commodity | 每个分类标注成熟度等级 |
| 组合进化 | W. Brian Arthur | 技术=已有技术的组合；技术域=解题"语言" | 分类本质是识别"技术域" |
| 技术体趋势 | Kevin Kelly | 技术有内在趋势：复杂化、专业化、共生化 | 推测必然出现的萌芽分类 |
| TRL | NASA | 9级技术成熟度 | 辅助标注域成熟度 |

### 执行步骤

#### Phase 1: 定义边界（Scope Boundary）

**目标**：生成可判定的 IN/OUT 标准

1. **核心定义**：一句话说清主题本质
2. **必要条件**：项目必须满足什么才算 IN？（2-3 条 AND）
3. **排除条件**：满足什么直接 OUT？（2-3 条 OR）

**⛩ 门控：呈现给用户确认后才继续**

#### Phase 2-A: 技术演化定位（宏观定位）

用未来学框架回答三个问题：

1. **Perez 阶段**：这个技术主题处于 Irruption / Frenzy / Synergy / Maturity 的哪个阶段？
2. **核心建块**（Brian Arthur）：这个主题依赖哪些已有技术作为"原材料"？各建块处于 Wardley 哪个阶段？
3. **Kelly 趋势推演**：技术的内在趋势指向哪里？
   - 复杂化方向：简单→复合→系统
   - 专业化方向：通用→垂直→细分
   - 共生化方向：独立→协作→共生
   - 自指化方向：执行→优化执行→优化"优化过程"

#### Phase 2-B: 技术域识别（推导分类）

**方法一：演化树推导**（自顶向下）

画出从最早原型到当前前沿的技术分化树，每个分支 = 一个候选分类。

**方法二：项目聚类**（自底向上）

随机抽样 20-30 个项目，用 3-5 词描述各自解决的子问题，合并相似描述。

**方法三：演化推测域（≥ 3 个，强制要求）**

从 Kelly 趋势 + Arthur 组合逻辑推导出当前几乎没有项目、但技术路径上必然会出现的分类。每个推测域必须包含：

| 字段 | 说明 |
|------|------|
| 推测逻辑 | 为什么它必然出现？哪些建块已就位？ |
| 信号特征 | 如果正在萌芽，应该看到什么关键词/论文模式/项目特征？ |
| 搜索指令 | P2-C 信号猎捕时用的关键词 |

**合并三个方法的结果**，目标 5-12 个分类。

#### Phase 2-C: 信号猎捕（主动搜索推测域）

对每个推测域，用信号特征中的关键词在 GitHub / arXiv 搜索：

```
找到 ≥ 3 个项目 → 升级为 Emerging（确认萌芽）
找到 1-2 个     → 保留为 Speculative（纯推测），标注已有信号
找到 0 个       → 保留为 Speculative，下一轮迭代再搜
```

#### Phase 2-D: MECE 检验 + 确认

- **Mutually Exclusive**：任取两类，能否找到同时完美属于两类的项目？能 → 调整边界
- **Collectively Exhaustive**：是否每个项目都能归入某类？不能 → 增加类或调整定义
- **异常检测**：某类 < 3 个项目且非推测类 → 考虑合并；某类 > 总数 30% → 考虑拆分

**⛩ 门控：呈现分类列表 + 演化树 + Wardley 标注给用户确认**

#### Phase 3: 判定卡片

每个分类写一张判定卡片：

```
类名: [中文] [English]
一句话定义: ...
Wardley 阶段: Genesis / Custom / Product / Commodity
状态: Established / Emerging / Speculative
典型特征（满足 2/3 即归入）:
  - 特征 A
  - 特征 B
  - 特征 C
典型项目（锚点）: [2-3 个毫无争议的代表]
容易混淆的类: [列出] → 区分标准: [怎么判断归这边不归那边]
推测逻辑（仅推测域）: 为什么必然出现
```

**判定卡片嵌入 HTML 报告顶部**，作为可折叠面板，便于后续 check。

#### Phase 4: 迭代搜索 + 全量分类（分层策略）

每轮执行步骤：

1. **搜索 Round N**（复用 Mode 2 search_repos.py）
2. **Scope Filter**（P1 规则过滤）
3. **逐项分类**（P3 判定卡片）
4. **冲突检测**：匹配 2 类 → 看哪个匹配更多特征
5. **推测域信号扫描**：已分类项目中是否有子功能涉及推测域？
6. **抽样校验**：每类随机 2 个，人工确认
7. **进度报告**：输出 "Round N 新增 X 个 (Y%)，累计 Z 个，覆盖 M 条泳道"

**搜索轮次控制（执行约束）：**

```
Round 1-2: 必须执行（下限）
  └─ Round 2 结束后进入「检查点」

检查点（Round 2 结束后）:
  ├─ 累计 < 50 个项目   → 强制继续 Round 3（覆盖不足）
  ├─ 累计 50-99 个      → 继续 Round 3，除非 Round 2 新增 < 10%
  └─ 累计 ≥ 100 个      → 暂停，向用户报告并询问：
       "已收集 N 个项目，覆盖 M 条泳道。
        继续饱和搜索预计还需 1-2 轮，
        可能发现新的子领域或遗漏赛道。是否继续？"
       用户选择：
         ✓ 继续       → 执行饱和搜索（直到新增 < 10%）
         ✗ 停止       → 进入 Phase 5 定向补充
         ✗ 指定方向   → 用户给关键词，定向搜索 1 轮

饱和搜索（若触发）:
  - 每轮结束输出进度报告
  - 新增 < 10% → 宣告饱和，进入 Phase 5
  - 最多 5 轮（防止无限循环）
```

#### Phase 5: 定向补充 + 域迭代

- P4 后某个 Emerging 域项目 < 3 → 触发定向搜索（用判定卡片信号特征）
- 新轮 > 20% 项目无法归类 → 触发 P2 迭代（增加/调整分类）
- 推测域状态流转：

```
Speculative → 搜到信号 → Emerging → 项目 ≥ 5 → Established
           → 多轮搜不到 → 标注"当前无信号"，保留观察
```

### 可视化输出

D3.js 交互时间线，泳道布局：
- X 轴：项目创建时间
- Y 轴：分类泳道
- 圆圈大小：log(stars)
- 颜色：分类色
- 交互：hover 显示详情，click 跳转 GitHub
- 顶部面板：判定卡片（可折叠）
- 底部表格：全项目索引 + 一句话描述

### 未来学分析层（Phase 6）

在时间线和项目索引之上，叠加两个分析层：

#### 6-A: 演化全景（6 维度）

对分类完成后的全量数据做整体性分析（不按泳道逐条描述）：

| # | 维度 | 核心问题 | 方法 |
|---|------|---------|------|
| 1 | 阶段判断 | 这个领域处于技术生命周期的哪个位置？ | 从数据中标定阶段，各阶段可切换查看里程碑事件 |
| 2 | 驱动力 | 什么底层力量在推动整个领域？ | 找 2-3 个跨泳道的共同驱动力，每个配证据链 |
| 3 | 趋同轨迹 | 泳道之间正在发生什么？ | 识别泳道交叉点，推导交汇产生的新方向 |
| 4 | 必然与偶然 | 哪些趋势不可逆？哪些取决于事件？ | 两列对照，每条附推理依据 |
| 5 | 情景推演 | 12 个月后的可能图景？ | 2-3 个场景（乐观/基准/风险），附触发条件和概率 |
| 6 | 弱信号 | 什么被低估但可能改变格局？ | 从数据中找反常比例、缺失方向、概念收敛信号 |

**关键原则**：
- 分析对象是**整个领域**，不是逐个泳道
- 每个观点必须有数据支撑（项目名/数量/比例），不写空话
- 不堆砌学术人名（不写"Kevin Kelly 式""Carlota Perez 框架"），让分析本身说话

#### 6-B: 写给读者（三维后记）

报告最后一个 section，对报告自身做元分析。三个维度，每个维度回答一个核心问题：

| 维度 | 视角 | 核心问题 | 分析方法 |
|------|------|---------|---------|
| **来时路** | 回顾 | 什么模式在重复？这个模式预示什么？ | 从数据中识别波浪节奏（能力层→基建层→安全层？）。找催化链（哪个建块催生了哪个范式）。用模式预测下一个"应该到来但还没来"的层 |
| **未来观** | 终局 | 无论哪种未来，什么张力必须被解决？ | 回顾情景推演中的多个场景，提取**所有场景共有**的结构性张力（不是预测终点，是识别无法回避的问题）。张力 = 两个目标在结构上矛盾 |
| **看当下** | 行动 | 什么决策是有时间窗口的？ | 识别报告中最关键的不对称（从数据提取具体比例）。命名负空间（根据报告逻辑应该存在但不存在的方向）。声明报告的视野边界（数据来源能看到什么、看不到什么） |

**关键原则**：
- 三个维度的内容全部**从报告数据中推导**，不是泛泛的哲学感悟
- 每个维度底部附具体数据点（项目分布、比例、来源声明）
- 未来观不预设单一终局——用"张力"替代"预测"
- 看当下必须包含报告方法论的诚实声明（数据覆盖范围和偏差）

报告保存至：`output/evolution-timeline_{topic}_{date}.html`

---

## Seed List 自定义

编辑 `config/seed_list.json` 添加或移除关注的开发者：

```json
{
  "builders": [
    {"github": "username", "note": "为什么重要"}
  ],
  "last_updated": "2026-02-18"
}
```

当前默认包含 76 个 AI 领域重要 builder/org，覆盖 lab、agent-framework、coding-agent、inference、platform 等 17 个分类。
