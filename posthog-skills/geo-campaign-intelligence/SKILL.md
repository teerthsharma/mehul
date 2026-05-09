---
name: geo-campaign-intelligence
category: novelpedia/analytics
version: 2.0.0
description: Geographic breakdown of campaign performance. http_country_code is available on chapter events.
priority: medium
inputs:
  - date_range (7d, 14d, 30d)
  - campaign_filter
outputs:
  - Visitors by country
  - Engagement by country
  - Bot risk detection
requires:
  - PostHog Events API

---

# Geo x Campaign Intelligence

## Data Source

`http_country_code` property is available on:
- $pageview
- $autocapture
- $web_vitals
- chapter_opened (verified)
- chapter_completed (verified)

chapter_opened and chapter_completed DO carry http_country_code (verified from sample data: GH, US, GB seen)

## Join Strategy

chapter_opened does NOT carry geo on the same event as UTM campaign.
To get geo x campaign attribution:
```
1. chapter_opened events have BOTH UTM and http_country_code (verified)
2. Use chapter_opened directly for geo x campaign analysis
```

## MCP Commands

```python
# Get chapter events with geo
GET /events/?event=chapter_opened&limit=5000&after=-7d

# Python: group by http_country_code
from collections import defaultdict
geo_counts = defaultdict(lambda: {'chapter_opened': 0, 'chapter_completed': 0})
for e in events:
    country = e['properties'].get('http_country_code', 'UNKNOWN')
    geo_counts[country][e['event']] += 1
```

## Known Countries (from sample)

- US - United States (high volume)
- GH - Ghana (seen on chapter_completed - real reader)
- GB - United Kingdom

## Bot Risk Detection

| Signal | Bot Risk |
|--------|----------|
| High country with 0 chapter_completed | High |
| < 5% chapter_completion rate | Medium |
| < 30s time_spent_sec | High |
| Very high pageviews, near-zero chapter_opened | High |

## Quality Tiers

| Country Tier | Quality Signal |
|-------------|---------------|
| Tier 1: US, GB, CA, AU | High time_spent_sec, high completion |
| Tier 2: DE, FR, IN, BR | Medium engagement |
| Tier 3: GH, NG, etc. | Verify with time_spent_sec |

## Engagement by Geo

```
completion_rate(country) = chapter_completed / chapter_opened per country
```
