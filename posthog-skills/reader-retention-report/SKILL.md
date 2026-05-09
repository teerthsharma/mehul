---
name: reader-retention-report
category: novelpedia/analytics
version: 2.0.0
description: Reader retention analysis using chapter continuation as proxy. Uses Dashboard 1483189 patterns.
priority: high
inputs:
  - date_range (7d, 14d, 30d)
  - cohort_filter (new users, binge readers)
outputs:
  - Chapter continuation rate
  - Reader return rate
  - Streak data
  - ⚠️ Registration attribution broken
requires:
  - PostHog Events API
  - chapter_opened, chapter_completed, streak_milestone_reached
---

# Reader Retention Report

## ⚠️ Critical: No Native Retention Tab

PostHog Retention tab requires UI configuration. No cohorts exist yet (0 cohorts).
Use chapter continuation as the retention proxy.

---

## Retention Proxies

### 1. Chapter Continuation (Primary)
- `chapter_completed` followed by `chapter_opened` within 7 days
- Tracks whether a reader who completed chapter N opens chapter N+1

**Dashboard Pattern** (Campaign ROI Dashboard 1484131, Tile 4):
```
Events: chapter_opened, chapter_completed, chapter_opened (second open)
Math: median_count_per_actor
Date: -14d
Filter: utm_campaign is_set, utm_campaign is_not ["novelpedia-launch", "novelpedia"]
```

### 2. Streak Data
- `streak_milestone_reached` events with `streak_count`
- Shows reader loyalty milestones (streak_count = 5, 10, etc.)
- ⚠️ Only 3 streak events in 1000-event sample — very few readers reaching milestones

### 3. Registration Nudge
- `registration_nudge_shown` with `chapters_read` count
- Shows heavy readers (143+ chapters read in sample) being prompted to register
- **This means readers are reading 100+ chapters before registering**

---

## Chapter Continuation Funnel

```
Chapter N completed → Chapter N+1 opened within 7 days = retained
Chapter N completed → No chapter opened in 7 days = churned
```

### Continuation Rate Calculation
```
continuation_rate = readers who opened next chapter / readers who completed current chapter
```

### Alert Thresholds
| Metric | Healthy | Warning | Critical |
|--------|---------|---------|---------|
| Continuation rate (ch.N → ch.N+1) | > 40% | 20-40% | < 20% |
| Avg chapters completed per reader | > 3 | 1-3 | 1 |
| Streak milestone (5+ chapters) | > 20% of readers | 5-20% | < 5% |

---

## Engagement Events

From Dashboard 1484131 Tile 5:
- `novel_followed` — reader followed a novel
- `comment_created` — reader commented
- `share_clicked` — reader shared

These indicate deep engagement beyond passive reading.

---

## ⚠️ Registration Attribution Broken

`user_registered` has no UTM params. Cannot attribute which campaign brought a registering user.
However, `chapter_opened` DOES have UTM — so you CAN attribute which campaign brought the reader to the first chapter.

---

## MCP Commands

```python
# Get all chapter events for retention analysis
/events/?event=chapter_opened&limit=5000
/events/?event=chapter_completed&limit=5000
/events/?event=streak_milestone_reached&limit=100
```

---

## Streak Data Insight

Sample shows: 1 reader with streak_count=5 triggered `streak_milestone_reached`
This means only 1 reader has hit a 5-day reading streak.
Most readers are not yet in the retention loop.

---

## Reader WAU (chapter_opened on novelpedia.net)

Since chapter_opened = north-star = active user:
```
WAU = distinct(distinct_id) WHERE event = chapter_opened AND timestamp > now() - 7d
```
