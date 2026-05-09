---
name: novelpedia-cost-attribution
category: novelpedia
version: 1.0.0
description: Cross-referencing A-ADS spend data with PostHog events for cost-per-attribution analysis. Discovered that HogQL queries in PostHog dashboards are session-only (not API-executable) and require workarounds.
priority: critical
inputs:
  - campaign names
  - date range
  - desired metrics (CPA, CTR, CPC, cost per completer)
outputs:
  - Cost per unique visitor
  - Cost per chapter opener / reader
  - Cost per chapter completed
  - CTR reconciliation (A-ADS clicks vs PostHog visitors)
requires:
  - PostHog API key
  - Access to PostHog Campaign ROI dashboard (id: 1484131) OR BigQuery service account

---

# Novelpedia Cost Attribution Workflow

## Problem

Comparing ad creative variants (e.g., `static-v3` vs `trial-static-v1` for reader-mage) by **cost per result** — not just completion rate. Engagement quality means nothing without cost efficiency.

## Architecture

```
A-ADS CSV exports
       ↓
  BigQuery: ads.spend_daily
       ↓
PostHog HogQL (BigQuery warehouse source)
       ↓
  PostHog Dashboard Tiles (DataTableNode with HogQLQuery)
       ↓
  Joined with PostHog events table
       ↓
  Cost-per-stage metrics
```

## Critical Finding: HogQL Is Session-Only

**PostHog HogQL queries CANNOT be executed via API key from external tools.**

- Endpoint: `POST /api/projects/{id}/query/` → requires session auth, returns `permission_denied` for API key
- Workaround 1: Read the query definitions from dashboard tile JSON (they're stored in the tile config)
- Workaround 2: Use PostHog MCP tools (if configured in session)
- Workaround 3: Pull raw events from events API and compute locally
- Workaround 4: User manually reads from PostHog dashboard tiles

## Key Dashboard Tiles (Campaign ROI Dashboard id=1484131)

These tiles contain pre-built HogQL queries joining BigQuery spend with PostHog events:

| Tile ID | Name | Purpose |
|---------|------|---------|
| 7425818 | Daily ad spend by campaign & creative | Spend, CPC per variant |
| 7425816 | Clicks vs. visits by campaign & creative | A-ADS click vs PostHog visitor reconciliation |
| 7425815 | Reading depth funnel by campaign & creative | Visitor → ch1 → ch3 → ch8 breakdown |
| 7425812 | Cost per funnel stage by campaign & creative | **CPA for visitor, reader, completer, ch3** |
| 7354371 | Traffic by campaign & creative | Pageview volume per variant |

### Tile Query Format

Tiles of kind `DataTableNode` contain HogQL queries stored in the tile config. To find queries:

```python
GET /api/projects/314999/dashboards/1484131/
# → tiles[].insight.query.source.query  (HogQLQuery kind)
```

**Note**: Campaign name mapping — `self-summoning-gif-v2` in BigQuery maps to `self-summoning-demon` in PostHog events:
```sql
CASE WHEN s.utm_campaign = 'self-summoning-gif-v2' THEN 'self-summoning-demon'
     ELSE replaceRegexpAll(s.utm_campaign, '__.*$', '')
END = ph.utm_campaign
```

## Events API (Fallback when HogQL unavailable)

Use when HogQL returns `permission_denied` or PostHog MCP not loaded.

```python
# Fetch events from PostHog Events API
GET /api/projects/314999/events/?event=chapter_opened&limit=5000&after=-7d
GET /api/projects/314999/events/?event=chapter_completed&limit=5000&after=-7d
GET /api/projects/314999/events/?event=$pageview&limit=5000&after=-7d
```

API key header: `Authorization: Bearer phx_HBorvUARpdZwGBNBuCuTmjnBoRetfHTc4ELdvD5f9pjrECAc`
Base: `https://app.posthog.com/api/projects/314999`

### Local Aggregation Pattern

```python
from collections import defaultdict

data = defaultdict(lambda: {"visitors": set(), "opened": set(), "completed": set()})
for e in events:
    p = e.get("properties", {})
    campaign = p.get("utm_campaign") or "unknown"
    variant = p.get("utm_content") or "unknown"
    did = e.get("distinct_id")
    # Filter out internal campaigns
    if campaign not in ("unknown", "novelpedia-launch", "novelpedia") and did:
        data[(campaign, variant)]["opened"].add(did)
```

**CRITICAL**: Use `distinct_id` consistently for ALL event types. Do NOT mix `distinct_id` and `person_id` — they differ and mixing produces inflated funnel counts (>100%).

## Decision Thresholds

| Metric | Kill | Hold | Scale |
|--------|------|------|-------|
| Completion rate | < 10% | 10–30% | > 30% |
| Cost per completer | > 2x target | 1–2x target | < target |
| Cost per visitor | > CPC benchmark | marginal | < CPC benchmark |

## Setup Requirements

1. **BigQuery access** (live cost data):
   - Service account JSON needed
   - Dataset: `ads`, Table: `spend_daily`
   - Pipeline: A-ADS CSV → GCS → Cloud Run importer → BigQuery
   - Contact: KarmicDaoist for pipeline access

2. **PostHog MCP** (in-session HogQL):
   - Add to `~/.hermes/config.yaml` under `mcp_servers`
   - Use tool whitelist to prevent 247-tool flood
   - Tools: `ph_query_insights`, `ph_get_funnel`, `ph_get_person`, `ph_get_feature_flag`

3. **A-ADS manual export** (fastest one-off):
   - Export per-campaign CSV from A-ADS dashboard
   - Campaign-level only (no variant breakdown)
