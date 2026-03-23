---
name: GitHub Radar
description: >
  A GitHub Intelligence Tool from an AI PM perspective.
  Goes beyond displaying data to deliver PM-grade paradigm insights.
  Powered by the locally authenticated gh CLI + GitHub API.
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
    packages: []  # stdlib only, no pip dependencies
---

# GitHub Radar

An open-source intelligence engine for AI PMs. Five modes, one Layer analysis framework.

## Language Selection

This skill ships with both English and Chinese versions. The agent should **automatically match the user's language**:

- If the user speaks **English** -> Use `skill.md`, `agents/analyzer.md`, `references/layer_model.md`, `templates/*.html`, and generate English reports
- If the user speaks **Chinese** -> Use `skill_cn.md`, `agents/analyzer_cn.md`, `references/layer_model_cn.md`, `templates/*_cn.html`, and generate Chinese reports
- Scripts (`scripts/`) and config (`config/`) are language-neutral and shared by both versions

## When to Use

- "What's worth looking at today?" / `--pulse` -> Mode 1
- "Find me GitHub projects related to [topic]" -> Mode 2
- "Monitor anomalous signals" / `--watch` -> Mode 3
- "Analyze the ecosystem around [repo]" -> Mode 4
- "Map the evolution of [topic]" / `--evolve` -> Mode 5
- Any need involving GitHub project discovery, trend analysis, or paradigm assessment

## File Structure

```
github-trend-observer/
├── skill.md                     # Agent execution instructions (English)
├── skill_cn.md                  # Agent execution instructions (Chinese)
├── ONBOARD.md                   # Agent cold-start instructions (English)
├── ONBOARD_CN.md                # Agent cold-start instructions (Chinese)
├── requirements.txt             # Dependency declaration
├── agents/
│   ├── analyzer.md              # PM insight analyzer agent (English)
│   └── analyzer_cn.md           # PM insight analyzer agent (Chinese)
├── scripts/
│   ├── gh_utils.py              # Unified gh CLI utility functions
│   ├── check_rate_limit.py      # API rate limit checker
│   ├── fetch_star_history.py    # Star growth data fetcher
│   ├── radar_pulse.py           # Mode 1 trending fetcher
│   ├── search_repos.py          # Mode 2 search
│   ├── watch_signals.py         # Mode 3 anomaly detection
│   ├── deep_link.py             # Mode 4 relationship analysis
│   ├── evolution_timeline.py    # Mode 5 topic evolution data collector
│   ├── generate_report.py       # HTML/MD report generation
│   └── test_oss.py              # Automated tests (6 tiers, 41 tests)
├── config/
│   ├── seed_list.json           # Key developer list
│   └── domain_keywords.json     # Domain keyword mappings
├── templates/
│   ├── radar-pulse.html         # Mode 1 report template (en/cn variants)
│   ├── direction-search.html    # Mode 2 report template
│   ├── signal-watch.html        # Mode 3 report template
│   ├── deep-link.html           # Mode 4 report template
│   └── evolution-timeline.html  # Mode 5 report template (D3.js interactive)
├── evals/
│   ├── evals.json               # Test cases (English)
│   └── evals_cn.json            # Test cases (Chinese)
└── references/
    ├── layer_model.md           # Layer classification standard (English)
    └── layer_model_cn.md        # Layer classification standard (Chinese)
```

## Dependencies

| Dependency | Requirement | Check Command |
|------------|-------------|---------------|
| gh CLI | >= 2.40.0, authenticated | `gh auth status` |
| Python | >= 3.9 | `python --version` |
| Extra Python packages | None, stdlib only | — |
| API quota | 5,000 requests/hour when authenticated | `python scripts/check_rate_limit.py` |

## Common Prerequisites

**Must be completed before running any mode:**

```bash
# 1. Check API quota
python scripts/check_rate_limit.py
```

Determine the execution strategy based on the returned `mode` field:
- `full` -> Normal execution, including star history fetching
- `degraded` -> Skip fetch_star_history.py, use basic data only
- `minimal` -> Run search scripts only, skip detail API calls

---

## Mode 1: Proactive Exploration (Radar Pulse)

**Trigger**: `--pulse` or "What's worth looking at today?"

### Execution Steps

```bash
# Step 1: Check quota
python scripts/check_rate_limit.py

# Step 2: Fetch candidates
python scripts/radar_pulse.py --days 7

# Step 3: Read agents/analyzer.md + references/layer_model.md
#         Layer classification -> Filter out L1/L5 -> Select 1-2 with highest PM value

# Step 4: Fetch star history for selected projects (full mode only)
python scripts/fetch_star_history.py owner/repo
```

### Filtering Rules

1. Label each candidate's Layer
2. Remove L1 (model-level, too low-level) and L5 (wrapper/demo, noise)
3. PM value weighting: L2 x 1.5, L3 x 1.3, L4 x 1.0
4. Take Top 3-5, deep-dive into 1-2

### Output Format

```markdown
# Radar Pulse — {date}
> L2/L3/L4 selection | Filtered {m} from {n} candidates | API: {remaining}/{limit}

## Today's Picks
### {repo} [L?]
> {description}
| Stars | 30d Growth | Language | Created |
|-------|------------|----------|---------|
**Why this one**: {rationale}
**Paradigm signal**: {where the stack is shifting}
**Recommendation**: Deep-dive via Mode 4 / Keep watching

## Also Worth a Look
| Repo | Layer | Stars | One-liner |
|------|-------|-------|-----------|

## Filtered Out
- L1: {n} projects ({examples})
- L5: {n} projects ({examples})
```

Report saved to: `output/radar-pulse_{date}.md`

---

## Mode 2: Direction Search

**Trigger**: User provides a technical direction or keywords

### Execution Steps

#### Step 1: Check Quota
```bash
python scripts/check_rate_limit.py
```

#### Step 2: Keyword Expansion + Layer 1 Relevance Review

1. **Understand the topic**: State the core concept of the user's search in one sentence
2. **Expand keywords**: Generate 8-15 search keywords around the topic, covering:
   - Synonymous expressions (swarm -> fleet, colony)
   - Scenario-specific terms (swarm observability, coding agent swarm)
   - Adjacent concepts (coordination, monitoring — things adjacent to swarm)
3. **Layer 1 self-review**: Review each keyword; the criterion is **"would most results returned be about the same category of thing?"** — exact match to every word is not required:
   - **Keep**: Results are different angles on the same topic
   - **Remove**: Most results fall into a broader category where the topic is only a small subset
   - Example — topic "agent swarm": `swarm orchestration` keep (same topic); `multi-agent framework` remove (swarm is a subset of multi-agent; most results won't be about swarms)
   - Example — topic "Agent-human collaboration": `human-in-the-loop agent` keep (same topic); `AI assistant` remove (assistant != human-agent collaboration)
4. **Present to user for confirmation**: List kept and removed keywords with rationale; proceed with search only after user confirms

#### Step 3: Search
```bash
python scripts/search_repos.py "{main keyword}" \
  --also "{keyword2}" "{keyword3}" ... \
  --expand "{fallback1}" "{fallback2}" ... \
  --min-stars 20 --min-recall 50
```

#### Step 3.5: Dynamic Strategy When Recall Is Low

If deduplicated results < 50, **do not silently expand**. Instead, present the current situation to the user with three options:

> Searched {n} keywords, only {m} unique results after deduplication. Possible reasons and options:
>
> **A. This direction hasn't formed a distinct category yet** — The relevant capabilities may be embedded as features within larger frameworks rather than existing as standalone projects. Recommend abandoning the search; this finding is itself valuable.
>
> **B. Keyword coverage is insufficient** — Current keywords may be missing expressions commonly used by the community. I suggest adding the following keywords: {list}. Will continue after confirmation.
>
> **C. Proceed with existing results** — Although {m} results is a small set, if quality is sufficient, we can go straight to analysis. Suitable for a quick overview of the landscape.

Heuristics for recommending an option:
- Most keywords return 0 results -> lean toward A (category doesn't exist)
- Only the main keyword has results, expanded terms return nothing -> lean toward B (missing community terminology)
- Few results but highly relevant -> lean toward C (small category with clear signal)

#### Step 4: Layer 2 Result Relevance Classification

After raw search results are returned and **before analysis**, classify each repo's relevance:

| Classification | Criteria | Handling |
|----------------|----------|----------|
| **high** | This project is directly working on the topic | Include in competitive landscape analysis |
| **medium** | Related to the topic, but not its primary focus | Include based on quality |
| **low** | Keyword match was coincidental; project is actually about something else | Filter out, list under "Filtered Out" |

Judgment basis: repo name + description. Ask yourself, "Would this project's author consider themselves working on {user's topic}?"

#### Step 5: Star History + PM Analysis

```bash
# Fetch star growth for key high/medium projects (full mode only)
python scripts/fetch_star_history.py owner/repo

# Read agents/analyzer.md and references/layer_model.md
# Perform Layer classification + PM insight analysis on the data
```

### Output Structure

```
headline (one paradigm-level judgment)
-> Worth Watching (3-5 deep analysis cards)
-> Competitive Landscape (grouped tables by subcategory; count depends on actual relevant projects)
-> Paradigm Assessment (blue-bordered section)
-> Suggested Deep Dives (3-5, pointing to other Modes)
-> Filtered Out (collapsed, grouped with reasons)
```

Reports generated in both HTML and MD: `output/search_{keyword}_{date}.html/.md`

---

## Mode 3: Anomalous Signal Monitoring (Signal Watch)

**Trigger**: `--watch` or "Monitor anomalous signals"

> **Known blind spot**: Currently only detects growth anomalies in **new projects** (created within 90 days). Detecting sudden surges in established projects requires persistent storage for differential comparison — reserved for future iteration.

### Execution Steps

#### Step 1: Check Quota
```bash
python scripts/check_rate_limit.py
```

#### Step 2: Candidate Discovery
```bash
python scripts/watch_signals.py
# Global scan (default), three windows: 7d/30d/90d
# Domain scan: python scripts/watch_signals.py --domain ai-agent
# domain options: ai-agent, llm-tools, ai-infra, mcp, all (default)
```

The script returns a candidate list (sorted by rough velocity descending), each containing:
- `stars`, `forks`, `created`, `age_days`
- `rough_velocity` = stars / age_days (rough velocity)
- `fork_ratio` = forks / stars (adoption depth signal)

#### Step 3: Initial Screening + Growth Curve Fetching

1. **Exclude obviously irrelevant items**: Check descriptions, exclude games, tutorials, awesome-lists, and other non-technical projects
2. **Fetch star history for remaining candidates** (full mode only):
```bash
python scripts/fetch_star_history.py owner/repo
```

Returned growth metrics:
| Metric | Meaning |
|--------|---------|
| `avg_daily_7d` / `avg_daily_30d` | Average daily growth |
| `acceleration` | 7d avg / 30d avg; >1 means accelerating |
| `trend_direction` | Last 3 days avg / prior 4 days avg; indicates current trend |
| `consecutive_growth_days` | Consecutive days of growth |
| `peak_recency` | Days since peak; 0 = today |
| `burst_ratio` | Peak day / 7d avg; high = spike-type growth |
| `recent_7_days[]` | Daily breakdown; used to assess growth shape |

#### Step 4: Growth Pattern Classification

Examine the shape of `recent_7_days[]` to determine the growth type:

| Pattern | Characteristics | PM Implication | Signal Quality |
|---------|----------------|----------------|----------------|
| **sustained** | `consecutive > 7` + `burst_ratio < 3` | Organic growth, real demand | High |
| **accelerating** | `trend_direction > 2` + `consecutive > 5` | Currently surging, act fast | Highest |
| **spike+decay** | `burst_ratio > 5` + `trend_direction < 0.5` | One-time launch burst, likely noise | Low |
| **step** | Single-day spike + stable before and after | Event-driven (influencer repost) | Medium, watch follow-through |

#### Step 5: Three-Tier Assessment + PM Analysis

Read `agents/analyzer.md` and assess each candidate holistically:

- **Worth deep-diving**: sustained/accelerating pattern + L2/L3 layer
- **Watch**: Has growth signal but pattern is unclear, or step-type awaiting follow-through
- **Ignore**: spike+decay + L5 wrapper / tutorial / fork_ratio < 0.02

### Output Structure

```
headline (one sentence summarizing the most important signal this period)
-> Signal Overview (table: repo / stars / rough velocity / pattern / assessment)
-> Worth Deep-Diving (3-5 deep cards with growth curve data and PM insights)
-> Watch List (table with brief rationale)
-> Ignored This Period (collapsed, with reasons)
```

Report saved to: `output/signal-watch_{date}.html`

---

## Mode 4: Deep Link Analysis

**Trigger**: User provides a repo URL or owner/repo name

### Execution Steps

```bash
# Step 1: Check quota
python scripts/check_rate_limit.py

# Step 2: Fetch complete data
python scripts/deep_link.py langchain-ai/langgraph
# URL input supported: python scripts/deep_link.py https://github.com/langchain-ai/langgraph

# Step 3: Fetch star growth curve (full mode only)
python scripts/fetch_star_history.py langchain-ai/langgraph

# Step 4: Read agents/analyzer.md + references/layer_model.md
#         Generate ecosystem map + Layer positioning + paradigm assessment
```

### Output Structure

```
headline (a bold, tension-bearing judgment that highlights the core tension or most important signal)
-> Basic Profile (table + spark trend chart + commit distribution)
-> Layer Positioning (badge + reasoning + "why not X")
-> Adoption Depth (fork rate / watcher rate / issue activity — distinguishing "spectating" from "actually using")
-> Contributor Structure (table + PM interpretation: bus factor / team vs solo / corporate vs community)
-> Release Cadence (timeline component + product strategy interpretation, not just "how many releases")
-> Issue Composition (table + PM interpretation. If categorization fails (>50% uncategorized),
   must manually sample recent_titles for qualitative analysis as a fallback; never leave blank)
-> Core Innovation (ASCII comparison diagram: traditional approach vs this project's approach.
   This is the fastest path for a PM to understand project value; every report must include one.)
-> Ecosystem Map (ASCII diagram + PM interpretation)
-> Competitor Candidates (collapsed details, annotated with "direct competitor or not" to filter noise)
-> Paradigm Assessment (blue section, structure:
   1. One-sentence paradigm thesis
   2. Core difference: old way vs new way
   3. Who may be threatened
   4. Who is not threatened
   Note: Do not include "relevance to you" — protect privacy)
-> PM Summary (summary-table: maturity / confidence / growth nature / PM value / risk / recommendation)
```

### Output Style

- CSS uses the `--bg/--surface/--border/--accent/--muted` variable system, consistent across modes
- PM insights use `.pm-box` card component (white background + border), not inline `<p>`
- Layer positioning uses `.layer-box` component with badge + reasoning list + "why not X"
- Paradigm assessment uses `.paradigm` component (blue background + border)
- Competitor candidates go in `<details>` collapsed sections
- All technical metrics include plain-language explanations (plain language principle)

Report saved to: `output/deep-link_{owner}_{repo}_{date}.html`

---

## Mode 5: Topic Evolution Timeline

**Trigger**: `--evolve` or user provides a technical topic and wants to see the full evolution landscape of open-source projects in that domain

### Core Philosophy

Mode 5 is not just search + list. It stands on the arc of technology history, uses futurology frameworks to position the current stage, derives classification systems from evolution logic, then fills them with iterative search. Classifications come from **technology evolution logic**, not search keywords.

### Theoretical Foundations

| Framework | Author | Core Idea | Role in Mode 5 |
|-----------|--------|-----------|-----------------|
| Tech Revolution Cycles | Carlota Perez | Irruption→Frenzy→Synergy→Maturity (50-60 years) | Position the topic's stage, determine classification granularity |
| Evolution Axis | Simon Wardley | Genesis→Custom→Product→Commodity | Label maturity level for each classification |
| Combinatorial Evolution | W. Brian Arthur | Technology = combination of existing technologies; tech domains = problem-solving "languages" | Classification = identifying "tech domains" |
| Technium Trends | Kevin Kelly | Technology has intrinsic trends: complexification, specialization, symbiosis | Predict inevitable emerging categories |
| TRL | NASA | 9-level Technology Readiness Level | Assist in labeling domain maturity |

### Execution Steps

#### Phase 1: Scope Boundary Definition

**Goal**: Generate decidable IN/OUT criteria

1. **Core definition**: One sentence defining the topic's essence
2. **Inclusion criteria**: What must a project satisfy to be IN? (2-3 AND conditions)
3. **Exclusion criteria**: What makes a project immediately OUT? (2-3 OR conditions)

**Gate: Present to user for confirmation before proceeding**

#### Phase 2-A: Technology Evolution Positioning (Macro)

Answer three questions using futurology frameworks:

1. **Perez Phase**: Which stage is this topic in — Irruption / Frenzy / Synergy / Maturity?
2. **Core Building Blocks** (Brian Arthur): Which existing technologies serve as "raw materials"? What Wardley stage is each at?
3. **Kelly Trend Projection**: Where do technology's intrinsic trends point?
   - Complexification: simple → composite → systemic
   - Specialization: general → vertical → niche
   - Symbiosis: independent → collaborative → symbiotic
   - Self-reference: execute → optimize execution → optimize "the optimization process"

#### Phase 2-B: Domain Identification (Derive Classifications)

**Method A: Evolution Tree** (top-down)

Draw the technology branching tree from earliest prototype to current frontier. Each branch = one candidate classification.

**Method B: Project Clustering** (bottom-up)

Sample 20-30 projects randomly, describe each sub-problem in 3-5 words, merge similar descriptions.

**Method C: Speculative Domains (minimum 3, mandatory)**

Derive from Kelly trends + Arthur combinatorial logic: categories that barely exist today but will inevitably emerge. Each speculative domain must include:

| Field | Description |
|-------|-------------|
| Speculation logic | Why must it emerge? Which building blocks are in place? |
| Signal signature | If germinating, what keywords / paper patterns / project traits should appear? |
| Search directive | Keywords for Phase 2-C signal hunting |

**Merge results from all three methods**, targeting 5-12 classifications.

#### Phase 2-C: Signal Hunting (Actively Search Speculative Domains)

For each speculative domain, search GitHub / arXiv using signal signature keywords:

```
Found >= 3 projects → Upgrade to Emerging (confirmed germination)
Found 1-2 projects  → Keep as Speculative, annotate observed signals
Found 0 projects    → Keep as Speculative, search again in next iteration
```

#### Phase 2-D: MECE Validation + Confirmation

- **Mutually Exclusive**: Pick any two categories — can you find a project that perfectly belongs to both? Yes → adjust boundaries
- **Collectively Exhaustive**: Can every project be assigned to a category? No → add category or adjust definitions
- **Anomaly detection**: A category with < 3 projects and not speculative → consider merging; a category with > 30% of total → consider splitting

**Gate: Present classification list + evolution tree + Wardley labels to user for confirmation**

#### Phase 3: Judgment Cards

Write a judgment card for each classification:

```
Name: [English]
One-line definition: ...
Wardley Stage: Genesis / Custom / Product / Commodity
Status: Established / Emerging / Speculative
Typical traits (match 2/3 to classify):
  - Trait A
  - Trait B
  - Trait C
Anchor projects: [2-3 unambiguous exemplars]
Easily confused with: [list] → Distinguishing criteria: [how to decide]
Speculation logic (speculative only): Why it must emerge
```

**Judgment cards are embedded at the top of the HTML report** as a collapsible panel.

#### Phase 4: Iterative Search + Classification (Layered Strategy)

Each round:

1. **Search Round N** (reuse Mode 2's `search_repos.py`)
2. **Scope Filter** (Phase 1 rules)
3. **Classify each project** (Phase 3 judgment cards)
4. **Conflict detection**: Matches 2 categories → check which matches more traits
5. **Speculative domain signal scan**: Do any classified projects have sub-features touching speculative domains?
6. **Sample validation**: Randomly pick 2 from each category for manual confirmation
7. **Progress report**: Output "Round N added X new (Y%), cumulative Z, covering M lanes"

**Search round control:**

```
Round 1-2: Mandatory (minimum)
  └─ Checkpoint after Round 2

Checkpoint (after Round 2):
  ├─ Cumulative < 50 projects   → Force Round 3 (insufficient coverage)
  ├─ Cumulative 50-99           → Continue Round 3, unless Round 2 added < 10%
  └─ Cumulative >= 100          → Pause, report to user and ask:
       "Collected N projects covering M lanes.
        Saturation search may need 1-2 more rounds,
        potentially revealing new sub-domains. Continue?"
       User choice:
         ✓ Continue      → Run saturation search (until new < 10%)
         ✗ Stop          → Enter Phase 5 targeted supplement
         ✗ Specify focus  → User gives keywords, search 1 targeted round

Saturation search (if triggered):
  - Output progress report after each round
  - New < 10% → Declare saturation, enter Phase 5
  - Maximum 5 rounds (prevent infinite loops)
```

#### Phase 5: Targeted Supplement + Domain Iteration

- If an Emerging domain has < 3 projects after Phase 4 → trigger targeted search (using judgment card signal signatures)
- If > 20% of new-round projects can't be classified → trigger Phase 2 iteration (add/adjust classifications)
- Speculative domain status transitions:

```
Speculative → Signal found → Emerging → Projects >= 5 → Established
           → No signal after multiple rounds → Label "no current signal", keep for observation
```

### Visualization Output

D3.js interactive timeline with swim-lane layout:
- X-axis: project creation date
- Y-axis: classification swim lanes
- Circle size: log(stars)
- Color: classification color
- Interaction: hover shows details, click opens GitHub
- Top panel: judgment cards (collapsible)
- Bottom table: full project index + one-line descriptions

### Futurology Analysis Layer (Phase 6)

On top of the timeline and project index, overlay two analysis layers:

#### 6-A: Evolution Panorama (6 Dimensions)

Holistic analysis of the complete classified dataset (not per-lane descriptions):

| # | Dimension | Core Question | Method |
|---|-----------|---------------|--------|
| 1 | Stage Assessment | Where is this domain in the technology lifecycle? | Mark stage from data, milestone events viewable per stage |
| 2 | Driving Forces | What underlying forces drive the entire domain? | Find 2-3 cross-lane common drivers, each with evidence chain |
| 3 | Convergence Trajectories | What's happening between lanes? | Identify lane intersection points, derive new directions from convergence |
| 4 | Inevitable vs. Contingent | Which trends are irreversible? Which depend on events? | Two-column comparison, each with reasoning |
| 5 | Scenario Projection | Possible landscape in 12 months? | 2-3 scenarios (optimistic/baseline/risk), with trigger conditions and probability |
| 6 | Weak Signals | What's underestimated but could change the landscape? | Find anomalous proportions, missing directions, concept convergence signals from data |

**Key principles**:
- Analysis subject is **the entire domain**, not lane-by-lane
- Every claim must have data support (project names/counts/ratios) — no empty statements
- Don't name-drop academics ("Kevin Kelly-style", "Carlota Perez framework") — let the analysis speak for itself

#### 6-B: For the Reader (Three-Dimensional Afterword)

The report's final section — meta-analysis of the report itself. Three dimensions, each answering one core question:

| Dimension | Perspective | Core Question | Method |
|-----------|-------------|---------------|--------|
| **Looking Back** | Retrospective | What pattern is repeating? What does it predict? | Identify wave rhythms from data (capability layer → infrastructure layer → safety layer?). Find catalytic chains (which building block spawned which paradigm). Use patterns to predict the next "should-arrive-but-hasn't" layer |
| **Looking Forward** | Endgame | Regardless of which future, what tensions must be resolved? | Review multiple scenarios from projections, extract **structural tensions common to all scenarios** (not predicting an endpoint, but identifying unavoidable problems). Tension = two goals that are structurally contradictory |
| **Looking Now** | Action | What decisions have a time window? | Identify the report's most critical asymmetry (extract specific ratios from data). Name the negative space (directions that should exist per report logic but don't). Declare the report's horizon boundaries (what the data sources can and cannot see) |

**Key principles**:
- All three dimensions are **derived from report data**, not generic philosophical musings
- Each dimension includes specific data points at the bottom (project distributions, ratios, source declarations)
- Looking Forward does not assume a single endgame — use "tensions" instead of "predictions"
- Looking Now must include an honest methodology statement (data coverage and biases)

Report saved to: `output/evolution-timeline_{topic}_{date}.html`

---

## Seed List Customization

Edit `config/seed_list.json` to add or remove developers you follow:

```json
{
  "builders": [
    {"github": "username", "note": "why they matter"}
  ],
  "last_updated": "2026-02-18"
}
```

The default list currently includes 76 important AI builders/orgs, covering 17 categories including labs, agent frameworks, coding agents, inference, platforms, and more.
