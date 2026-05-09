---
name: author-platform-health
category: novelpedia/analytics
version: 2.0.0
description: Author-side analytics for author.novelpedia.net. Uses Dashboard 1483191 query patterns.
priority: medium
inputs:
  - date_range (7d, 14d, 30d)
outputs:
  - Novel publish rate
  - Author engagement (comment_created)
  - Author WAU
requires:
  - PostHog Events API (filtered by $host = author.novelpedia.net)
  - ✅ chapter_published fires (205 events/30d). ✅ comment_created fires (60 events/30d) but has 0% UTM.
---

# Author Platform Health

## ⚠️ Critical: Author Events Not Firing

`novel_published` and `comment_created` is defined in Dashboard 1483191 and IS in the raw event stream (60 events/30d).
Before running this skill, verify these events are actually being instrumented on author.novelpedia.net.

---

## Verified Author-Side Events

### From raw events API ($host = author.novelpedia.net):
- `$pageview` — page views on author dashboard
- `$autocapture` — author interactions
- `$web_vitals` — performance
- `$pageleave` — exits
- `$exception` — errors
- `$rageclick` — frustration
- `$identify` — person identification

### Dashboard Events (may not be firing):
- `novel_published` — should fire when author publishes
- `comment_created` — should fire when reader comments on author's novel

---

## Dashboard Query Pattern (1483191)

### Tile 1: novel_published + comment_created
```
Event: chapter_published (total), comment_created (total)
Date: -30d
```

### Tiles 2-7: Author $pageview funnel
```
First page view: $pageview (total), $host = author.novelpedia.net
Second page view: $pageview (total), $host = author.novelpedia.net
Third page view: $pageview (total), $host = author.novelpedia.net
```

---

## What to Measure

1. **Author WAU**: distinct users with $pageview on author.novelpedia.net in 7d
2. **Novel publish rate**: count of novel_published events per week
3. **Comment activity**: count of comment_created events per week (⚠️ 0% UTM — cannot attribute to campaigns)
4. **Author onboarding funnel**: $pageview count escalating across first/second/third visits

---

## Verification Steps

```python
# Check if novel_published is firing
events = get("/api/projects/314999/events/?event=novel_published&limit=10")
# If empty: instrument novel_published event on author.novelpedia.net

# Check author.novelpedia.net pageviews
events = get("/api/projects/314999/events/?limit=200&properties=%7B%22%24host%22%3A%22author.novelpedia.net%22%7D")
# Should have $pageview, $autocapture, etc.
```

---

## Fallback Metrics (if novel_published not firing)

Use $pageview on author.novelpedia.net as proxy for author activity:
- Author WAU = distinct users with $pageview on author.novelpedia.net
- Author DAU = distinct users with $pageview on author.novelpedia.net today
