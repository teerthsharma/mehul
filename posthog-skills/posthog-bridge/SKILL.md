---
name: posthog-bridge
category: novelpedia/analytics
version: 3.0.0
description: Controlled PostHog access layer. Maps named capabilities to actual API endpoints. Updated with real endpoint data.
priority: critical
inputs:
  - capability_name (get_funnel, get_trend, etc.)
  - parameters
outputs:
  - Formatted metric response
  - Error with fix suggestion
requires:
  - PostHog Events API
  - PostHog Dashboard API

---

# PostHog Bridge v3.0

## Critical Endpoint Correction (v2 → v3)

| Endpoint | Status | Notes |
|----------|--------|-------|
| `https://app.posthog.com/api/projects/314999/events/` | ✅ WORKS | Primary data source |
| `https://app.posthog.com/api/projects/314999/dashboards/{id}/` | ✅ WORKS | Dashboard tiles |
| `https://app.posthog.com/api/projects/314999/cohorts/` | ✅ WORKS (empty) | 0 cohorts exist |
| `https://app.posthog.com/api/projects/314999/funnels/{id}/` | ❌ 404 | No funnels exist |
| `https://app.posthog.com/api/projects/314999/insights/trend/` | ❌ 403 | Forbidden |
| `https://app.posthog.com/api/projects/314999/feature_flags/` | ✅ WORKS (empty) | 0 flags exist |
| `https://mcp.posthog.com/api/projects/314999/events/` | ❌ 404 | DO NOT USE |

## MCP: query-run (PRIMARY — for cost-weighted analysis)

The PostHog MCP is available via the gateway and exposes **`query-run`** which executes HogQL
queries against the data warehouse, including `bigquery.spend_daily` for A-ADS cost data.

### MCP Setup (one-time session)

```python
import urllib.request, json, re

API_KEY = "phx_HBorvUARpdZwGBNBuCuTmjnBoRetfHTc4ELdvD5f9pjrECAc"
MCP_URL = "https://mcp.posthog.com/mcp"

def mcp_init():
    init_payload = json.dumps({
        "jsonrpc": "2.0", "method": "initialize",
        "params": {"protocolVersion": "2024-11-05", "capabilities": {},
                   "clientInfo": {"name": "hermes", "version": "1.0"}}, "id": 1
    }).encode()
    req = urllib.request.Request(MCP_URL, data=init_payload,
        headers={"Authorization": f"Bearer {API_KEY}",
                 "Content-Type": "application/json",
                 "Accept": "application/json, text/event-stream"},
        method="POST")
    with urllib.request.urlopen(req, timeout=10) as resp:
        response = resp.read().decode()
    sid = re.search(r'"Mcp-Session-Id"\s*:\s*"([^"]+)"', response)
    return sid.group(1) if sid else None

SESSION_ID = mcp_init()  # Cache and reuse
```

### Executing HogQL via MCP

```python
def mcp_query(query_str, session_id):
    payload = json.dumps({
        "jsonrpc": "2.0", "method": "tools/call",
        "params": {"name": "query-run",
                   "arguments": {"query": {"kind": "HogQLQuery", "query": query_str}}},
        "id": 3
    }).encode()
    req = urllib.request.Request(MCP_URL, data=payload,
        headers={"Authorization": f"Bearer {API_KEY}",
                 "Content-Type": "application/json",
                 "Accept": "application/json, text/event-stream",
                 "Mcp-Session-Id": session_id},
        method="POST")
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode())
```

### Key BigQuery Tables

| Table | Contents |
|-------|----------|
| `bigquery.spend_daily` | A-ADS daily spend: date, utm_campaign, utm_content, clicks, cost_usd, impressions |

### Standard Cost-Per-Funnel-Stage Query (7d)

```hogql
SELECT
    s.utm_campaign, s.utm_content,
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
    SELECT properties.utm_campaign AS utm_campaign, properties.utm_content AS utm_content,
           uniqIf(person_id, event = '$pageview') AS unique_visitors,
           uniqIf(person_id, event = 'chapter_opened') AS chapter_openers,
           uniqIf(person_id, event = 'chapter_completed') AS chapter_completers
    FROM events WHERE timestamp >= now() - INTERVAL 7 DAY
      AND isNotNull(properties.utm_campaign) AND properties.utm_campaign != ''
    GROUP BY utm_campaign, utm_content
) ph ON CASE WHEN s.utm_campaign = 'self-summoning-gif-v2' THEN 'self-summoning-demon'
             ELSE replaceRegexpAll(s.utm_campaign, '__.*$', '') END = ph.utm_campaign
   AND s.utm_content = ph.utm_content
WHERE s.date >= today() - INTERVAL 7 DAY
  AND s.utm_campaign NOT IN ('novelpedia-launch', 'novelpedia')
  AND s.cost_usd > 0
GROUP BY s.utm_campaign, s.utm_content, ph.unique_visitors, ph.chapter_openers, ph.chapter_completers
ORDER BY sum(s.cost_usd) DESC LIMIT 50
```

### Known A-ADS Campaign JOIN Mapping

| A-ADS Campaign (utm_campaign) | Maps To |
|---|---|
| `self-summoning-gif-v2` | `self-summoning-demon` (exception — literal match before regex) |
| Pattern `__.*$` stripped | Campaign slug (e.g., `reader-mage`, `gu-demon-king`) |

### Session ID Persistence
- A single MCP session ID is valid for the lifetime of the gateway process
- If `tools/call` returns `Session not found`, re-run `mcp_init()` to get a fresh session ID

## HTTP Client (Events API — no session needed)

- **`urllib.request` FAILS** in hermes execute_code sandbox for app.posthog.com — returns HTTP 404
- **Use `subprocess.run(['curl', ...])` instead** for events API
- **Bearer auth**: `Authorization: Bearer phx_HBorvUARpdZwGBNBuCuTmjnBoRetfHTc4ELdvD5f9pjrECAc`

## Working Recipe: Events API via curl

```python
import subprocess, json
from collections import defaultdict

API_KEY = "phx_HBorvUARpdZwGBNBuCuTmjnBoRetfHTc4ELdvD5f9pjrECAc"
BASE = "https://app.posthog.com/api/projects/314999"

def fetch_events(event, after="14d"):
    all_events, url = [], f"{BASE}/events/?event={event}&limit=5000&after=-{after}"
    while url:
        result = subprocess.run(["curl", "-s", "-H", f"Authorization: Bearer {API_KEY}", url],
                                capture_output=True, text=True, timeout=30)
        data = json.loads(result.stdout)
        all_events.extend(data.get("results", []))
        url = data.get("next")
    return all_events
```

## Alert Rules

1. If funnel ID referenced -> ERROR "use events API with Python aggregation instead"
2. If cohort queried -> return 0 + "create cohort in PostHog UI"
3. If feature flag queried -> return False + "no flags defined"
4. If events API returns < 5 events -> WARN "low volume, verify tracking"
5. If 404 from mcp.posthog.com -> switch to app.posthog.com
6. **If HogQL query returns permission_denied -> the MCP session expired, re-run mcp_init()**

## Real Dashboard IDs

| ID | Name |
|----|------|
| 1458931 | Executive Overview |
| 1458292 | Reader App |
| 1458291 | Author App |
| 1484131 | Campaign ROI and Activation |
| 1483188 | Overall Platform |
| 1483189 | Reader Platform |
| 1483191 | Author Platform |

## Real Event Properties

All documented in: posthog-metrics-pack/references/GROUND_TRUTH.json

Key events:
- chapter_opened: novel_id, chapter_number, word_count, utm_*, http_country_code, time_spent_sec
- chapter_completed: same as chapter_opened + time_spent_sec
- user_registered: role, has_email, is_migrated (NO UTM)
- novel_detail_viewed: novel_id, novel_title, utm_*, http_country_code

## Degraded Mode

When insights API (403) or dashboard API fails:
- Use events API with Python aggregation (recipe above)
- Group by event type + date + UTM in Python
- Report with `data_quality: degraded` flag
