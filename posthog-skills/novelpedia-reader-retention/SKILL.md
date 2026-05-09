---
name: novelpedia-reader-retention
category: novelpedia
version: 1.0.0
description: Analyze reader retention and engagement depth by ad acquisition variant using PostHog MCP. Measures D1/D7/D30 retention, post-completion chapter opens, and registration rates grouped by acquisition source.
priority: high
inputs:
  - utm_content_filter (required — specific variant to analyze, e.g., 'gif-v1-Route-Ch1')
  - date_range (default: 30d for completion window, 7d+ required for D7 observation)
  - completion_age_filter (default: timestamp <= now() - INTERVAL 7 DAY for D7/D30 metrics)
outputs:
  - completers (unique persons who completed a chapter)
  - D1/D7/D30 active rate (% who returned on a different day)
  - avg post-completion chapter opens
  - registration rate
requires:
  - PostHog MCP (mcp.posthog.com)
  - chapter_completed + chapter_opened + user_registered events in events table
  - HogQL with dateDiff, uniqIf, INNER JOIN pattern

---

# Novelpedia Reader Retention Analysis by Acquisition Variant

## When to Use This Skill

Use this when you need to understand **reader quality** (not just acquisition cost) by ad variant. 
Essential for comparing:
- Route-Ch1 (direct-to-chapter landing) vs Normal-GIF (synopsis landing)
- Static vs GIF creatives
- Trial vs non-trial variants

**Prerequisite analysis:** Run `novelpedia-aads-cost` first to get CPA/CPR numbers, then use this skill 
to understand whether cheaper completers are actually quality readers.

## Key Discovery (2026-05-09)

Route-Ch1 completers have **3.8x fewer post-completion chapter opens** than Normal-GIF (3.54 vs 13.56 avg)
but cost **2.8x less per completer** ($0.384 vs $1.059). This means Route-Ch1 is a high-volume 
acquisition channel; Normal-GIF produces deeper readers. Use Route-Ch1 for volume, Normal-GIF-style 
creatives for retargeting.

Also: Registration rate from GIF traffic is **0%** for both groups — none of the completers 
from paid GIF ads registered within the observation window.

## MCP Setup (required — same as novelpedia-aads-cost)

```python
import urllib.request, json

API_KEY = "phx_HBorvUARpdZwGBNBuCuTmjnBoRetfHTc4ELdvD5f9pjrECAc"
MCP_URL = "https://mcp.posthog.com/mcp"

def mcp_init():
    init_payload = json.dumps({
        "jsonrpc": "2.0", "method": "initialize",
        "params": {"protocolVersion": "2024-11-05", "capabilities": {},
                   "clientInfo": {"name": "hermes", "version": "1.0"}}, "id": 1
    }).encode()
    req = urllib.request.Request(MCP_URL, data=init_payload,
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json",
                 "Accept": "application/json, text/event-stream"}, method="POST")
    with urllib.request.urlopen(req, timeout=10) as resp:
        return resp.headers.get("Mcp-Session-Id")

SESSION_ID = mcp_init()

def mcp_call(method, params=None):
    payload = json.dumps({"jsonrpc": "2.0", "method": method, "params": params or {}, "id": 3}).encode()
    req = urllib.request.Request(MCP_URL, data=payload,
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json",
                 "Accept": "application/json, text/event-stream",
                 "Mcp-Session-Id": SESSION_ID}, method="POST")
    with urllib.request.urlopen(req, timeout=120) as resp:
        return resp.read().decode()

def parse_sse(raw):
    for line in raw.strip().split('\n'):
        if line.startswith('data: '):
            return json.loads(line[6:])["result"]["content"][0]["text"]
    return ""
```

## Retention Query Template (D7/D30 for 7d+ old completers)

Use this for variants with enough history (7d+ old completers). Filter: `timestamp <= now() - INTERVAL 7 DAY`.

```hogql
SELECT
    group_name,
    uniq(person_id) AS completers,
    uniqIf(person_id, d7_days >= 1) AS d7_active,
    round(avg(d7_days), 2) AS avg_d7_days,
    uniqIf(person_id, d30_days >= 1) AS d30_active,
    round(avg(d30_days), 2) AS avg_d30_days,
    uniqIf(person_id, reg_flag = 1) AS registered
FROM (
    SELECT
        e.person_id,
        'VARIANT_GROUP_NAME' AS group_name,
        -- d7_days: count of DISTINCT calendar days with chapter_opened between completion+1d and completion+7d
        countIf(e.event = 'chapter_opened' AND dateDiff('day', c.completion_ts, e.timestamp) >= 1 AND dateDiff('day', c.completion_ts, e.timestamp) <= 7) AS d7_days,
        -- d30_days: same but up to 30 days
        countIf(e.event = 'chapter_opened' AND dateDiff('day', c.completion_ts, e.timestamp) >= 1 AND dateDiff('day', c.completion_ts, e.timestamp) <= 30) AS d30_days,
        maxIf(1, e.event = 'user_registered' AND e.timestamp >= c.completion_ts) AS reg_flag
    FROM events AS e
    INNER JOIN (
        SELECT person_id, min(timestamp) AS completion_ts
        FROM events
        WHERE event = 'chapter_completed'
          AND timestamp >= now() - INTERVAL 30 DAY
          AND timestamp <= now() - INTERVAL 7 DAY  -- must be 7d+ old for D7 observation
          AND isNotNull(properties.utm_content)
          AND properties.utm_content != ''
          AND properties.utm_content ILIKE '%gif%'
          AND properties.utm_campaign NOT IN ('novelpedia-launch', 'novelpedia')
          -- Add variant filter here, e.g.: AND properties.utm_content IN ('gif-v1-Route-Ch1', 'gif-v1-route-ch1')
        GROUP BY person_id
    ) AS c ON c.person_id = e.person_id
    WHERE e.event IN ('chapter_opened', 'user_registered')
      AND e.timestamp > c.completion_ts
    GROUP BY e.person_id
)
GROUP BY group_name
```

## D1 Retention for Recent Completers (<7d old)

For new variants that don't have 7d+ old completers yet. Measures same/next-day activity.

```hogql
SELECT
    uniq(person_id) AS completers,
    uniqIf(person_id, post_comp_reads > 0) AS d1_active,
    round(avg(post_comp_reads), 2) AS avg_post_comp_reads,
    uniqIf(person_id, reg_flag = 1) AS registered
FROM (
    SELECT
        e.person_id,
        countIf(e.event = 'chapter_opened' AND dateDiff('day', c.completion_ts, e.timestamp) >= 0 AND dateDiff('day', c.completion_ts, e.timestamp) <= 1) AS post_comp_reads,
        maxIf(1, e.event = 'user_registered' AND e.timestamp >= c.completion_ts) AS reg_flag
    FROM events AS e
    INNER JOIN (
        SELECT person_id, min(timestamp) AS completion_ts
        FROM events
        WHERE event = 'chapter_completed'
          AND timestamp >= now() - INTERVAL 30 DAY
          AND timestamp > now() - INTERVAL 7 DAY  -- recent completers
          AND isNotNull(properties.utm_content)
          AND properties.utm_content != ''
          AND properties.utm_content IN ('gif-v1-Route-Ch1', 'gif-v1-route-ch1')
          AND properties.utm_campaign NOT IN ('novelpedia-launch', 'novelpedia')
        GROUP BY person_id
    ) AS c ON c.person_id = e.person_id
    WHERE e.event IN ('chapter_opened', 'user_registered')
      AND e.timestamp >= c.completion_ts
    GROUP BY e.person_id
)
```

## Key HogQL Patterns That Work

1. **`dateDiff('day', ts1, ts2)` for day-based filtering** — NOT `toDate()` on DateTime columns (causes `Illegal type DateTime64(6, 'UTC')` error)
2. **`uniqIf(col, cond)` for conditional unique counts** — NOT `DISTINCTIf(...)` (unsupported function)
3. **Table aliases for JOINs** — Always use `events AS e` and qualify all field references to avoid `Ambiguous query` errors
4. **INNER JOIN on person_id + completion_ts** — Pre-compute completion timestamps in a subquery, then join to get post-completion events
5. **`HAVING countIf(event = 'chapter_completed') > 0`** — Ensures only people who actually completed are included

## Common Errors and Fixes

| Error | Cause | Fix |
|---|---|---|
| `Unsupported function call 'DISTINCTIf(...)'` | Wrong function name | Use `uniqIf(col, cond)` instead |
| `Illegal type DateTime64(6, 'UTC') of first argument of function toDateOrNull` | Using `toDate()` on DateTime column | Use `dateDiff('day', ts1, ts2)` instead |
| `Aggregation 'min' cannot be nested inside another aggregation` | `countIf(min(timestamp)...)` pattern | Pre-compute min timestamp in subquery before aggregate |
| `Found multiple sources for field: person_id` | Multiple JOINs without table alias qualification | Use `e.person_id` not bare `person_id` |
| `GROUP BY` returns empty despite data existing | `properties.utm_content` not accessible as `utm_content` alone | Always qualify: `properties.utm_content` |
| `Received an empty SQL insight` from query generator | AI-generated HogQL fails on complex queries | Write HogQL manually using patterns above |

## Route-Ch1 Data Context (2026-05-09)

When analyzing Route-Ch1 variants, note:
- Route-Ch1 completers are all recent (< 7 days old) — Normal-GIF has 7d+ history, Route-Ch1 doesn't yet
- This means D7/D30 metrics are NOT available for Route-Ch1 (n=0 for 7d+ old), only D1 metrics
- Normal-GIF: 66 completers (7d+ old), 33.3% D7 active, 36.4% D30 active, 13.56 avg post-comp chapter opens
- Route-Ch1 recent (n=13): 100% D1 active, 3.54 avg post-comp chapter opens
- Registration rate is 0% for both — paid GIF traffic does not convert to registered users

## Interpretation Framework

| Metric | What It Measures | Low = Problem If |
|---|---|---|
| Post-comp chapter opens | Session depth / engagement immediately after completion | High is always better |
| D1/D7/D30 active | Did they come back on a different day? | Low = weak return rate |
| Avg unique days | Consistency of reading behavior | Low = casual, not habitual |
| Registration rate | Conversion to registered user | Low = acquisition channel not producing users |