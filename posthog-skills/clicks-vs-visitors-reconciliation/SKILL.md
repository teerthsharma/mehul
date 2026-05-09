---
name: clicks-vs-visitors-reconciliation
category: novelpedia/analytics
version: 2.0.0
description: Reconcile A-ADS reported ad clicks vs PostHog-tracked real visitors (chapter_opened). Gap analysis tells you traffic quality.
priority: critical
inputs:
  - campaign_name (utm_campaign)
  - date_range (7d, 14d, 30d)
outputs:
  - A-ADS clicks (from Marketing Analytics)
  - PostHog chapter_opened count per UTM campaign
  - Click-to-visitor rate
  - Gap analysis
requires:
  - PostHog Events API
  - A-ADS Marketing Analytics (external)

---

# Clicks vs Visitors Reconciliation

## Two Data Sources

### A-ADS (Ad Platform)
- Reports: clicks, impressions, spend per campaign/creative
- Access: Marketing Analytics dashboard (external to PostHog)
- Metric: clicks

### PostHog (Web Analytics)
- Reports: real users who triggered chapter_opened
- Access: Events API
- Metric: chapter_opened count grouped by utm_campaign

## Reconciliation Formula

```
click_to_visitor_rate = chapter_opened_count / aads_clicks
```

## Quality Benchmarks

| Rate | Signal |
|------|--------|
| > 20% | Excellent - landing page converts well |
| 10-20% | Average |
| 5-10% | Below average - check landing page |
| < 5% | Likely bot or broken UTM |

## Known Issue: A-ADS Partner ID in Events

From raw events:
- `partner` property on chapter_opened = 209646_2385223, 209566_2404108, etc.
- These are A-ADS partner IDs, not UTM campaigns
- UTM campaign is stored separately as `utm_campaign`
- Both must be joined for full reconciliation

## MCP Commands

```python
# Get chapter_opened events grouped by UTM campaign
GET /events/?event=chapter_opened&limit=5000&after=-7d

# Count distinct users per campaign
# Python aggregation required:
from collections import defaultdict
campaign_users = defaultdict(set)
for e in events:
    campaign_users[e['properties']['utm_campaign']].add(e['distinct_id'])
```

## A-ADS Metrics to Pull

- clicks - ad clicks per campaign per day
- impressions - ad views per campaign per day
- spend - cost per campaign per day
- ctr - click-through rate (clicks / impressions)

## Gap Analysis

```
gap = aads_clicks - chapter_opened_count
gap_rate = gap / aads_clicks

High gap = users click ads but do not open chapters
  -> Landing page issue (chapter list does not load?)
  -> Bot clicks inflating A-ADS stats
  -> UTM params not persisting to chapter_opened
```

## Campaign Data (from PostHog events)

- reader-mage: high volume, utm_source = aads-novelfire
- self-summoning-demon: high volume, utm_source = aads-novelfire
