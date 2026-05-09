---
name: cost-per-funnel-stage
category: novelpedia/analytics
version: 2.0.0
description: Cost per funnel stage (visitor, reader, registered). WARNING: BigQuery not connected. Requires A-ADS cost data from Marketing Analytics.
priority: critical
inputs:
  - campaign_name
  - date_range (7d, 14d, 30d)
outputs:
  - Cost per chapter_opened (visitor cost)
  - Cost per chapter_completed (reader cost)
  - Cost per user_registered (registration cost) - BROKEN
  - Estimated CPA
requires:
  - A-ADS Marketing Analytics (cost data)
  - PostHog Events API (conversion counts)
  - BigQuery not configured

---

# Cost Per Funnel Stage

## BigQuery Not Configured

`bigquery.spend_daily` not available. Cost data must come from A-ADS Marketing Analytics (external).

## Funnel Stages

```
Stage 0: Ad Click (A-ADS)
Stage 1: chapter_opened (PostHog) - visitor
Stage 2: chapter_completed (PostHog) - engaged reader
Stage 3: user_registered (PostHog) - BROKEN (no UTM)
```

## CPA Calculation (Without BigQuery)

```
CPA_per_chapter_opened = AADS_spend / chapter_opened_count
CPA_per_chapter_completed = AADS_spend / chapter_completed_count
CPA_per_registration = AADS_spend / user_registered_count  <- BROKEN
```

## Data Sources

| Metric | Source | Access |
|--------|--------|--------|
| Ad spend | A-ADS Marketing Analytics | External dashboard |
| Clicks | A-ADS Marketing Analytics | External dashboard |
| chapter_opened | PostHog Events API | /events/?event=chapter_opened |
| chapter_completed | PostHog Events API | /events/?event=chapter_completed |
| user_registered | PostHog Events API | /events/?event=user_registered |

## MCP Commands

```python
# Get conversion counts per campaign
GET /events/?event=chapter_opened&limit=5000&after=-7d
# Group by utm_campaign -> count distinct distinct_ids
```

## Known Campaigns

- reader-mage: high volume
- self-summoning-demon: high volume

## Alert Thresholds

| Metric | Kill Campaign | Warning |
|--------|--------------|---------|
| CPA (chapter_opened) | > $5 | > $2 |
| CPA (chapter_completed) | > $20 | > $10 |
| CPA (registration) | N/A (broken) | N/A |

## Degraded Mode

If A-ADS data unavailable: report only PostHog conversion counts with `cost_data: unavailable` flag.
