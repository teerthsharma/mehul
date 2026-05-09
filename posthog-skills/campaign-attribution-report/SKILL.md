---
name: campaign-attribution-report
category: novelpedia/analytics
version: 2.0.0
description: Campaign attribution using TrendsQuery with UTM breakdown. Funnel IDs return 404 — use event series.
priority: critical
inputs:
  - date_range (7d, 14d, 30d)
  - campaign_filter
  - creative_filter
outputs:
  - Campaign performance table (UTM × event)
  - Registration attribution (⚠️ broken — user_registered 0% UTM at both levels)
  - Recommendation
requires:
  - PostHog Events API
  - PostHog Dashboard Tile 6 (1484131)
---

# Campaign Attribution Report

## ⚠️ Critical: Registration Attribution is Broken

`user_registered` event has NO UTM params. Cannot attribute registrations to campaigns.
Only chapter_opened/completed and novel_detail_viewed are UTM-attributable.

---

## Actual Dashboard Queries (from Campaign ROI dashboard 1484131)

### Tile 6: Full Acquisition Funnel by Campaign
```
Events: novel_detail_viewed, chapter_opened, chapter_completed
Math: total
Filters: utm_campaign is_set, utm_campaign is_not ["novelpedia-launch", "novelpedia"]
Breakdown: utm_campaign
Date: -14d
```

### Tile 8: Acquisition Funnel by Campaign × Creative
```
Events: $pageview, novel_detail_viewed, chapter_opened, chapter_completed
Math: total
Filters: utm_campaign is_set, utm_campaign is_not ["novelpedia-launch", "novelpedia"], utm_content is_set
Breakdown: utm_campaign, utm_content
Date: -14d
```

### Tile 9: Registrations by Campaign (Person Attribution)
```
Event: user_registered
Math: dau
Filters: $initial_utm_campaign is_set, $initial_utm_campaign is_not ["novelpedia-launch", "novelpedia"]
Date: -14d
```
**⚠️ This only works if $initial_utm_campaign is set on the person profile via $identify.
Currently unverified whether this is working.**

---

## Engagement Events (Tile 5)
```
novel_followed (dau)
comment_created (dau)
share_clicked (dau)
Filters: utm_source is_not ["aads-ranobes", "aads-freewebnovel"], utm_campaign is_set, utm_campaign is_not ["novelpedia-launch", "novelpedia"]
Date: -14d
```

---

## Attribution Approach

Since user_registered has no UTM, attribute registrations via `$identify` if `$initial_utm_*` is set on person profiles. Otherwise, registrations cannot be attributed to campaigns.

**What CAN be attributed to campaigns:**
- novel_detail_viewed (discovery)
- chapter_opened (activation)
- chapter_completed (engagement)
- novel_followed (loyalty)
- comment_created (engagement)
- share_clicked (viral)

---

## Active Campaigns

- `reader-mage` — high volume
- `self-summoning-demon` — high volume  
- `inertia-beneath-starlit-veil` — low volume
- `gu-demon-king` — very low volume

---

## A-ADS Source

All campaigns from A-ADS via `utm_source: aads-novelfire`, `utm_medium: cpc`

---

## MCP Commands

Use Events API with UTM properties:

```
/events/?event=chapter_opened&properties=utm_campaign:{campaign_name}&limit=1000
```

For campaign breakdown, query all chapter_opened events with UTM and aggregate in Python:

```python
# Get all chapter_opened events with UTM
events = get("/api/projects/314999/events/?event=chapter_opened&limit=1000")
# Group by properties.utm_campaign
# Count distinct distinct_ids per campaign
```

---

## ROAS Calculation (Degraded)

Without A-ADS cost data in PostHog, ROAS cannot be calculated directly.
Workaround:
1. Use A-ADS Marketing Analytics for cost per campaign
2. Use PostHog chapter_opened as the "conversion" event
3. CPA = A-ADS_cost / chapter_opened_count_per_campaign
