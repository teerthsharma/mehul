---
name: binge-reader-funnel-health
category: novelpedia/analytics
version: 2.1.0
description: Binge reader funnel analysis. Queries real funnel steps via TrendsQuery (NOT funnel ID — funnel IDs return 404).
priority: critical
inputs:
  - date_range (7d, 14d, 30d)
  - campaign_filter (utm_campaign is_set, exclude internal)
outputs:
  - Conversion rate per funnel step
  - Drop-off point identification
  - Campaign breakdown
requires:
  - PostHog Events API
  - PostHog Dashboard API (for query patterns)
---

# Binge Reader Funnel Health

## Funnel Definition

**IMPORTANT: Funnel IDs return 404.** Use TrendsQuery with event series instead.

### Actual Funnel Steps (from Campaign ROI dashboard Tile 6)
```
Step 1: novel_detail_viewed    (discovery)
Step 2: chapter_opened         (activation) ← north-star
Step 3: chapter_completed      (engagement)
```

**⚠️ This is a 3-step funnel, not 4-step.** The app_opened → novel_detail step is not a tracked conversion event in PostHog.

### Filter Pattern (from real dashboard)
```
utm_campaign is_set
utm_campaign is_not ["novelpedia-launch", "novelpedia"]
utm_source is_not ["aads-ranobes", "aads-freewebnovel"]
```

---

## MCP Commands (Events API Only)

Since funnel API is 404, use the events API to count distinct users per step:

```python
# Step 1: novel_detail_viewed
/events/?event=novel_detail_viewed&limit=1&after=-{days}d

# Step 2: chapter_opened
/events/?event=chapter_opened&limit=1&after=-{days}d

# Step 3: chapter_completed
/events/?event=chapter_completed&limit=1&after=-{days}d
```

For campaign breakdown, use the Dashboard Query pattern (Tile 6 of 1484131):
- Breakdown by: utm_campaign
- Metrics: novel_detail_viewed (total), chapter_opened (total), chapter_completed (total)

---

## Conversion Rate Calculation

```
novel_detail_viewed → chapter_opened: chapter_opened / novel_detail_viewed
chapter_opened → chapter_completed: chapter_completed / chapter_opened
novel_detail_viewed → chapter_completed: chapter_completed / novel_detail_viewed
```

---

## Alert Thresholds

| Step | Healthy | Warning | Critical |
|------|---------|---------|---------|
| Step 1→2 (discovery→activation) | > 40% | 20-40% | < 20% |
| Step 2→3 (activation→completion) | > 30% | 15-30% | < 15% |

---

## What to Look For

1. **Drop-off at Step 1→2**: Novel detail page not converting to chapter open — check if chapters are loading, if free content is available
2. **Drop-off at Step 2→3**: Chapters opening but not completing — check chapter length, content quality, time_spent_sec
3. **Campaign differences**: Some campaigns may drive high novel_detail but low chapter_opened — indicates landing page problem

---

## Degraded Mode

If events API is slow, use the Campaign ROI dashboard (1484131) Tile 6 which has pre-computed breakdowns by campaign.

---

## MCP Command Reference

Since ph_get_funnel returns 404, use ph_query_insights for TrendsQuery:

```json
{
  "kind": "TrendsQuery",
  "source": {
    "kind": "EventsNode",
    "event": "chapter_opened",
    "math": "total",
    "properties": [
      {"key": "utm_campaign", "type": "event", "operator": "is_set"},
      {"key": "utm_campaign", "type": "event", "operator": "is_not", "value": ["novelpedia-launch", "novelpedia"]}
    ]
  },
  "dateRange": {"date_from": "-7d"}
}
```

---

## Data Quality Notes

## MCP Failure Mode -- SSE Transport Issues

**Known issue (April 2026):** When `mcp_init()` returns `None`, the PostHog MCP SSE transport is failing in hermes-agent sandbox environments. This is a session-establishment problem, NOT a credential problem.

**Workaround -- REST API fallback (verified working):**
```python
import urllib.request, json
from collections import defaultdict

API_KEY = "phx_HBorvUARpdZwGBNBuCuTmjnBoRetfHTc4ELdvD5f9pjrECAc"
BASE = "https://app.posthog.com/api/projects/314999"

EVENTS = ["$pageview", "chapter_opened", "chapter_completed", "user_registered"]

all_events = {}
for ev in EVENTS:
    events = []
    url = f"{BASE}/events/?event={ev}&limit=50000&after=-12h"
    while url:
        req = urllib.request.Request(url, headers={"Authorization": f"Bearer {API_KEY}"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())
        results = data.get('results', [])
        events.extend(results)
        url = data.get('next')  # follow pagination URL
        if not url:
            break
    all_events[ev] = events

# distinct_id is the user identifier -- use sets for unique counts
visitors = set()
chapter_openers = set()
chapter_completers = set()
for e in all_events["$pageview"]:
    did = e.get("distinct_id")
    if did:
        visitors.add(did)
for e in all_events["chapter_opened"]:
    did = e.get("distinct_id")
    if did:
        chapter_openers.add(did)
for e in all_events["chapter_completed"]:
    did = e.get("distinct_id")
    if did:
        chapter_completers.add(did)
```

**Important:** REST API has no BigQuery access. To get cost data (CPA, cost per completion), you need MCP working with BigQuery joined queries. Without it, report conversion rates only.

## Critical Finding -- Ch.2 Is the Funnel Killer

**Discovered via 12h live analysis (April 2026):**

Real chapter-level completion rates from production data:
| Chapter | Opens | Completions | Rate |
|---------|-------|-------------|------|
| Ch.1 | 95 | 9 | **9%** |
| Ch.2 | 71 | 1 | **1%** 🔴 |
| Ch.3+ | 19+ | 2+ | **11-67%** |

**Ch.2 completion is 1% -- one percentage point.** This is by far the biggest drop in the entire funnel. Ch.1 loses 91%, but Ch.2 loses 99%. Once readers get past Ch.2, completion rates recover to 11-67%.

**Interpretation:** The novel endings at Ch.1 and Ch.2 are creating cliffhanger-style drop-offs. Either:
1. Ch.1 ending hooks readers into opening Ch.2, but Ch.2 ending doesn't hook into Ch.3
2. Ch.2 content itself has a pacing problem (too long, anti-climactic)

**Action:** When analyzing any campaign or novel, always break down completion rate by chapter number. A creative that drives lots of Ch.1 opens is only valuable if those readers reach Ch.3 (the true retention milestone).

- UTM params present on chapter_opened and chapter_completed ✅
- UTM params NOT present on user_registered ⚠️ (separate attribution problem)
- http_country_code available on chapter events for geo analysis
- time_spent_sec available on chapter_completed for quality signal
