---
name: novelpedia-aads-cost
category: novelpedia
version: 1.0.0
description: Query A-ADS spend data joined with PostHog chapter events to compute true cost per completed reader per campaign/variant. Uses PostHog MCP (query-run) with BigQuery warehouse integration.
priority: critical
inputs:
  - campaign_filter (optional, defaults to all active campaigns)
  - date_range (7d or 14d)
outputs:
  - Spend, clicks, visitors, readers, completers per variant
  - CPA (cost per completer), CPV (cost per visitor), CPR (cost per reader)
  - Kill/scale/hold recommendation per variant
requires:
  - PostHog MCP (mcp.posthog.com) — 268 tools, use tools/call
  - bigquery.spend_daily — A-ADS spend data in PostHog warehouse
  - chapter_opened / chapter_completed events in PostHog events table
  - HogQLQuery wrapped object passed to query-run tool

---

# Novelpedia AADS Cost Analysis via PostHog MCP

## Key Discovery (2026-04-29)

The PostHog MCP at `https://mcp.posthog.com/mcp` exposes a `query-run` tool
that accepts HogQL queries against `bigquery.spend_daily` (A-ADS spend) JOINED
with PostHog `events` table (chapter events).

**This replaces the broken BigQuery direct access path.**

## MCP Session Setup (required for every session)

PostHog MCP uses a session-based protocol. Each session requires:

1. **Initialize** to get a session ID from response headers
2. **Use that session ID** in all subsequent tool calls

```python
import urllib.request, json

API_KEY = "phx_HBorvUARpdZwGBNBuCuTmjnBoRetfHTc4ELdvD5f9pjrECAc"
MCP_URL = "https://mcp.posthog.com/mcp"

def mcp_init():
    init_payload = json.dumps({
        "jsonrpc": "2.0",
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "hermes", "version": "1.0"}
        },
        "id": 1
    }).encode()

    req = urllib.request.Request(
        MCP_URL, data=init_payload,
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream"
        },
        method="POST"
    )

    with urllib.request.urlopen(req, timeout=10) as resp:
        session_id = resp.headers.get("Mcp-Session-Id")
        return session_id

SESSION_ID = mcp_init()  # e.g. "a0116ec4590482009bc92693eb667bcc9674f9152741f3e88090aea349d71fdc"
```

## Tool Invocation Pattern

**Correct:**
```python
def mcp_call(method, params=None):
    payload = json.dumps({"jsonrpc": "2.0", "method": method, "params": params or {}, "id": 3}).encode()
    req = urllib.request.Request(
        MCP_URL, data=payload,
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "Mcp-Session-Id": SESSION_ID
        }, method="POST"
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read().decode()

# Call query-run with HogQLQuery wrapped object
result = mcp_call("tools/call", {
    "name": "query-run",
    "arguments": {"query": {"kind": "HogQLQuery", "query": "SELECT 1 AS test"}}
})
```

**Common mistakes:**
- Passing query as a raw string → `Invalid arguments for tool query-run: expected object`
- Missing `kind: "HogQLQuery"` discriminator → `No matching discriminator`
- Calling `query-run` directly as RPC method (not via tools/call) → `Method not found`
- Using wrong session ID or expired session → `Session not found`
- Session ID not included in headers → `Session not found`

## Primary Query: Cost Per Funnel Stage

```hogql
SELECT
    s.utm_campaign,
    s.utm_content,
    sum(s.clicks) AS reported_clicks,
    round(sum(s.cost_usd), 2) AS total_cost,
    coalesce(ph.unique_visitors, 0) AS visitors,
    coalesce(ph.chapter_openers, 0) AS readers,
    coalesce(ph.chapter_completers, 0) AS completers,
    round(sum(s.cost_usd) / nullIf(coalesce(ph.unique_visitors, 0), 0), 4) AS cost_per_visitor,
    round(sum(s.cost_usd) / nullIf(coalesce(ph.chapter_openers, 0), 0), 4) AS cost_per_reader,
    round(sum(s.cost_usd) / nullIf(coalesce(ph.chapter_completers, 0), 0), 4) AS cost_per_completer
FROM bigquery.spend_daily s
LEFT JOIN (
    SELECT
        properties.utm_campaign AS utm_campaign,
        properties.utm_content AS utm_content,
        uniqIf(person_id, event = '$pageview') AS unique_visitors,
        uniqIf(person_id, event = 'chapter_opened') AS chapter_openers,
        uniqIf(person_id, event = 'chapter_completed') AS chapter_completers
    FROM events
    WHERE timestamp >= now() - INTERVAL 7 DAY
      AND isNotNull(properties.utm_campaign)
      AND properties.utm_campaign != ''
    GROUP BY utm_campaign, utm_content
) ph ON CASE
        WHEN s.utm_campaign = 'self-summoning-gif-v2' THEN 'self-summoning-demon'
        ELSE replaceRegexpAll(s.utm_campaign, '__.*$', '')
    END = ph.utm_campaign
 AND s.utm_content = ph.utm_content
WHERE s.date >= today() - INTERVAL 7 DAY
  AND s.utm_campaign NOT IN ('novelpedia-launch', 'novelpedia')
  AND s.cost_usd > 0
GROUP BY s.utm_campaign, s.utm_content, ph.unique_visitors, ph.chapter_openers, ph.chapter_completers
ORDER BY sum(s.cost_usd) DESC
LIMIT 50
```

## Campaign Name Mapping Quirks

| A-ADS campaign_id | PostHog utm_campaign | Notes |
|---|---|---|
| `self-summoning-demon` | `self-summoning-demon` | Direct match |
| `self-summoning-gif-v2` | maps to `self-summoning-demon` via CASE | causes double-count |
| `reader-mage` | `reader-mage` | Direct match |
| `reader-mage__trial` | `reader-mage` via strip `__.*$` | Trial sub-campaign |
| `gu-demon-king` | `gu-demon-king` | Direct match |
| `weakest-kobold` | `weakest-kobold` | Direct match |

**Always filter out** `utm_campaign IN ('novelpedia-launch', 'novelpedia')` — internal campaigns.

## Decision Matrix

| CPA Completer | Action | Threshold |
|---|---|---|
| < $0.60 | SCALE | Best in class |
| $0.60–$1.00 | Scale | Profitable |
| $1.00–$1.50 | HOLD | Marginal |
| > $1.50 | KILL | Unprofitable |
| null (0 completers) | KILL | No conversion |

**Volume guard:** Require at least 5 completers before declaring a variant "scale" — thin data produces unstable CPAs.

## BigQuery Table Schema

`bigquery.spend_daily` columns:
- `date` — DATE
- `network` — STRING (e.g., "aads")
- `campaign_id` — STRING
- `utm_campaign` — STRING
- `utm_content` — STRING (creative variant name)
- `utm_source` — STRING
- `utm_medium` — STRING
- `cost_usd` — FLOAT64
- `clicks` — INT64
- `impressions` — INT64
- `loaded_at` — TIMESTAMP (incremental cursor for PostHog sync)

## Known Issues

1. **Session expiry**: MCP sessions time out. If `Session not found`, re-initialize and get a fresh session ID.
2. **Double-counting**: When A-ADS campaign name equals `utm_content` value (e.g., `self-summoning-gif-v2` with content `gif-v2`), it appears as a separate row — filter or merge.
3. **visitor count discrepancy**: PostHog `unique_visitors` may differ from A-ADS clicks due to cookie churn, VPN users, and attribution window differences.
4. **ORDER BY alias not allowed**: Using `ORDER BY total_cost` (the alias) gives `Field not found: total_cost`. Always use `ORDER BY sum(s.cost_usd) DESC` instead.
5. **SSE parsing is non-obvious**: The raw response contains SSE lines mixed with a JSON text block. Always use `parse_sse()` function above — do NOT try to navigate `structuredContent` via JSON paths.
6. **`DISTINCTIf` not supported**: Use `uniqIf(col, cond)` instead. `DISTINCTIf(...)` → `Unsupported function call 'DISTINCTIf(...)'`.
7. **`toDate()` on DateTime columns fails**: Error `Illegal type DateTime64(6, 'UTC') of first argument of function toDateOrNull`. Use `dateDiff('day', ts1, ts2)` for day-diff comparisons instead.
8. **`min()` nested in aggregate fails**: `countIf(min(timestamp) ...)` → `Aggregation 'min' cannot be nested inside another aggregation`. Pre-compute in a subquery.
9. **Ambiguous field (multiple sources)**: When joining events table twice (completion + reads), use table aliases (`e`, `c`) and qualify all field references. Error: `Found multiple sources for field: person_id`.
10. **`query-generate-hogql-from-question` is unreliable**: Returns "Received an empty SQL insight" for complex queries. Write HogQL manually.
11. **`GROUP BY timestamp` returns empty**: When GROUP BY produces no rows despite data existing, check that `properties.utm_content` is accessed correctly (not as `utm_content` alone). Always qualify: `properties.utm_content`.

### Daily Trend Query (per campaign × variant × day)

Use this to see day-by-day performance trends for a specific campaign. Essential for detecting spend anomalies, V→R drops, and budget exhaustion.

```hogql
SELECT
    s.date,
    s.utm_campaign,
    s.utm_content,
    s.clicks AS aads_clicks,
    round(s.cost_usd, 4) AS cost,
    coalesce(ph.visitors, 0) AS visitors,
    coalesce(ph.readers, 0) AS readers,
    coalesce(ph.completers, 0) AS completers
FROM bigquery.spend_daily s
LEFT JOIN (
    SELECT
        toDate(timestamp) AS date,
        properties.utm_campaign AS utm_campaign,
        properties.utm_content AS utm_content,
        uniqIf(person_id, event = '$pageview') AS visitors,
        uniqIf(person_id, event = 'chapter_opened') AS readers,
        uniqIf(person_id, event = 'chapter_completed') AS completers
    FROM events
    WHERE timestamp >= now() - INTERVAL 14 DAY
      AND isNotNull(properties.utm_campaign)
      AND properties.utm_campaign != ''
    GROUP BY date, utm_campaign, utm_content
) ph ON s.date = ph.date
 AND replaceRegexpAll(s.utm_campaign, '__.*$', '') = ph.utm_campaign
 AND s.utm_content = ph.utm_content
WHERE s.date >= today() - INTERVAL 14 DAY
  AND s.utm_campaign = 'CAMPAIGN_NAME'
  AND s.utm_content = 'VARIANT_NAME'
ORDER BY s.date
```

**Key flags to detect in daily data:**
- Spend ≈ $0 in 12h → campaign is paused or budget exhausted
- V→R drop >3pp day-over-day → possible audience drift or creative fatigue
- CPC jumps >50% vs baseline → A-ADS algorithm re-optimizing
- 0 completers with >3 readers → paywall friction (trial gate) or Ch.2 bottleneck

## Also Available: Other HogQL Queries

### Daily Ad Spend by Campaign & Creative
```hogql
SELECT
    date, utm_campaign, utm_content,
    clicks, round(cost_usd, 4) AS cost_usd,
    round(cost_usd / nullIf(clicks, 0), 5) AS cpc
FROM bigquery.spend_daily
WHERE date >= today() - INTERVAL 7 DAY
  AND utm_campaign NOT IN ('novelpedia-launch', 'novelpedia')
ORDER BY date DESC, cost_usd DESC
LIMIT 100
```

### Clicks vs Visits Reconciliation
```hogql
SELECT
    s.utm_campaign, s.utm_content,
    sum(s.clicks) AS reported_clicks,
    coalesce(ph.unique_visitors, 0) AS posthog_visitors,
    round(coalesce(ph.unique_visitors, 0) * 100.0 / nullIf(sum(s.clicks), 0), 1) AS visit_rate_pct,
    round(sum(s.cost_usd) / nullIf(coalesce(ph.unique_visitors, 0), 0), 4) AS cost_per_visitor
FROM bigquery.spend_daily s
LEFT JOIN (
    SELECT properties.utm_campaign AS utm_campaign,
           properties.utm_content AS utm_content,
           uniq(person_id) AS unique_visitors
    FROM events
    WHERE event = '$pageview'
      AND timestamp >= now() - INTERVAL 7 DAY
      AND isNotNull(properties.utm_campaign)
      AND properties.utm_campaign != ''
      AND properties.utm_campaign NOT IN ('novelpedia-launch', 'novelpedia')
      AND isNotNull(properties.utm_content)
      AND properties.utm_content != ''
    GROUP BY utm_campaign, utm_content
) ph ON CASE
        WHEN s.utm_campaign = 'self-summoning-gif-v2' THEN 'self-summoning-demon'
        ELSE replaceRegexpAll(s.utm_campaign, '__.*$', '')
    END = ph.utm_campaign
 AND s.utm_content = ph.utm_content
WHERE s.date >= today() - INTERVAL 7 DAY
  AND s.utm_campaign NOT IN ('novelpedia-launch', 'novelpedia')
GROUP BY s.utm_campaign, s.utm_content, ph.unique_visitors
ORDER BY sum(s.cost_usd) DESC
LIMIT 100
```

### Reading Depth Funnel by Campaign & Creative (14d, person-level)
```hogql
SELECT
    campaign, source, creative,
    uniq(person_id) AS visitors,
    uniqIf(person_id, has_chapter_opened = 1) AS opened_chapter,
    uniqIf(person_id, has_ch3 = 1) AS reached_ch3,
    uniqIf(person_id, has_registered = 1) AS registered,
    round(uniqIf(person_id, has_chapter_opened = 1) * 100.0 / nullIf(uniq(person_id), 0), 1) AS open_rate_pct,
    round(uniqIf(person_id, has_ch3 = 1) * 100.0 / nullIf(uniq(person_id), 0), 1) AS ch3_rate_pct
FROM (
    SELECT
        person_id,
        anyIf(properties.utm_campaign, event = '$pageview' AND isNotNull(properties.utm_campaign) AND properties.utm_campaign != '' AND properties.utm_campaign NOT IN ('novelpedia-launch', 'novelpedia')) AS campaign,
        anyIf(properties.utm_source, event = '$pageview' AND isNotNull(properties.utm_source) AND properties.utm_source != '') AS source,
        anyIf(properties.utm_content, event = '$pageview' AND isNotNull(properties.utm_content) AND properties.utm_content != '') AS creative,
        maxIf(1, event = 'chapter_opened') AS has_chapter_opened,
        maxIf(1, event = 'chapter_completed' AND toFloat(properties.chapter_number) = 3) AS has_ch3,
        maxIf(1, event = 'user_registered') AS has_registered,
        maxIf(1, event = '$pageview' AND isNotNull(properties.utm_campaign) AND properties.utm_campaign != '' AND properties.utm_campaign NOT IN ('novelpedia-launch', 'novelpedia') AND isNotNull(properties.utm_content) AND properties.utm_content != '') AS has_campaign_pv
    FROM events
    WHERE timestamp >= now() - INTERVAL 14 DAY
    GROUP BY person_id
)
WHERE has_campaign_pv = 1
  AND campaign != ''
  AND creative != ''
  AND (campaign, creative) IN (
      SELECT
          CASE WHEN utm_campaign = 'self-summoning-gif-v2' THEN 'self-summoning-demon'
               ELSE replaceRegexpAll(utm_campaign, '__.*$', '')
          END,
          utm_content
      FROM bigquery.spend_daily
      WHERE date >= today() - INTERVAL 7 DAY
        AND cost_usd > 0
  )
GROUP BY campaign, source, creative
ORDER BY visitors DESC
LIMIT 100
```

## PostHog MCP Tool Discovery

268 tools available. Key ones:
- `query-run` — Execute HogQL queries (primary workhorse)
- `insight-query` — Execute a saved insight by numeric ID or short_id
- `query-generate-hogql-from-question` — AI-generated HogQL from natural language
- `dashboard-insights-run` — Run all insights on a dashboard

## Setup Verification

```python
result = mcp_call("tools/call", {
    "name": "query-run",
    "arguments": {"query": {"kind": "HogQLQuery", "query": "SELECT 1 AS test"}}
})
assert "test" in result, "MCP session invalid or expired"
```

## SSE Response Parsing (CRITICAL — not documented in MCP)

PostHog MCP returns SSE-wrapped JSON-RPC. The actual data is embedded inside a text block.

**What failed:**
- `parsed["result"]["structuredContent"]["results"]` → KeyError (not a real JSON path)
- `parsed["result"]["results"]` → `[]` (empty)
- `json.loads(raw)` on full response → fails on mixed SSE lines
- Using alias in `ORDER BY` → `"Field not found: total_cost"` — always use `ORDER BY sum(s.cost_usd) DESC`
- `re.search(r'"structuredContent": \{.*\}', text)` → JSON is nested inside a text field, regex fails

**Working pattern (2026-04-29, verified):**

```python
def parse_sse(raw):
    """Parse SSE-wrapped MCP response. Returns raw text block."""
    lines = raw.strip().split('\n')
    for line in lines:
        if line.startswith('data: '):
            return json.loads(line[6:])["result"]["content"][0]["text"]
    return ""

def extract_rows(text_block):
    """Extract (columns, rows) from text block.
    Format: 'columns[N]: col1,col2' then 'results[N]:' then '    - [N]: val1,val2'
    """
    import re
    lines = text_block.split('\n')
    columns, results = [], []
    for line in lines:
        cm = re.search(r'columns\[(\d+)\]: (.+)', line)
        rm = re.search(r'^\s+-\s+\[(\d+)\]: (.+)', line)
        if cm:
            columns = [c.strip() for c in cm.group(2).split(',')]
        elif rm and columns:
            vals = [v.strip() for v in rm.group(2).split(',')]
            results.append(dict(zip(columns, vals)))
    return columns, results

# Usage:
text_block = parse_sse(mcp_call("tools/call", {...}))
columns, rows = extract_rows(text_block)
for r in rows:
    print(dict(zip(columns, r)))
```

**Simpler alternative:** For quick inspection, print the first 100 chars of the text block and read the `columns[N]:` + `    - [N]: val` lines manually — faster than debugging the extractor for small results.

**The `structuredContent` field** appears in the raw text block as an embedded JSON string but is NOT accessible via any JSON path. Do not try to navigate to it.
