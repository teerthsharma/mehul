---
name: metric-anomaly-detection
category: novelpedia/analytics
version: 2.0.0
description: Detect flatlines and drops across key product events. Uses 7-day rolling baseline.
priority: high
inputs:
  - date_range (7d default)
  - alert_threshold (default: 2-sigma drop)
outputs:
  - Daily event volumes
  - Baseline comparison
  - Drop alerts
requires:
  - PostHog Events API

---

# Metric Anomaly Detection

## Monitored Events

| Event | Critical Floor | Warning Floor | Meaning |
|-------|---------------|---------------|---------|
| chapter_opened | < 5/day | < 20/day | Product is dead |
| chapter_completed | < 2/day | < 5/day | Engagement broken |
| user_registered | < 1/day | < 3/day | Acquisition broken |
| novel_detail_viewed | < 10/day | < 25/day | Discovery broken |

## Detection Logic

```
baseline_avg = avg(daily_counts for past 7 days)
baseline_std = std(daily_counts for past 7 days)
today_count = count of events today
z_score = (today_count - baseline_avg) / baseline_std

if today_count < baseline_avg - 2 * baseline_std: ALERT
```

## MCP Commands

```python
# Get daily event counts
GET /events/?event=chapter_opened&limit=5000&after=-7d

# Python aggregation:
from collections import defaultdict
daily = defaultdict(int)
for e in events:
    day = e['timestamp'][:10]  # YYYY-MM-DD
    daily[day] += 1
```

## Alert Patterns

| Pattern | Cause | Action |
|---------|-------|--------|
| chapter_completed drops, chapter_opened stable | Chapter quality issue | Check chapter load times |
| user_registered drops, chapter_opened stable | Registration funnel broken | Check registration page |
| chapter_opened drops, registrations stable | Traffic source problem | Check ad spend / UTM |
| All metrics flatline | Tracking broken | Check PostHog SDK |

## Novelpedia is 3-4 Days Old

Low baseline volume means anomaly detection has high false positive rate.
Use absolute floors, not just z-scores, for young products.

## Discord Alert Format

```
METRIC ALERT: chapter_opened

Today: 3 events
7-day avg: 12 events
Drop: -75% CRITICAL

Last 7 days: [15, 8, 14, 11, 9, 12, 3]
```

## Escalation

If chapter_opened < 5 for 3 consecutive days: ping <@&ROLE_ID>
If chapter_completed = 0 for 1 day: ping <@&ROLE_ID>
