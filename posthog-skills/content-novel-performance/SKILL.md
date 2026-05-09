---
name: content-novel-performance
category: novelpedia/analytics
version: 2.0.0
description: Per-novel ranking by chapter opens, completion rate, reading depth. Uses chapter_opened/chapter_completed with novel_id grouping.
priority: high
inputs:
  - date_range (7d, 30d)
  - min_sample_size (default: 10 events)
outputs:
  - Novel rankings by engagement
  - Completion rate per novel
  - Aha! moment detection (ch.8+)
requires:
  - PostHog Events API
  - chapter_opened, chapter_completed
---

# Content / Novel Performance

## Event Properties Available

### chapter_opened has:
- `novel_id` — unique novel identifier
- `novel_title` — display name
- `chapter_number` — which chapter
- `word_count` — chapter length
- `time_spent_sec` — ⚠️ only on chapter_completed, not chapter_opened

### chapter_completed has:
- `novel_id`, `novel_title`, `chapter_number`, `word_count`
- `time_spent_sec` — actual reading time
- `http_country_code` — reader geography

---

## Key Metrics

### Completion Rate
```
completion_rate(novel) = chapter_completed / chapter_opened
```

### Reading Depth
```
avg_chapters_per_reader(novel) = count(chapter_completed) / count(distinct distinct_id)
```

### Aha! Moment Detection
```
chapter_completed WHERE chapter_number >= 8
```
Dashboard 1484131 Tile 3 uses `median_count_per_actor` for chapter_completed — this is the Aha! proxy.

### Velocity Signal
```
avg_time_spent_sec(novel) = avg(time_spent_sec) on chapter_completed
```
Low time (< 30s) may indicate bot/skimmer. High time (> 300s) may indicate very engaged reader.

---

## MCP Commands

```python
# Get chapter events for a specific novel
/events/?event=chapter_opened&properties=novel_id:{id}&limit=500
/events/?event=chapter_completed&properties=novel_id:{id}&limit=500

# Get all novels with chapter activity (last 30d)
/events/?event=chapter_opened&limit=5000&after=-30d
```

---

## Known Novels (from sample data)

- `7b4f72b3-0ff3-4856-b916-46ffb443bc7e` — "Self-Summon [Demon Summoning/Evolution litRPG]"
- `87335bb6-9ed1-48ec-86fe-d0071cf1b043` — "Reader Mage"

---

## Alert Thresholds

| Metric | Critical | Warning |
|--------|----------|---------|
| Completion rate | < 10% | < 20% |
| time_spent_sec | < 30s (likely bot) | < 60s |
| Chapters per reader | < 1.5 | < 2 |

---

## Novel Card Clicked (Discovery Signal)

`novel_card_clicked` has:
- `source` — where the click happened (unknown, browse, etc.)
- `source_surface` — grid, list, etc.
- `rank` — position in list
- `novel_id`, `novel_title`

Use this to understand which novels get clicked vs. which get read.

---

## Engagement Signals Beyond Reading

From Dashboard Tile 5 (1484131):
- `novel_followed` — reader saved novel
- `share_clicked` — reader shared
- `comment_created` — reader engaged

A novel with high chapter_opened but low novel_followed may have a hook problem.
